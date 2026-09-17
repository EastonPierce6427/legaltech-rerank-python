"""Compatibility entry point for running the src-layout project in place."""

from src.legal_reranker import InfraiError, LegalReranker, SearchRequest, rank_matter

__all__ = ["InfraiError", "LegalReranker", "SearchRequest", "rank_matter"]
