"""
Advanced Agentic Chat Service
───────────────────────────────────────────────────────────────────
Multi-step mental-health support agent with:
  • Semantic intent classification (zero-shot via LLM)
  • Dynamic tool orchestration with dependency resolution
  • Sliding-window + summary-compressed conversation memory
  • Crisis escalation ladder with configurable thresholds
  • Structured chain-of-thought reasoning before response
  • Retry / fallback across Gemini model variants
  • Async-first with sync shim for legacy callers
  • Structured observability (spans + metrics)
  • Input / output validation via dataclasses
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum, auto
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse

from config import Config
from gemini_service import gemini_service

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
logger = logging.getLogger(__name__)
_TRACE = 5  # custom TRACE level below DEBUG
logging.addLevelName(_TRACE, "TRACE")


def _trace(msg: str, *args: Any) -> None:  # noqa: D401
    logger.log(_TRACE, msg, *args)


def _extract_gemini_text(resp: Any) -> str:
    """
    Read assistant text from GenerateContentResponse without raising.
    Accessing .text can throw when the response is blocked or malformed.
    """
    if resp is None:
        return ""
    try:
        t = (resp.text or "").strip()
        if t:
            return t
    except Exception as exc:
        logger.debug("Gemini resp.text unavailable: %s", exc)
    try:
        cands = getattr(resp, "candidates", None) or []
        if not cands:
            return ""
        content = getattr(cands[0], "content", None)
        parts = getattr(content, "parts", None) if content else None
        if not parts:
            return ""
        chunks: List[str] = []
        for part in parts:
            tx = getattr(part, "text", None)
            if tx:
                chunks.append(tx)
        return " ".join(chunks).strip()
    except Exception as exc:
        logger.debug("Gemini candidate parse failed: %s", exc)
    return ""


def _is_degraded_agent_text(text: Optional[str]) -> bool:
    """True if the model returned an error/boilerplate reply instead of real support."""
    if not text or not str(text).strip():
        return True
    low = text.lower()
    return any(
        s in low
        for s in (
            "something went wrong on my end",
            "technical difficulty right now",
        )
    )


# ─────────────────────────────────────────────
# Enums & Constants
# ─────────────────────────────────────────────
class Intent(str, Enum):
    ANXIETY      = "anxiety"
    DEPRESSION   = "depression"
    STRESS       = "stress"
    GRIEF        = "grief"
    RELATIONSHIP = "relationship"
    SELF_ESTEEM  = "self_esteem"
    SLEEP        = "sleep"
    CRISIS       = "crisis"
    GENERAL      = "general"


class CrisisLevel(int, Enum):
    NONE     = 0
    LOW      = 1   # passive ideation / hopelessness
    MODERATE = 2   # active ideation, no plan
    HIGH     = 3   # active ideation + plan or access to means
    IMMINENT = 4   # immediate danger


class ToolID(str, Enum):
    BREATHING       = "breathing_exercise"
    GROUNDING       = "grounding_5_4_3_2_1"
    PMR             = "progressive_muscle_relaxation"
    JOURNAL_PROMPT  = "journal_prompt"
    COGNITIVE_REFRAME = "cognitive_reframe"
    SAFETY_PLAN     = "safety_plan"
    CRISIS_HOTLINES = "crisis_hotlines"
    SLEEP_HYGIENE   = "sleep_hygiene"
    GRIEF_RITUAL    = "grief_ritual"


_MODEL_FALLBACK_CHAIN: Tuple[str, ...] = (
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-pro-latest",
    "gemini-pro",
)

_MAX_HISTORY_WINDOW      = 12   # turns kept verbatim
_SUMMARY_TRIGGER         = 20   # turns before compressing older ones
_INTENT_CACHE_SECONDS    = 120  # TTL for cached intent classifications
_GENERATION_TIMEOUT      = 18.0 # seconds
_MAX_RETRIES             = 3
_RETRY_BACKOFF_BASE      = 0.6  # seconds


# ─────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────
@dataclass(frozen=True)
class Turn:
    role: str          # "user" | "assistant"
    content: str
    ts: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    intent: Optional[str] = None
    crisis_level: int = 0


@dataclass
class ToolResult:
    tool_id: ToolID
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"tool": self.tool_id.value, "content": self.content, **self.metadata}


@dataclass
class AgentSpan:
    """Lightweight tracing span for observability."""
    span_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    started_at: float = field(default_factory=time.monotonic)
    ended_at: Optional[float] = None
    tags: Dict[str, Any] = field(default_factory=dict)

    def finish(self, **extra_tags: Any) -> "AgentSpan":
        self.ended_at = time.monotonic()
        self.tags.update(extra_tags)
        return self

    @property
    def duration_ms(self) -> Optional[float]:
        if self.ended_at is None:
            return None
        return round((self.ended_at - self.started_at) * 1000, 2)


@dataclass
class AgentResponse:
    session_id: str
    intent: str
    crisis_level: int
    response: str
    tools_used: List[str]
    reasoning_summary: str
    confidence: float
    spans: List[Dict[str, Any]]
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    model_used: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ─────────────────────────────────────────────
# Tool Registry
# ─────────────────────────────────────────────
class ToolRegistry:
    """
    Declarative registry mapping intents + crisis levels to tools.
    Each tool is a pure function returning a ToolResult.
    """

    @staticmethod
    def breathing() -> ToolResult:
        return ToolResult(
            tool_id=ToolID.BREATHING,
            content=(
                "Box Breathing — 4 rounds:\n"
                "  1. Inhale slowly for 4 counts.\n"
                "  2. Hold for 4 counts.\n"
                "  3. Exhale for 4 counts.\n"
                "  4. Hold empty for 4 counts.\n"
                "Repeat. Let each breath anchor you to this moment."
            ),
        )

    @staticmethod
    def grounding() -> ToolResult:
        return ToolResult(
            tool_id=ToolID.GROUNDING,
            content=(
                "5-4-3-2-1 Grounding:\n"
                "  • 5 things you can SEE right now\n"
                "  • 4 things you can physically FEEL (chair, temperature, fabric)\n"
                "  • 3 things you can HEAR\n"
                "  • 2 things you can SMELL (or imagine you like)\n"
                "  • 1 thing you can TASTE\n"
                "Take your time with each sense."
            ),
        )

    @staticmethod
    def pmr() -> ToolResult:
        return ToolResult(
            tool_id=ToolID.PMR,
            content=(
                "Progressive Muscle Relaxation (5 min):\n"
                "  Starting from your feet — tense each muscle group for 5 s, "
                "then release for 30 s. Move up: calves → thighs → abdomen → hands → "
                "shoulders → face. Notice the contrast between tension and release."
            ),
        )

    @staticmethod
    def journal_prompt(context: str = "") -> ToolResult:
        prompts = [
            "What happened today that stirred an emotion in me?",
            "What am I carrying that isn't mine to carry?",
            "If my feelings had a colour and shape right now, what would they look like?",
            "What does the wisest version of me want me to know today?",
        ]
        # Simple deterministic selection based on context length
        chosen = prompts[len(context) % len(prompts)]
        return ToolResult(
            tool_id=ToolID.JOURNAL_PROMPT,
            content=(
                f"Journal Prompt:\n  \"{chosen}\"\n\n"
                "Write for at least 5 minutes without stopping to edit. "
                "Let honesty lead."
            ),
            metadata={"prompt_text": chosen},
        )

    @staticmethod
    def cognitive_reframe() -> ToolResult:
        return ToolResult(
            tool_id=ToolID.COGNITIVE_REFRAME,
            content=(
                "Cognitive Reframe — 3 questions:\n"
                "  1. What thought is making this harder?\n"
                "  2. What evidence supports it? What contradicts it?\n"
                "  3. What would I say to a friend who had this thought?\n"
                "Write down your answers; distance helps."
            ),
        )

    @staticmethod
    def sleep_hygiene() -> ToolResult:
        return ToolResult(
            tool_id=ToolID.SLEEP_HYGIENE,
            content=(
                "Sleep Hygiene Checklist:\n"
                "  • Same bed/wake time every day (±30 min)\n"
                "  • No screens 60 min before bed\n"
                "  • Keep room cool (65–68 °F / 18–20 °C)\n"
                "  • Avoid caffeine after 2 PM\n"
                "  • 4-7-8 breathing to fall asleep: inhale 4 s, hold 7 s, exhale 8 s"
            ),
        )

    @staticmethod
    def grief_ritual() -> ToolResult:
        return ToolResult(
            tool_id=ToolID.GRIEF_RITUAL,
            content=(
                "A Small Grief Ritual:\n"
                "  Find a quiet moment. Light a candle or hold something meaningful.\n"
                "  Speak (or write) three sentences:\n"
                "    • \"I am grieving …\"\n"
                "    • \"What I miss most is …\"\n"
                "    • \"I honour you / it by …\"\n"
                "Grief asks to be witnessed. You have witnessed it today."
            ),
        )

    @staticmethod
    def safety_plan() -> ToolResult:
        return ToolResult(
            tool_id=ToolID.SAFETY_PLAN,
            content=(
                "Safety Plan — write these down right now:\n"
                "  1. Warning signs I'm in crisis: ___\n"
                "  2. Internal coping I can do alone: ___\n"
                "  3. People / places that provide distraction: ___\n"
                "  4. People I can ask for help: ___\n"
                "  5. Professionals / crisis lines: ___\n"
                "  6. Making my environment safer: ___\n"
                "Keep this somewhere you can find quickly."
            ),
        )

    @staticmethod
    def crisis_hotlines() -> ToolResult:
        return ToolResult(
            tool_id=ToolID.CRISIS_HOTLINES,
            content=(
                "Crisis Resources — reach out right now:\n"
                "  🇺🇸 988 Suicide & Crisis Lifeline: call or text 988\n"
                "  🌍 International: https://findahelpline.com\n"
                "  💬 Crisis Text Line: text HOME to 741741 (US)\n"
                "  🇬🇧 Samaritans: 116 123\n"
                "  🇮🇳 iCall: 9152987821\n"
                "You are not alone. A real person is waiting to listen."
            ),
        )


# ─────────────────────────────────────────────
# Intent → Tool Mapping
# ─────────────────────────────────────────────
_INTENT_TOOL_MAP: Dict[Intent, List[Callable[[], ToolResult]]] = {
    Intent.ANXIETY:      [ToolRegistry.breathing, ToolRegistry.grounding],
    Intent.DEPRESSION:   [ToolRegistry.journal_prompt, ToolRegistry.cognitive_reframe],
    Intent.STRESS:       [ToolRegistry.breathing, ToolRegistry.pmr],
    Intent.GRIEF:        [ToolRegistry.grief_ritual, ToolRegistry.journal_prompt],
    Intent.RELATIONSHIP: [ToolRegistry.journal_prompt, ToolRegistry.cognitive_reframe],
    Intent.SELF_ESTEEM:  [ToolRegistry.cognitive_reframe, ToolRegistry.journal_prompt],
    Intent.SLEEP:        [ToolRegistry.sleep_hygiene, ToolRegistry.breathing],
    Intent.CRISIS:       [ToolRegistry.crisis_hotlines, ToolRegistry.safety_plan,
                          ToolRegistry.breathing],
    Intent.GENERAL:      [ToolRegistry.breathing],
}

_CRISIS_LEVEL_KEYWORDS: Dict[CrisisLevel, List[str]] = {
    CrisisLevel.IMMINENT: [
        "going to kill myself", "about to end it", "have a gun", "have pills ready",
        "saying goodbye", "final note",
    ],
    CrisisLevel.HIGH: [
        "suicide", "kill myself", "end my life", "want to die", "ending it all",
        "plan to", "i will hurt",
    ],
    CrisisLevel.MODERATE: [
        "self harm", "self-harm", "hurt myself", "can't go on", "no point",
        "worthless", "better off dead",
    ],
    CrisisLevel.LOW: [
        "hopeless", "trapped", "don't see a way out", "exhausted of living",
        "nobody cares", "disappear",
    ],
}


def assess_crisis_text(text: str) -> int:
    """Return crisis level 0 (none) through 4 (imminent) for LangGraph / guardrails."""
    lower = (text or "").lower()
    for level in sorted(CrisisLevel, reverse=True):
        if level == CrisisLevel.NONE:
            continue
        if any(kw in lower for kw in _CRISIS_LEVEL_KEYWORDS.get(level, [])):
            return int(level)
    return 0


# ─────────────────────────────────────────────
# Utility Decorators
# ─────────────────────────────────────────────
def _with_span(name: str):
    """Attach an AgentSpan to the return list automatically."""
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        async def wrapper(self: "AgenticChatService", *args, **kwargs):
            span = AgentSpan(name=name)
            result = await fn(self, *args, **kwargs)
            span.finish()
            self._spans.append(span)
            return result
        return wrapper
    return decorator


# ─────────────────────────────────────────────
# Memory Manager
# ─────────────────────────────────────────────
class ConversationMemory:
    """
    Sliding-window memory with LLM-powered compression for long conversations.

    Keeps the last `window_size` turns verbatim.  When total turns exceed
    `summary_trigger`, older turns are summarised by a lightweight LLM call
    and stored as a single "summary" pseudo-turn.
    """

    def __init__(
        self,
        window_size: int = _MAX_HISTORY_WINDOW,
        summary_trigger: int = _SUMMARY_TRIGGER,
    ) -> None:
        self._turns: List[Turn] = []
        self._summary: str = ""
        self._window_size = window_size
        self._summary_trigger = summary_trigger

    def add(self, turn: Turn) -> None:
        self._turns.append(turn)

    def recent_turns(self) -> List[Turn]:
        return self._turns[-self._window_size:]

    def needs_compression(self) -> bool:
        return len(self._turns) > self._summary_trigger

    def compress(self, summary: str) -> None:
        """Replace old turns with a summary, keeping recent window intact."""
        keep = self._turns[-self._window_size:]
        self._turns = keep
        self._summary = summary

    def render(self) -> str:
        lines: List[str] = []
        if self._summary:
            lines.append(f"[Earlier session summary]\n{self._summary}\n")
        for turn in self.recent_turns():
            prefix = "User" if turn.role == "user" else "SeraNova"
            lines.append(f"{prefix}: {turn.content}")
        return "\n".join(lines) if lines else "This is the start of the session."


# ─────────────────────────────────────────────
# Main Service
# ─────────────────────────────────────────────
class AgenticChatService:
    """
    Advanced multi-step agentic service for mental health support.

    Architecture:
      1. Crisis triage   — deterministic keyword scan + level scoring
      2. Intent routing  — LLM zero-shot classification (cached)
      3. Tool planning   — intent → tool map + crisis overrides
      4. CoT reasoning   — structured chain-of-thought plan
      5. Response gen    — grounded generation with tool context
      6. Memory update   — sliding window + async compression
    """

    def __init__(self, session_id: Optional[str] = None) -> None:
        self.session_id = session_id or uuid.uuid4().hex
        self._api_key   = Config.GEMINI_API_KEY
        self._model_name = Config.GEMINI_MODEL_NAME
        self._memory    = ConversationMemory()
        self._model_cache: Optional[genai.GenerativeModel] = None
        self._active_model_name: Optional[str] = None
        self._intent_cache: Dict[str, Tuple[Intent, float]] = {}  # text → (intent, ts)
        self._spans: List[AgentSpan] = []
        self._configure()

    # ── Setup ───────────────────────────────────────────────────────────────

    def _configure(self) -> None:
        if not self._api_key:
            logger.warning("GEMINI_API_KEY not set — agent will use fallback responses.")
            return
        try:
            genai.configure(api_key=self._api_key)
        except Exception as exc:
            logger.error("Gemini configuration failed: %s", exc)

    def _get_model(self) -> Optional[genai.GenerativeModel]:
        if self._model_cache:
            return self._model_cache

        candidates = (
            [self._model_name] + list(_MODEL_FALLBACK_CHAIN)
            if self._model_name and self._model_name not in _MODEL_FALLBACK_CHAIN
            else list(_MODEL_FALLBACK_CHAIN)
        )

        for name in candidates:
            try:
                model = genai.GenerativeModel(name)
                self._model_cache = model
                self._active_model_name = name
                _trace("Model loaded: %s", name)
                return model
            except Exception:
                continue

        logger.error("All model candidates failed to load.")
        return None

    # ── Crisis Detection ─────────────────────────────────────────────────────

    def _assess_crisis_level(self, text: str) -> CrisisLevel:
        lower = text.lower()
        for level in sorted(CrisisLevel, reverse=True):
            if level == CrisisLevel.NONE:
                continue
            if any(kw in lower for kw in _CRISIS_LEVEL_KEYWORDS.get(level, [])):
                return level
        return CrisisLevel.NONE

    # ── Intent Classification ────────────────────────────────────────────────

    async def _classify_intent(self, user_input: str) -> Intent:
        # Check cache
        cached = self._intent_cache.get(user_input)
        if cached:
            intent, ts = cached
            if time.monotonic() - ts < _INTENT_CACHE_SECONDS:
                _trace("Intent cache hit: %s", intent)
                return intent

        model = self._get_model()
        if not model:
            return Intent.GENERAL

        prompt = (
            "Classify the mental health concern in the user message below into EXACTLY ONE label.\n"
            "Labels: anxiety, depression, stress, grief, relationship, self_esteem, sleep, crisis, general\n"
            "Respond with ONLY the label word, nothing else.\n\n"
            f"Message: {user_input[:400]}"
        )
        try:
            loop = asyncio.get_running_loop()
            resp: GenerateContentResponse = await loop.run_in_executor(
                None, lambda: model.generate_content(prompt)
            )
            raw = _extract_gemini_text(resp).lower()
            intent = Intent(raw) if raw in Intent._value2member_map_ else Intent.GENERAL
            self._intent_cache[user_input] = (intent, time.monotonic())
            return intent
        except Exception as exc:
            logger.warning("Intent classification failed (%s); defaulting to GENERAL.", exc)
            return Intent.GENERAL

    # ── Tool Planning ────────────────────────────────────────────────────────

    def _plan_tools(
        self,
        intent: Intent,
        crisis_level: CrisisLevel,
        user_input: str,
    ) -> List[ToolResult]:
        if crisis_level >= CrisisLevel.HIGH:
            tools = [
                ToolRegistry.crisis_hotlines(),
                ToolRegistry.safety_plan(),
                ToolRegistry.breathing(),
            ]
        elif crisis_level == CrisisLevel.MODERATE:
            tools = [
                ToolRegistry.safety_plan(),
                ToolRegistry.breathing(),
                ToolRegistry.grounding(),
            ]
        elif crisis_level == CrisisLevel.LOW:
            tools = [
                ToolRegistry.breathing(),
                ToolRegistry.grounding(),
                ToolRegistry.journal_prompt(user_input),
            ]
        else:
            factories = _INTENT_TOOL_MAP.get(intent, _INTENT_TOOL_MAP[Intent.GENERAL])
            tools = []
            for factory in factories:
                try:
                    # journal_prompt accepts optional context
                    if factory is ToolRegistry.journal_prompt:
                        tools.append(factory(user_input))
                    else:
                        tools.append(factory())
                except Exception as exc:
                    logger.warning("Tool factory %s failed: %s", factory, exc)

        _trace("Planned %d tool(s) for intent=%s crisis=%s", len(tools), intent, crisis_level)
        return tools

    # ── Chain-of-Thought Reasoning ───────────────────────────────────────────

    async def _chain_of_thought(
        self,
        user_input: str,
        intent: Intent,
        crisis_level: CrisisLevel,
        context: str,
    ) -> str:
        """
        Ask the model to reason step-by-step before generating the final reply.
        Returns a brief reasoning summary (not shown to user, used to ground response).
        """
        model = self._get_model()
        if not model:
            return "No reasoning available."

        prompt = (
            "You are SeraNova's internal reasoning engine.\n"
            "Given the following context, briefly answer these 3 questions in ≤3 sentences each:\n"
            "  Q1: What is the user's core emotional need right now?\n"
            "  Q2: What ONE thing could most help them in the next 10 minutes?\n"
            "  Q3: What should SeraNova avoid saying to not make things worse?\n\n"
            f"Intent: {intent.value}  |  Crisis level: {crisis_level.value}\n"
            f"Context:\n{context}\n\n"
            f"User message: {user_input}\n\n"
            "Reasoning (internal, not for user):"
        )
        try:
            loop = asyncio.get_running_loop()
            resp = await loop.run_in_executor(None, lambda: model.generate_content(prompt))
            return _extract_gemini_text(resp)[:600]
        except Exception as exc:
            logger.warning("CoT reasoning failed: %s", exc)
            return "Reasoning unavailable."

    # ── Memory Compression ───────────────────────────────────────────────────

    async def _maybe_compress_memory(self) -> None:
        if not self._memory.needs_compression():
            return
        model = self._get_model()
        if not model:
            return

        turns_text = self._memory.render()
        prompt = (
            "Summarise the following therapy-style conversation in 4–6 bullet points.\n"
            "Focus on: emotional themes, progress, key disclosures, and tools used.\n"
            "Be compassionate and specific. Use 'The user…' and 'SeraNova…'.\n\n"
            f"{turns_text}"
        )
        try:
            loop = asyncio.get_running_loop()
            resp = await loop.run_in_executor(None, lambda: model.generate_content(prompt))
            summary = _extract_gemini_text(resp)
            if summary:
                self._memory.compress(summary)
                logger.info("Memory compressed for session %s.", self.session_id)
        except Exception as exc:
            logger.warning("Memory compression failed: %s", exc)

    # ── Response Generation ──────────────────────────────────────────────────

    async def _generate_response(
        self,
        user_input: str,
        context: str,
        tools: List[ToolResult],
        crisis_level: CrisisLevel,
        reasoning: str,
        intent: Intent,
        retrieval_context: str = "",
        crew_notes: str = "",
    ) -> Tuple[str, str]:
        """Returns (response_text, model_name_used)."""

        if not self._api_key:
            return (
                "I'm here with you. The AI backbone isn't fully initialised right now, "
                "but you matter, and what you're feeling is real. "
                "Take one slow breath with me, then tell me what feels heaviest.",
                "fallback",
            )

        model = self._get_model()
        if not model:
            return (
                "I'm having trouble reaching my response engine. "
                "Please try again in a moment — I haven't gone anywhere.",
                "error",
            )

        tools_text = json.dumps(
            [t.to_dict() for t in tools], ensure_ascii=False, indent=2
        )

        system_persona = (
            "You are SeraNova — a compassionate, clinically-informed mental health support assistant.\n"
            "You are NOT a therapist or doctor; you do not diagnose or prescribe.\n"
            "Your role: hold space, validate emotion, offer evidence-based coping tools, "
            "and guide toward professional help when needed.\n"
        )

        crisis_instruction = ""
        if crisis_level >= CrisisLevel.HIGH:
            crisis_instruction = (
                "⚠ HIGH CRISIS — Your FIRST task is safety. "
                "Acknowledge the pain immediately. Strongly encourage contacting emergency services "
                "or a crisis line (provided in tools). Do not delay with lengthy exploration.\n"
            )
        elif crisis_level == CrisisLevel.MODERATE:
            crisis_instruction = (
                "MODERATE CONCERN — Validate, express care, gently surface the safety plan tool, "
                "and suggest professional support without alarming the user.\n"
            )

        rag_block = ""
        if (retrieval_context or "").strip():
            rag_block = (
                f"Relevant past conversation (retrieved for continuity; do not contradict—use only if it fits):\n"
                f"{retrieval_context.strip()}\n\n"
            )
        crew_block = ""
        if (crew_notes or "").strip():
            crew_block = (
                "Structured multi-agent notes (emotion/CBT; integrate lightly, do not read aloud as a list):\n"
                f"{crew_notes.strip()}\n\n"
            )

        prompt = (
            f"{system_persona}"
            f"{crisis_instruction}"
            f"{rag_block}{crew_block}"
            "Guidelines:\n"
            "  • Warm, plain language; avoid clinical jargon.\n"
            "  • 2–4 paragraphs max; no bullet lists in the reply itself.\n"
            "  • Weave 1–2 of the planned tools naturally into the response.\n"
            "  • End with an open, inviting question.\n"
            "  • Never dismiss, minimise, or over-promise.\n\n"
            f"Detected intent: {intent.value}\n"
            f"Crisis level: {crisis_level.value} / {CrisisLevel.IMMINENT.value}\n\n"
            f"Internal reasoning (do NOT repeat verbatim):\n{reasoning}\n\n"
            f"Planned support tools (weave in naturally):\n{tools_text}\n\n"
            f"Conversation so far:\n{context}\n\n"
            f"User: {user_input}\n\n"
            "SeraNova:"
        )

        last_exc: Optional[Exception] = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                loop = asyncio.get_running_loop()
                resp: GenerateContentResponse = await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: model.generate_content(prompt)),
                    timeout=_GENERATION_TIMEOUT,
                )
                text = _extract_gemini_text(resp)
                if not text:
                    raise ValueError("Empty model response on attempt %d" % attempt)
                return text, self._active_model_name or "unknown"
            except Exception as exc:
                last_exc = exc
                wait = _RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
                logger.warning(
                    "Generation attempt %d/%d failed (%s); retrying in %.1f s",
                    attempt, _MAX_RETRIES, exc, wait,
                )
                await asyncio.sleep(wait)
                # Invalidate model cache to force re-selection on next attempt
                if attempt < _MAX_RETRIES:
                    self._model_cache = None

        logger.error("All generation attempts exhausted. Last error: %s", last_exc)
        return (
            "Thank you for trusting me with this. I'm having a technical difficulty "
            "right now, but you deserve support. Please take three slow breaths "
            "and reach out to someone you trust — I'll be back shortly.",
            "error",
        )

    # ── Confidence Scoring ───────────────────────────────────────────────────

    @staticmethod
    def _compute_confidence(
        intent: Intent,
        crisis_level: CrisisLevel,
        tool_count: int,
    ) -> float:
        base = 0.80
        if intent != Intent.GENERAL:
            base += 0.07
        if tool_count >= 2:
            base += 0.05
        if crisis_level >= CrisisLevel.HIGH:
            base = max(base, 0.97)  # high precision needed in crisis
        return round(min(base, 0.99), 2)

    # ── Public API ───────────────────────────────────────────────────────────

    async def agenerate(
        self,
        user_input: str,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """
        Primary async entry point.

        Steps:
          1. Crisis triage
          2. Async intent classification
          3. Tool planning
          4. CoT reasoning
          5. Response generation (with retry)
          6. Memory update + async compression
          7. Observability packaging
        """
        self._spans = []  # reset per call

        # 1. Crisis triage
        s1 = AgentSpan(name="crisis_triage")
        crisis_level = self._assess_crisis_level(user_input)
        s1.finish(crisis_level=crisis_level.value)
        self._spans.append(s1)

        # 2. Intent classification (skip if crisis — always crisis intent)
        s2 = AgentSpan(name="intent_classification")
        if crisis_level >= CrisisLevel.MODERATE:
            intent = Intent.CRISIS
        else:
            intent = await self._classify_intent(user_input)
        s2.finish(intent=intent.value)
        self._spans.append(s2)

        # 3. Tool planning
        s3 = AgentSpan(name="tool_planning")
        tools = self._plan_tools(intent, crisis_level, user_input)
        s3.finish(tool_count=len(tools))
        self._spans.append(s3)

        # 4. Context rendering
        context_text = self._memory.render()

        # 5. Chain-of-thought reasoning
        s4 = AgentSpan(name="chain_of_thought")
        reasoning = await self._chain_of_thought(user_input, intent, crisis_level, context_text)
        s4.finish()
        self._spans.append(s4)

        # 6. Response generation
        extra = extra_context or {}
        s5 = AgentSpan(name="response_generation")
        response_text, model_used = await self._generate_response(
            user_input=user_input,
            context=context_text,
            tools=tools,
            crisis_level=crisis_level,
            reasoning=reasoning,
            intent=intent,
            retrieval_context=str(extra.get("retrieval_context", "") or ""),
            crew_notes=str(extra.get("crew_notes", "") or ""),
        )
        s5.finish(model=model_used, tokens_approx=len(response_text.split()))
        self._spans.append(s5)

        # 7. Memory update
        self._memory.add(Turn(role="user", content=user_input,
                              intent=intent.value, crisis_level=crisis_level.value))
        self._memory.add(Turn(role="assistant", content=response_text))
        await self._maybe_compress_memory()

        return AgentResponse(
            session_id=self.session_id,
            intent=intent.value,
            crisis_level=crisis_level.value,
            response=response_text,
            tools_used=[t.tool_id.value for t in tools],
            reasoning_summary=reasoning,
            confidence=self._compute_confidence(intent, crisis_level, len(tools)),
            spans=[{"name": s.name, "duration_ms": s.duration_ms, **s.tags}
                   for s in self._spans],
            model_used=model_used,
        )

    def generate(
        self,
        user_input: str,
        history: Optional[List[Dict[str, Any]]] = None,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Synchronous shim for legacy callers.

        Accepts the old `history` list and hydrates memory before calling
        the async pipeline.
        """
        # Hydrate memory from legacy history format
        if history:
            for item in history:
                msg  = item.get("message", "") or item.get("user", "")
                resp = item.get("response", "") or item.get("assistant", "")
                if msg:
                    self._memory.add(Turn(role="user", content=msg))
                if resp:
                    self._memory.add(Turn(role="assistant", content=resp))

        try:
            # Flask/Werkzeug runs each request in a worker thread with no event loop.
            # asyncio.get_event_loop() raises there on Python 3.10+; use asyncio.run() instead.
            try:
                result: AgentResponse = asyncio.run(
                    self.agenerate(user_input, extra_context)
                )
            except RuntimeError as rexc:
                if "cannot be called from a running event loop" in str(rexc).lower():
                    # e.g. sync caller already inside a running loop (Jupyter, nested async)
                    import concurrent.futures

                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                        future = pool.submit(
                            asyncio.run,
                            self.agenerate(user_input, extra_context),
                        )
                        result = future.result(timeout=_GENERATION_TIMEOUT + 60)
                else:
                    raise
        except Exception as exc:
            logger.error("Sync shim failed: %s", exc)
            return {
                "intent": "general",
                "crisis_level": 0,
                "response": (
                    "I'm here. Something went wrong on my end. "
                    "Please try again or contact a trusted person if you need support now."
                ),
                "tools_used": [],
                "confidence": 0.0,
                "agent": {"error": str(exc)},
            }

        return result.to_dict()

    def generate_agent_response(
        self,
        user_input: str,
        history: Optional[List[Dict[str, Any]]] = None,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Route-compatible wrapper expected by existing Flask handlers.
        When ORCHESTRATION_MODE=langgraph, runs the LangGraph + Crew + RAG pipeline; otherwise
        the in-class AgenticChatService (legacy). Always applies a direct Gemini pass if
        the primary reply is missing or a known error boilerplate.
        """
        if Config.ORCHESTRATION_MODE == "langgraph":
            try:
                from orchestration.orchestrator_service import run_langgraph_pipeline

                result = run_langgraph_pipeline(
                    user_input, history, extra_context
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "LangGraph orchestration failed, using legacy agent: %s",
                    exc,
                    exc_info=True,
                )
                result = self.generate(
                    user_input=user_input,
                    history=history,
                    extra_context=extra_context,
                )
        else:
            result = self.generate(
                user_input=user_input,
                history=history,
                extra_context=extra_context,
            )

        return apply_degraded_gemini_fallback(result, user_input)


def apply_degraded_gemini_fallback(
    result: Dict[str, Any],
    user_input: str,
    extra_agent: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Public helper: maps flat AgentResponse-style dicts to the API schema and
    applies direct Gemini if the main reply is missing or known-degraded.
    Merges optional result[\"orchestration_meta\"] into the response agent payload.
    """
    om = result.get("orchestration_meta")
    if isinstance(om, dict):
        merged: Dict[str, Any] = {**(extra_agent or {}), **om}
    else:
        merged = dict(extra_agent or {})
    response_text = (result.get("response") or "").strip()
    agent_err: Optional[str] = None
    a = result.get("agent")
    if isinstance(a, dict):
        agent_err = a.get("error")  # type: ignore[assignment]

    if _is_degraded_agent_text(response_text) or agent_err:
        try:
            fb = gemini_service.generate_mental_health_response(user_input)
            fb_text = (fb.get("response") or "").strip()
            if fb_text and fb.get("intent") != "error":
                logger.info("Using gemini_service fallback after agent degraded/error.")
                merge = {
                    "session_id": result.get("session_id"),
                    "crisis_level": result.get("crisis_level", 0),
                    "tools_used": result.get("tools_used", []),
                    "reasoning_summary": result.get("reasoning_summary", ""),
                    "model_used": result.get("model_used"),
                    "spans": result.get("spans", []),
                    "generated_at": result.get("generated_at"),
                    "fallback": "gemini_direct",
                    "prior_error": str(agent_err) if agent_err else None,
                }
                if merged:
                    merge.update(merged)
                return {
                    "intent": fb.get("intent", "mental_health_support"),
                    "response": fb_text,
                    "confidence": float(fb.get("confidence", 0.85)),
                    "agent": merge,
                }
        except Exception as exc:
            logger.warning("gemini_service fallback failed: %s", exc)

    ag = {
        "session_id": result.get("session_id"),
        "crisis_level": result.get("crisis_level", 0),
        "tools_used": result.get("tools_used", []),
        "reasoning_summary": result.get("reasoning_summary", ""),
        "model_used": result.get("model_used"),
        "spans": result.get("spans", []),
        "generated_at": result.get("generated_at"),
    }
    if merged:
        ag.update(merged)
    return {
        "intent": result.get("intent", "general"),
        "response": result.get("response", ""),
        "confidence": result.get("confidence", 0.0),
        "agent": ag,
    }


# ─────────────────────────────────────────────
# Module-level singleton (drop-in replacement)
# ─────────────────────────────────────────────
agentic_chat_service = AgenticChatService()