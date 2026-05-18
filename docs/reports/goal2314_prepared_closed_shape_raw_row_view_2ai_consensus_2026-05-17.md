# Goal2314 Prepared Closed-Shape Raw Row View 2-AI Consensus

## Scope

Goal2314 records 2-AI consensus for Goal2312, which added a generic
`PreparedOptixPointClosedShapeMembership2D.run_raw(...)` row-view path and used
it to refresh the current RayJoin-style prepared comparison.

Reviewed artifacts:

- `src/rtdsl/optix_runtime.py`
- `scripts/goal2292_rayjoin_current_prepared_comparison.py`
- `docs/reports/goal2312_prepared_closed_shape_raw_row_view_2026-05-17.md`
- `docs/reports/goal2312_prepared_closed_shape_raw_row_view_pod_2026-05-17.json`
- `tests/goal2312_prepared_closed_shape_raw_row_view_test.py`
- `docs/reviews/goal2313_gemini_review_goal2312_raw_row_view_rayjoin_perf_2026-05-17.md`

## Verdicts

| Reviewer | Artifact | Verdict |
| --- | --- | --- |
| Codex | `docs/reports/goal2312_prepared_closed_shape_raw_row_view_2026-05-17.md` | `accept-with-boundary` |
| Gemini | `docs/reviews/goal2313_gemini_review_goal2312_raw_row_view_rayjoin_perf_2026-05-17.md` | `accept-with-boundary` |

## Accepted Claim

For the scoped RayJoin-exported 100,000-query streams on the RTX A5000 pod,
RTDL's current prepared route now operates at low-millisecond query-execution
scale:

| Row | Median seconds | Exact rows |
| --- | ---: | ---: |
| LSI raw witness rows | 0.010123 | 8,921 |
| LSI scalar count | 0.009986 | 8,921 |
| PIP positive raw row view | 0.008657 | 8,686 |
| PIP scalar count | 0.008476 | 8,686 |

The accepted improvement is specifically that PIP positive-row output no
longer pays Python dictionary materialization when the caller asks for a raw
row view. Compared with Goal2305, PIP positive-row median time improved from
`0.023158s` to `0.008657s` while preserving the exact expected count.

## Boundary

This consensus does not authorize any of the following:

- RTDL beats the RayJoin paper implementation.
- The full RayJoin paper benchmark has been reproduced.
- Whole-app speedup.
- True zero-copy.
- Device-resident continuation.
- v2.0 release authorization.

The next meaningful RayJoin-style improvement remains generic device-resident
row-stream / continuation work, not an app-specific native engine path.
