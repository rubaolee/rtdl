# Goal1309 Claude Review Request

Date: 2026-05-05

Please review the current uncommitted Goal1309 polygon-pair generic area-summary slice plus the already committed Goal1308 float-sum contract.

Files to inspect:

- `src/rtdsl/float_reduction_contracts.py`
- `tests/goal1308_v1_5_polygon_float_sum_contract_test.py`
- `docs/reports/goal1308_v1_5_polygon_float_sum_contract_2026-05-05.md`
- `src/rtdsl/generic_polygon_primitives.py`
- `examples/rtdl_polygon_pair_overlap_area_rows.py`
- `tests/goal1309_v1_5_polygon_pair_generic_area_summary_test.py`
- `docs/reports/goal1309_v1_5_polygon_pair_generic_area_summary_2026-05-05.md`

Context:

- v1.5 active backend scope is Embree and OptiX only.
- Vulkan, HIPRT, and Apple RT are frozen before v2.1.
- Stable primitive set must remain bounded: `ANY_HIT`, `COUNT_HITS`, `REDUCE_FLOAT(MIN|MAX|SUM)`, `REDUCE_INT(COUNT|SUM)`.
- `COLLECT_K_BOUNDED` remains experimental.
- Public NVIDIA speedup wording is not authorized by this work.
- Polygon-pair current workload is integer-grid unit-cell area, so exact integer parity remains required before future float tolerance applies.

Review questions:

1. Does Goal1308 correctly define `REDUCE_FLOAT(SUM)` without overclaiming implementation or public wording?
2. Does Goal1309 correctly wrap polygon-pair summary as a generic `REDUCE_FLOAT(SUM)` metadata path while preserving the exact integer oracle boundary?
3. Are there any blockers before pod validation and inventory promotion?

Please write your review to:

`docs/reports/goal1309_claude_review_2026-05-05.md`

Use `ACCEPT` only if there are no blocking issues. If blocked, include precise findings and required fixes.
