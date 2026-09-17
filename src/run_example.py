from legal_reranker import LegalReranker, SearchRequest, rank_matter


def main() -> None:
    request = SearchRequest(
        query="signed delivery receipt for a settlement agreement",
        candidates=[
            "Matter intake: opposing counsel requests a signed settlement copy.",
            "Deadline follow-up: calendar the filing date and notify the client.",
            "Signed document delivery log with recipient and timestamp.",
        ],
        top_k=2,
    )
    print(rank_matter(request, LegalReranker()))


if __name__ == "__main__":
    main()
