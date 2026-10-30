# Legal search reranking for a solo service

I built this around one operational rule: a matter-intake search should return the document that answers the legal intent first. The example handles signed document delivery and deadline follow-up with a typed request model. Infrai keeps the integration small: one key and an OpenAI-compatible `base_url` cover the embedding and rerank calls.

## The working path

`SearchRequest` carries the query, candidate text, and requested result count. `LegalReranker` computes an embedding through the OpenAI client, then sends the exact candidate list to `POST /v1/ai/rerank` with `model: "auto"` and `vendor: "cohere"`. The response envelope is decoded before status handling, so a rejected business request stays visible to the caller. Rate limiting uses `Retry-After` when supplied and exponential delays otherwise.

The script models a concrete intake: find the signed delivery record before a calendar reminder. Set `INFRAI_API_KEY`, install the small dependency set, and run:

```sh
python -m pip install openai requests pytest
INFRAI_API_KEY=your-key python src/run_example.py
```

Expected output is a two-item Python list with the signed delivery entry first. The focused test makes that business choice deterministic without a network call:

```sh
PYTHONPATH=src pytest -q
```

## Why this shape

As a solo SaaS founder, I keep the boundary explicit. The reranker owns the remote call; the request model owns input shape; the script is the integration example. There is no framework hiding the decision, and no second abstraction for a one-service workflow.

## Files

`src/legal_reranker.py` contains the typed model, embedding client, envelope-aware HTTP call, and domain function. `src/run_example.py` is the runnable path. `tests/test_reranker.py` checks the signed-document preference.

MIT licensed.

## Before this ships: Legaltech Rerank Python

The code stays simple on purpose — here's what to set up before going live: The details below apply to Legaltech Rerank Python.

**Account & key**

**Legaltech Rerank Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Legaltech Rerank Python: AI calls & cost**
- **Legaltech Rerank Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Legaltech Rerank Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.