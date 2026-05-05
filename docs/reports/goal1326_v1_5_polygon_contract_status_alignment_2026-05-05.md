# Goal1326: v1.5 Polygon Contract Status Alignment

Date: 2026-05-05

## Scope

Align polygon pair and Jaccard primitive contract metadata with the already
verified Goal1321 and Goal1322 inventory state.

## Changes

- `polygon_pair_overlap_area_rows` summary-mode area reduction is now marked
  `pod_verified_generic_non_public` instead of deferred.
- Polygon-pair summary-mode contract now names the backend-neutral native
  polygon-pair area summary continuation.
- `polygon_set_jaccard` score reduction is now marked
  `pod_verified_generic_non_public` instead of blocked by native score
  reduction.
- Jaccard remains diagnostic and non-public because OptiX remains slower than
  Embree.

## Non-Goals

- No public speedup wording.
- No public v1.5 release authorization.
- No new Vulkan, HIPRT, or Apple RT implementation work.

## Validation

Targeted local gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1279_v1_4_polygon_pair_primitive_contract_test \
  tests.goal1280_v1_4_polygon_jaccard_diagnostic_contract_test \
  tests.goal1308_v1_5_polygon_float_sum_contract_test \
  tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test \
  tests.goal1320_v1_5_jaccard_generic_score_reduction_test \
  tests.goal1321_v1_5_native_polygon_pair_area_summary_abi_test

Ran 23 tests in 0.033s
OK
```
