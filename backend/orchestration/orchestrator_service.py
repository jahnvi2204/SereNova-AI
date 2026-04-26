"""
LangGraph pipeline: triage (guardrails) -> optional Crew (emotion/CBT) -> RAG -> Agentic generation.
Crisis levels HIGH/IMMINENT take a fast crisis pathway with hotlines + safety content.
"""
from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TypedDict

from config import Config

logger = logging.getLogger(__name__)

_compiled: Any = None


class GraphState(TypedDict, total=False):
    user_input: str
    history: List[Dict[str, Any]]
    extra: Dict[str, Any]
    session_id: str
    crisis_level: int
    crew_notes: str
    rag_context: str
    result: Dict[str, Any]
    t0: float


def _route_after_triage(st: GraphState) -> str:
    cl = int(st.get("crisis_level", 0) or 0)
    if cl >= 3:  # HIGH (3) or IMMINENT (4)
        return "crisis"
    return "crew"


def _node_triage(st: GraphState) -> Dict[str, Any]:
    from agent_service import assess_crisis_text

    t0 = st.get("t0", time.perf_counter())
    return {
        "crisis_level": assess_crisis_text(st.get("user_input", "")),
        "t0": t0,
    }


def _node_crisis(st: GraphState) -> Dict[str, Any]:
    from agent_service import ToolRegistry

    hot = ToolRegistry.crisis_hotlines()
    sp = ToolRegistry.safety_plan()
    br = ToolRegistry.breathing()
    body = f"{hot.content}\n\n{sp.content}\n\n{br.content}"
    intro = (
        "I'm really glad you're here, and I want you to be safe. "
        "The thoughts you're sharing can be heavy — you deserve real-time human support, not just an app. "
    )
    sid = st.get("session_id") or uuid.uuid4().hex
    cl = int(st.get("crisis_level", 0) or 0)
    return {
        "result": {
            "session_id": sid,
            "intent": "crisis",
            "crisis_level": cl,
            "response": f"{intro}\n\n{body[:3500]}",
            "tools_used": [hot.tool_id.value, sp.tool_id.value, br.tool_id.value],
            "reasoning_summary": "Guardrails: high-acuity crisis pathway (no LLM).",
            "confidence": 0.97,
            "spans": [
                {
                    "name": "crisis_fast_path",
                    "duration_ms": 0.0,
                    "kind": "guardrail",
                }
            ],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model_used": "guardrail_crisis",
            "orchestration_meta": {
                "orchestrator": "langgraph",
                "node": "crisis",
            },
        }
    }


def _node_crew(st: GraphState) -> Dict[str, Any]:
    if not Config.CREW_ENABLED or int(st.get("crisis_level", 0) or 0) >= 2:
        return {"crew_notes": ""}
    t1 = time.perf_counter()
    from .crew_assessment import run_crew_assessment

    notes = run_crew_assessment(
        st.get("user_input", ""),
        int(st.get("crisis_level", 0) or 0),
    )
    return {
        "crew_notes": notes or "",
        "crew_ms": (time.perf_counter() - t1) * 1000.0,
    }


def _node_rag(st: GraphState) -> Dict[str, Any]:
    if not Config.RAG_ENABLED:
        return {"rag_context": ""}
    t1 = time.perf_counter()
    from rag.vector_store import get_rag_index

    idx = get_rag_index()
    if not idx:
        return {"rag_context": ""}
    ex = st.get("extra") or {}
    sid = st.get("session_id") or (ex.get("session_id") if isinstance(ex, dict) else None) or "anon"
    ctx = idx.retrieve(
        str(sid),
        st.get("user_input", "") or "",
        k=3,
    )
    return {
        "rag_context": ctx or "",
        "rag_ms": (time.perf_counter() - t1) * 1000.0,
    }


def _node_synthesize(st: GraphState) -> Dict[str, Any]:
    t1 = time.perf_counter()
    from agent_service import AgenticChatService

    ex = dict(st.get("extra") or {}) if isinstance(st.get("extra"), dict) else {}
    sid = st.get("session_id") or ex.get("session_id")
    if not sid:
        sid = uuid.uuid4().hex
    ex["retrieval_context"] = (st.get("rag_context", "") or "")[:8000]
    ex["crew_notes"] = (st.get("crew_notes", "") or "")[:4000]

    chat = AgenticChatService(session_id=sid)
    raw = chat.generate(
        st.get("user_input", "") or "",
        st.get("history") or [],
        extra_context=ex,
    )
    if not raw:
        raise RuntimeError("Empty agent generate result")
    gen_ms = (time.perf_counter() - t1) * 1000.0
    t0 = st.get("t0", time.perf_counter())
    total_ms = (time.perf_counter() - t0) * 1000.0
    om = (raw.get("orchestration_meta") or {}) if isinstance(raw.get("orchestration_meta"), dict) else {}
    raw = dict(raw)
    raw["orchestration_meta"] = {
        "orchestrator": "langgraph",
        "node": "synthesize",
        "llm_path_ms": round(gen_ms, 2),
        "graph_total_ms": round(total_ms, 2),
        "crew_ran": bool((st.get("crew_notes") or "").strip()),
        "rag_hits": bool((st.get("rag_context") or "").strip()),
        **om,
    }
    return {"result": raw}


def _build_graph() -> Any:
    from langgraph.graph import END, StateGraph

    g = StateGraph(GraphState)
    g.add_node("triage", _node_triage)
    g.add_node("crisis", _node_crisis)
    g.add_node("crew", _node_crew)
    g.add_node("rag", _node_rag)
    g.add_node("synthesize", _node_synthesize)
    g.set_entry_point("triage")
    g.add_conditional_edges("triage", _route_after_triage, {"crisis": "crisis", "crew": "crew"})
    g.add_edge("crisis", END)
    g.add_edge("crew", "rag")
    g.add_edge("rag", "synthesize")
    g.add_edge("synthesize", END)
    return g.compile()


def get_compiled_graph() -> Any:
    global _compiled
    if _compiled is None:
        _compiled = _build_graph()
    return _compiled


def run_langgraph_pipeline(
    user_input: str,
    history: Optional[List[Dict[str, Any]]] = None,
    extra_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run the full LangGraph; returns a flat dict compatible with AgentResponse.to_dict()
    (plus optional orchestration_meta for the API wrapper).
    """
    extra = dict(extra_context) if extra_context else {}
    sid = str(extra.get("session_id") or "") or uuid.uuid4().hex
    t0 = time.perf_counter()
    initial: GraphState = {
        "user_input": user_input,
        "history": list(history or []),
        "extra": extra,
        "session_id": sid,
        "t0": t0,
    }
    g = get_compiled_graph()
    out = g.invoke(initial)
    result = (out or {}).get("result")
    if not isinstance(result, dict):
        raise RuntimeError("LangGraph returned no result")

    # Post-index the exchange for the next turn (RAG for continuity; skip acuity fast-path)
    try:
        if result.get("model_used") == "guardrail_crisis":
            pass
        elif Config.RAG_ENABLED and sid and sid != "anon":
            from rag.vector_store import get_rag_index

            idx = get_rag_index()
            if idx and (result.get("response") or "").strip():
                idx.add_turn(
                    sid,
                    user_input,
                    (result.get("response") or "").strip(),
                )
    except Exception as exc:  # noqa: BLE001
        logger.debug("RAG index write skipped: %s", exc)

    return result
