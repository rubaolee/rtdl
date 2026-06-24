# Call For Review: Phoenix V3 M42 Grouped-Reduction Grid Occupancy Root Cause

Date: 2026-06-23

Requested verdict labels:

- `accept_m42_shape_positive_continue_with_envelope`
- `accept_m42_shape_positive_require_tiled_kernel`
- `revise_m42_instrumentation_or_interpretation`
- `reject_m42_not_step2_evidence`

Please review:

- `docs/reports/phoenix_v3_m42_grouped_reduction_grid_occupancy_root_cause_2026-06-23.md`
- `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m42_lx1_shape_262144x65536_20260623_151852/summary.json`
- `scripts/v3_phoenix_grouped_reduction_m41_local_harness.py`
- `src/rtdsl/numba_partner_continuation.py`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/prepared_execution.py`

Review questions:

1. Is the root-cause diagnosis correct: the current offsets kernel parallelizes over `group_count`, so the M41 `1024`-group shape launched only `4` blocks?
2. Is the correction to the earlier speculative shapes correct: increasing `row_count` at fixed `group_count=1024` would not improve occupancy, and reducing `group_count` to `64` would worsen it?
3. Does the M42 free-local shape experiment (`262144` rows, `65536` groups) validly test the launch-shape hypothesis?
4. Does the M42 result close grouped reduction as a shape-positive second Step-2 family, or should it be treated only as a prompt to build a tiled/row-parallel generic kernel?
5. Are the new launch-shape metadata fields sufficient and placed in the right layer?
6. Does any wording overclaim performance, release readiness, all-app readiness, paid-POD authorization, V4, embedding, or true zero-copy?
7. What exact next step should be authorized: external-review-only closure, one local tiled-kernel implementation, one additional free local envelope run, or family switch?

Non-authorization to preserve:

- no release
- no all-app
- no paid POD
- no public speedup wording
- no broad V3-over-V2 claim
- no V4
- no embedding
- no C ABI
- no true zero-copy claim

