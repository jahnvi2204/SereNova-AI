"""
CrewAI: specialized agents (emotion framing + CBT focus) with Gemini via LiteLLM.
Falls back to an empty string if Crew is disabled or the stack is unavailable.
"""
from __future__ import annotations

import logging
import os
from typing import Any

from config import Config

logger = logging.getLogger(__name__)


def _gemini_crew() -> bool:
    return bool((Config.GEMINI_API_KEY or "").strip())


def run_crew_assessment(user_text: str, crisis_level: int) -> str:
    """
    Run a tiny sequential crew: (1) emotional tone/summary, (2) one CBT angle.
    """
    if not _gemini_crew() or not Config.CREW_ENABLED:
        return ""
    if crisis_level >= 2:
        # Crisis path already uses crisis tools; keep crew very light
        return ""

    try:
        from crewai import LLM, Agent, Task, Crew, Process
    except Exception as exc:
        logger.debug("CrewAI not importable: %s", exc)
        return ""

    # LiteLLM-style provider path used by Crew against Gemini
    model_name = f"gemini/{Config.GEMINI_MODEL_NAME.split('/')[-1] if '/' in Config.GEMINI_MODEL_NAME else Config.GEMINI_MODEL_NAME}"
    key = (Config.GEMINI_API_KEY or "").strip()
    for env_key in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GEMINI_API_KEY"):
        os.environ.setdefault(env_key, key or "")

    try:
        llm = LLM(
            model=model_name,
            api_key=key,
        )
    except Exception as exc:
        logger.warning("Crew LLM init failed: %s", exc)
        return ""

    agent_emotion = Agent(
        role="Emotion analyst",
        goal="Describe the user\u2019s likely emotional need in 2 short lines (no advice).",
        backstory="You are precise and compassionate; you never diagnose.",
        llm=llm,
        allow_delegation=False,
    )
    agent_cbt = Agent(
        role="CBT coach (informational)",
        goal="Propose one evidence-based CBT micro-step appropriate to the message (1\u20132 sentences).",
        backstory="You only suggest CBT ideas; you are not a replacement for a clinician.",
        llm=llm,
        allow_delegation=False,
    )
    t1 = Task(
        description=(
            f"User message:\n\"{user_text[:2000]}\"\n\n"
            "Output exactly two short lines: line 1 = emotional tone / needs; line 2 = what would help them feel heard."
        ),
        expected_output="Two plain-text lines, no JSON.",
        agent=agent_emotion,
    )
    t2 = Task(
        description=(
            f"User message (same as before):\n\"{user_text[:2000]}\"\n\n"
            "Offer ONE CBT-consistent micro-technique the main assistant can weave in (1\u20132 sentences; not a list). "
        ),
        expected_output="One or two sentences.",
        agent=agent_cbt,
    )
    try:
        crew = Crew(
            agents=[agent_emotion, agent_cbt],
            tasks=[t1, t2],
            process=Process.sequential,
            verbose=False,
        )
        out: Any = crew.kickoff()
        text = str(getattr(out, "raw", None) or out)
        if not (text and text.strip()):
            return ""
        return text.strip()[:2000]
    except Exception as exc:
        logger.warning("Crew run failed: %s", exc)
        return ""
