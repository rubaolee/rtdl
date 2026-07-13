# Call For Review - Goal5018 Public Workspace Query-Many Probe

Please review:

- `history/internal_docs/goal5018_public_workspace_query_many_result_2026-07-05.md`
- `history/internal_docs/goal5018_public_workspace_query_many_result_2026-07-05.json`
- `history/internal_docs/goal5018_public_workspace_query_many_probe.py`
- `src/rtdsl/optix_runtime.py`

## Requested Verdict

`approve_goal5018_public_workspace_query_many_probe_no_10x`

## Review Questions

1. Does Goal5018 genuinely use the public workspace/query lifecycle rather than
   private locator bootstrap handles for the prepared-base query-many route?

2. Is the regime correctly labeled as prepared-base / same-domain / distinct
   query batches, not cold CLI, not same-input replay, and not author parity?

3. Do the structural anchors (`428,322` LSI rows and `15,014` descriptor pairs
   for all three queries) support correctness/consistency for this bounded
   performance probe?

4. Is the performance interpretation honest: first query `4.657s` contains
   warmup/compile effects, while stable queries are about `1.13s/query`?

5. Is it correct to say this productizes the earlier `~1.22s/query` hand-built
   route through public APIs, but does not reach the `~0.42s/query` target?

6. Is the next bottleneck correctly identified as query-specific point-location
   locator preparation (`~0.41s/query`) plus downstream continuation
   (`~0.60s/query`)?

7. Does the report avoid claiming 10x, author parity, cold CLI speedup, or full
   zero-copy?
