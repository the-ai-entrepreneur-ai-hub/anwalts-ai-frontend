"""
Minimal RAG service stub to satisfy imports.

Production implementation should provide a `rag_service` object with a
`retrieve(query: str)` method returning a list of documents or passages.
"""

from typing import List, Dict, Any


class _RAGService:
    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        # Return an empty result set as a safe default
        return []


rag_service = _RAGService()

