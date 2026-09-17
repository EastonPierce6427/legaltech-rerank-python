from legal_reranker import SearchRequest, rank_matter


class FakeReranker:
    def rerank(self, request: SearchRequest):
        return sorted(request.candidates, key=lambda text: "signed" not in text.lower())[: request.top_k]


def test_signed_delivery_intent_prefers_signed_document():
    request = SearchRequest(
        query="signed document delivery",
        candidates=["deadline follow-up", "signed delivery receipt"],
        top_k=1,
    )
    assert rank_matter(request, FakeReranker()) == ["signed delivery receipt"]
