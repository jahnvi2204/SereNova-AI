"""Chroma-backed session RAG: retrieve prior turns to ground the LLM pipeline."""
from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Any, List, Optional

from config import Config

logger = logging.getLogger(__name__)

_rag_index: Optional["SessionRAGIndex"] = None


def get_rag_index() -> Optional["SessionRAGIndex"]:
    """Lazily open persistent Chroma; returns None if unavailable (missing deps or disk)."""
    global _rag_index
    if not Config.RAG_ENABLED:
        return None
    if _rag_index is not None:
        return _rag_index
    try:
        _rag_index = SessionRAGIndex()
    except Exception as exc:
        logger.warning("RAG index unavailable: %s", exc)
        _rag_index = None
    return _rag_index


class SessionRAGIndex:
    """Per-session turn storage + similarity search (Chroma persistent store)."""

    def __init__(self, persist_dir: Optional[Path] = None) -> None:
        import chromadb
        from chromadb.utils import embedding_functions

        root = Path(__file__).resolve().parent.parent
        p = Path(persist_dir) if persist_dir else root / Config.CHROMA_PERSIST_DIR
        p.mkdir(parents=True, exist_ok=True)

        self._client = chromadb.PersistentClient(path=str(p))
        self._ef = embedding_functions.DefaultEmbeddingFunction()
        self._col = self._client.get_or_create_collection(
            name="serenova_turns",
            embedding_function=self._ef,
            metadata={"hnsw:space": "cosine"},
        )

    def add_turn(
        self,
        session_id: str,
        user_text: str,
        assistant_text: str,
    ) -> None:
        if not (user_text or "").strip() and not (assistant_text or "").strip():
            return
        doc = f"User: {user_text}\nAssistant: {assistant_text}"
        uid = f"{session_id}_{uuid.uuid4().hex[:16]}"
        self._col.add(
            documents=[doc],
            ids=[uid],
            metadatas=[{"session_id": str(session_id)}],
        )

    def retrieve(self, session_id: str, query: str, k: int = 3) -> str:
        if not (query or "").strip():
            return ""
        try:
            res = self._col.query(
                query_texts=[query],
                n_results=k,
                where={"session_id": str(session_id)},
            )
        except Exception as exc:
            logger.debug("RAG query failed: %s", exc)
            return ""
        docs: List[Any] = (res or {}).get("documents") or []
        if not docs or not docs[0]:
            return ""
        out: List[str] = [d for d in docs[0] if d and str(d).strip()]
        return "\n---\n".join(out) if out else ""
