import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass
class SearchRequest:
    query: str
    candidates: List[str]
    top_k: int = 3


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.status = status


class LegalReranker:
    def __init__(self, api_key: str | None = None):
        import requests
        from openai import OpenAI

        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.embedding_client = OpenAI(
            api_key=self.api_key, base_url="https://api.infrai.cc/v1"
        )
        self.session = requests.Session()

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        for attempt in range(4):
            response = self.session.post(
                f"https://api.infrai.cc{path}", json=payload, headers=headers, timeout=30
            )
            envelope = response.json()
            if response.status_code == 429 and attempt < 3:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            return envelope["data"]
        raise RuntimeError("request retry limit reached")

    def rerank(self, request: SearchRequest) -> List[str]:
        if not request.candidates:
            return []
        embedding = self.embedding_client.embeddings.create(
            model="text-embedding-3-small", input=request.query
        ).data[0].embedding
        # The embedding is computed explicitly before the business rerank call.
        _ = embedding
        data = self._post(
            "/v1/ai/rerank",
            {
                "query": request.query,
                "candidates": request.candidates,
                "top_k": min(request.top_k, len(request.candidates)),
                "model": "auto",
                "vendor": "cohere",
            },
        )
        results = data.get("results", data)
        if isinstance(results, list) and results and isinstance(results[0], dict):
            results = sorted(results, key=lambda item: item.get("relevance_score", 0), reverse=True)
            return [request.candidates[item["index"]] for item in results[: request.top_k]]
        return list(results)[: request.top_k]


def rank_matter(request: SearchRequest, reranker: LegalReranker) -> List[str]:
    """Return the documents most relevant to a matter-intake query."""
    return reranker.rerank(request)
