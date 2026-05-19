# Gemini Review Request: Goal2435 RT-DBSCAN Single-Pass Chunked Adjacency

Please review Goal2435 as an independent Gemini/Antigravity reviewer.

## Files To Inspect

- `docs/reports/goal2435_rt_dbscan_single_pass_chunked_adjacency_2026-05-19.md`
- `docs/reports/goal2435_rt_dbscan_single_pass_chunked_adjacency_pod/*.json`
- `tests/goal2435_rt_dbscan_single_pass_chunked_adjacency_test.py`
- `src/rtdsl/partner_adapters.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/README.md`
- `docs/research/future_version_to_do_list.md`

Optional context:

- `docs/reports/goal2433_rt_dbscan_chunked_adjacency_continuation_2026-05-19.md`
- `docs/reviews/goal2434_gemini_review_goal2431_2433_rt_dbscan_adjacency_continuation_2026-05-19.md`

## Context

Goal2433 added a memory-bounded chunked OptiX adjacency continuation, but it
filled adjacency chunks twice. Goal2435 changes that continuation so the chunked
union pass also captures one core-neighbor candidate per non-core border point.
The final label kernel then labels borders from final parent roots without a
second RT adjacency fill.

Evidence:

- tiny exact fixture matches reference;
- clustered 4096 and 8192 repeat probes match signatures;
- clustered 32768 chunked probe matches signature;
- chunked runtime improved over Goal2433, but remains slower than full
  adjacency when full adjacency fits.

## Review Questions

1. Is the single-pass border-candidate algorithm correct for generic
   fixed-radius component labels?
2. Does it preserve the app-agnostic boundary and avoid DBSCAN-native engine
   logic?
3. Do the report and README honestly state that this is a memory/continuation
   improvement, not a broad speedup claim?
4. Are the tests and artifacts enough for an `accept-with-boundary` verdict, or
   is more pod evidence needed?

## Required Output

Write the review to:

`docs/reviews/goal2436_gemini_review_goal2435_single_pass_chunked_adjacency_2026-05-19.md`

Use one verdict:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Expected likely verdict is `accept-with-boundary` unless you find a concrete
bug or overclaim.
