# Handoff: Gemini Review for Goal2999/Goal3000 Triangle Numba Compact Mask

## Requested Output

Write an independent Gemini review to:

`docs/reviews/goal3001_gemini_review_goal2999_3000_triangle_numba_compact_mask_2026-06-01.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Scope

Review the current `main` branch around:

- `examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py`
- `src/rtdsl/numba_partner_continuation.py`
- `src/rtdsl/v2_6_roadmap.py`
- `scripts/goal3000_triangle_counting_numba_compact_mask_pod_runner.py`
- `docs/reports/goal2999_triangle_counting_numba_compact_mask_wiring_2026-06-01.md`
- `docs/reports/goal3000_triangle_counting_numba_compact_mask_pod_runner_2026-06-01.md`
- `docs/reports/goal3000_triangle_counting_numba_compact_mask_l4_pod_2026-06-01.md`
- `docs/reports/goal3000_triangle_counting_numba_compact_mask_l4_pod_2026-06-01.json`
- `tests/goal2999_triangle_counting_numba_compact_mask_wiring_test.py`
- `tests/goal3000_triangle_counting_numba_compact_mask_pod_runner_test.py`
- `tests/goal3000_triangle_counting_numba_compact_mask_l4_pod_test.py`

## Questions To Answer

1. Does Goal2999 correctly wire triangle-counting-style witness-row compaction through the generic `compact_mask_i64` Numba primitive without app-specific native-engine logic?
2. Does Goal3000 provide credible L4 runtime evidence for that app-level wiring: clean source commit, CUDA device arrays, neutral handoff accepted, CPU oracle parity, and all public/release/speedup claims blocked?
3. Is the `_numba_cuda_redirector` fix a legitimate general robustness improvement for `--target` installed `numba-cuda`, rather than a one-off pod workaround?
4. Does the evidence overclaim anything about v2.6 release readiness, whole-app triangle-counting speedup, RT-core speedup, Numba speedup, or true zero-copy?
5. What residual risks remain before v2.6 could make stronger user-facing claims?

## Validation Command

If shell execution is available, run:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3000_triangle_counting_numba_compact_mask_l4_pod_test tests.goal3000_triangle_counting_numba_compact_mask_pod_runner_test tests.goal2999_triangle_counting_numba_compact_mask_wiring_test tests.goal2997_numba_compact_mask_l4_pod_test tests.goal2995_raydb_numba_minmax_l4_pod_test tests.goal2806_v2_5_internal_readiness_packet_test
```

If shell execution is not available, disclose that clearly and perform a static/artifact review.

## Required Boundary

The review must not authorize release, public speedup wording, whole-app speedup wording, broad RT-core speedup wording, true-zero-copy wording, automatic partner selection, or app-specific native-engine logic.
