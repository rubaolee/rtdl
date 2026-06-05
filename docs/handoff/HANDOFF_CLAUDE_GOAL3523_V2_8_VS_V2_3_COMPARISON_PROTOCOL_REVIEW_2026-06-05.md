# Claude Review Request: Goal3523 v2.8 vs v2.3 Same-Contract Comparison Protocol

Please perform a read-only review of the Goal3523 protocol and write your
review to:

`docs/reviews/goal3523_claude_review_v2_8_vs_v2_3_comparison_protocol_2026-06-05.md`

## Files To Review

- `src/rtdsl/v2_8_vs_v2_3_benchmark_comparison.py`
- `tests/goal3523_v2_8_vs_v2_3_same_contract_comparison_test.py`
- `docs/reports/goal3523_v2_8_vs_v2_3_same_contract_comparison_protocol_2026-06-05.md`
- Background evidence:
  - `docs/reports/goal2654_all_benchmark_app_perf_comparison_refresh_2026-05-27.md`
  - `docs/reports/goal3518_v2_8_benchmark_matrix_refresh_2026-06-05.md`
  - `docs/reports/goal3521_v2_8_final_validation_packet_2026-06-05.md`
  - `docs/release_reports/v2_3/README.md`

## Review Questions

1. Does the protocol correctly avoid producing a fake all-app v2.8/v2.3 ratio
   from non-identical contracts?
2. Are all 10 v2.8 benchmark apps represented, and is the v2.3 promotion
   boundary for `contact_manifold` stated correctly?
3. Are the two artifact-ratio rows (`rt_dbscan`, `triangle_counting`) bounded
   correctly, or should either be downgraded to fresh-pod-required?
4. Are the fresh-pod-required rows and their required next actions precise
   enough to guide a pod run?
5. Does the protocol preserve claim boundaries: no public release, public
   speedup, whole-app speedup, broad RT-core, package-install, true-zero-copy,
   paper-reproduction, hidden-partner, or app-specific-engine claims?

## Required Review Shape

- Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
  `reject`.
- Lead with findings, ordered by severity.
- State whether Goal3523 is ready for pod execution.
- Do not mutate source files.
