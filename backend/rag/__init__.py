"""RAG layer (vector retrieval for session-aware context)."""
from .vector_store import SessionRAGIndex, get_rag_index

__all__ = ["SessionRAGIndex", "get_rag_index"]
