# Handoff: Gemini Review for Goal3012-Goal3013

Please perform an independent read-only review of the current RTDL main branch
for the Goal3012-Goal3013 Hausdorff Numba score-row work.

## Files to inspect

- `src/rtdsl/numba_partner_continuation.py`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/v2_6_roadmap.py`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`
- `docs/reports/goal3012_numba_pairwise_score_rows_for_hausdorff_2026-06-01.md`
- `docs/reports/goal3013_hausdorff_numba_device_score_rows_l4_pod_2026-06-01.md`
- `docs/reports/goal3013_hausdorff_numba_device_score_rows_l4_pod_2026-06-01.json`
- `tests/goal3012_numba_pairwise_score_rows_for_hausdorff_test.py`
- `tests/goal3013_hausdorff_numba_device_score_rows_pod_runner_test.py`

## Questions to answer

1. Is `pairwise_l2_sq_score_rows_2d` generic enough for the RTDL partner layer,
   without adding Hausdorff/app semantics to the native engine?
2. Does the Hausdorff app compose generic score rows and generic grouped witness
   reduction correctly while preserving oracle parity?
3. Does Goal3013 provide credible clean L4 evidence: clean commit, GPU/driver,
   warmup/evidence runs, 1024x1024 directed score-row scale, and all claim
   flags false?
4. Does any code/report/artifact overclaim v2.6 release readiness, speedup,
   RT-core acceleration, whole-app acceleration, true zero-copy, automatic
   partner selection, or app-specific native-engine logic?
5. What should be fixed before this path becomes a recommended Hausdorff
   benchmark implementation?

## Output

Write the review to:

`docs/reviews/goal3014_gemini_review_goal3012_3013_numba_hausdorff_score_rows_2026-06-01.md`

Use one of these verdict values only:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Do not edit source files. If you run tests, record the exact command and result.
