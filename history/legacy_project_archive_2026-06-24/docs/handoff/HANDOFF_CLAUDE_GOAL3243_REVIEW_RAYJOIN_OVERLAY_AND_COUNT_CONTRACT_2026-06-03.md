# Handoff: Goal3243 Claude Review Of RayJoin Overlay And Count-Contract Work

Please perform a read-only independent Claude review of the latest RayJoin evidence chain after Goal3240.

## Files To Read

- `docs/reports/goal3241_rayjoin_overlay_rt_failure_isolation_2026-06-03.md`
- `tests/goal3241_rayjoin_overlay_rt_failure_isolation_test.py`
- `docs/reports/goal3242_rtdl_rayjoin_count_contract_probe_2026-06-03.md`
- `docs/reports/goal3242_rtdl_rayjoin_count_contract_probe_2026-06-03.json`
- `tests/goal3242_rtdl_rayjoin_count_contract_probe_test.py`
- For context only: `docs/reports/goal3239_rayjoin_upstream_build_and_same_slice_smoke_2026-06-03.md`
- For context only: `docs/reviews/goal3240_claude_review_rayjoin_upstream_build_smoke_2026-06-03.md`

## Review Questions

1. Does Goal3241 honestly isolate the RayJoin overlay RT blocker without overgeneralizing it into a RayJoin/RTDL failure?
2. Does Goal3242 choose the correct fair current comparison contract for RayJoin `query_exec` LSI/PIP, namely RTDL `prepared_optix` count rather than row materialization or compact grouped-count routes?
3. Are the measured counts and ratios stated correctly: LSI RTDL count 269 vs RayJoin RT 269, RTDL prepared count phase 1.537 ms vs RayJoin RT query 0.229 ms, PIP RTDL count 1430 with RayJoin count unavailable, RTDL 1.268 ms vs RayJoin RT 0.186 ms?
4. Is it appropriate that compact grouped-count and left-id dense routes are preserved as useful larger-scale/reuse contracts but not treated as the current small-slice timing denominator?
5. Are all release/public speedup/RTDL-beats-RayJoin/RayJoin-paper-reproduction/true-zero-copy claims still blocked?
6. What should be the highest-value next engineering step: RayJoin PIP count extraction, repeated same-slice median runner, RTDL prepared-count gap investigation, or something else?

## Output

Write the review to:

`docs/reviews/goal3243_claude_review_rayjoin_overlay_and_count_contract_2026-06-03.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Keep the review grounded in repository files. Do not edit RTDL source code. If you run tests, record the command and result in the review.
