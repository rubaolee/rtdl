# Handoff: Gemini Review for Goal3002/Goal3003 RayJoin Numba Compact Mask

## Requested Output

Write an independent Gemini review to:

`docs/reviews/goal3004_gemini_review_goal3002_3003_rayjoin_numba_compact_mask_2026-06-01.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Scope

Review the current `main` branch around:

- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `src/rtdsl/numba_partner_continuation.py`
- `src/rtdsl/v2_6_roadmap.py`
- `scripts/goal3003_rayjoin_numba_compact_mask_pod_runner.py`
- `docs/reports/goal3002_rayjoin_numba_compact_mask_wiring_2026-06-01.md`
- `docs/reports/goal3003_rayjoin_numba_compact_mask_pod_runner_2026-06-01.md`
- `docs/reports/goal3003_rayjoin_numba_compact_mask_l4_pod_2026-06-01.md`
- `docs/reports/goal3003_rayjoin_numba_compact_mask_l4_pod_2026-06-01.json`
- `tests/goal3002_rayjoin_numba_compact_mask_wiring_test.py`
- `tests/goal3003_rayjoin_numba_compact_mask_pod_runner_test.py`
- `tests/goal3003_rayjoin_numba_compact_mask_l4_pod_test.py`

## Questions To Answer

1. Does Goal3002 correctly wire RayJoin-style row-stream compaction through the generic `compact_mask_i64` Numba primitive without app-specific native-engine logic?
2. Does Goal3003 provide credible L4 runtime evidence across `pip`, `lsi`, and `overlay_seed`: clean source commit, CUDA device arrays, neutral handoff accepted, CPU oracle parity, and all public/release/speedup claims blocked?
3. Does the work preserve the prepared generic RTDL count/parity path as the recommended scalar fast path instead of replacing it with Numba?
4. Does the evidence overclaim anything about RayJoin paper reproduction, `RTDL beats RayJoin`, v2.6 release readiness, Numba speedup, RT-core speedup, whole-app speedup, or true zero-copy?
5. What residual risks remain before stronger RayJoin-facing user claims could be made?

## Validation Command

If shell execution is available, run:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3003_rayjoin_numba_compact_mask_l4_pod_test tests.goal3003_rayjoin_numba_compact_mask_pod_runner_test tests.goal3002_rayjoin_numba_compact_mask_wiring_test tests.goal3000_triangle_counting_numba_compact_mask_l4_pod_test tests.goal2806_v2_5_internal_readiness_packet_test
```

If shell execution is not available, disclose that clearly and perform a static/artifact review.

## Required Boundary

The review must not authorize release, public speedup wording, whole-app speedup wording, broad RT-core speedup wording, true-zero-copy wording, automatic partner selection, app-specific native-engine logic, RayJoin paper-reproduction claims, or `RTDL beats RayJoin` claims.
