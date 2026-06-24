# Call For Review: V4 Section 8 Device-Array Front Door

Date: 2026-06-24
Requested verdict labels:

- `accept_device_array_frontdoor_product_boundary_cleared_continue_api`
- `accept_with_amendments`
- `reject_measurement_or_claim`
- `blocked_needs_more_evidence`

## Context

Route D established an independent hand-written OptiX ceiling for the
fixed-radius count-threshold contract. That review found a large product-boundary
gap: the current Python-facing RTDL prepared routes were hundreds of times
slower than Route D. The required next step was not a second primitive; it was
to build and measure a GPU array/device-array front door for the same primitive.

This packet asks you to review that next step.

## Files To Read

Primary:

- `future/v4/evidence/v4_section8_device_array_frontdoor_report_2026-06-24.md`
- `future/v4/evidence/v4_section8_device_array_frontdoor_result_2026-06-24.json`
- `src/rtdsl/v4_fixed_radius.py`
- `scripts/v4_section8_device_array_frontdoor_validation.py`
- `tests/v4_fixed_radius_device_array_api_test.py`
- `tests/v4_section8_device_array_frontdoor_validation_test.py`

Baselines:

- `future/v4/evidence/v4_section8_route_d_handwritten_optix_ceiling_report_2026-06-24.md`
- `future/v4/evidence/v4_section8_route_d_result_2026-06-24.json`
- `future/v4/evidence/v4_section8_prepared_hot_path_result_2026-06-24.json`
- `future/v4/reviews/claude_v4_section8_route_d_handwritten_optix_ceiling_review_2026-06-24.md`

Code path under review:

- `src/rtdsl/partner_adapters.py`
  - `prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene`
  - `allocate_fixed_radius_count_threshold_2d_partner_device_output_columns`
  - `fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns`
- `src/rtdsl/optix_runtime.py`
  - `PreparedOptixFixedRadiusCountThreshold2D.write_device_count_threshold_columns`
  - `prepare_optix_fixed_radius_count_threshold_2d_device_search_columns`
  - `pack_optix_fixed_radius_count_threshold_2d_device_point_inputs`

## Result Under Review

The new harness measures Torch CUDA device columns through the
`rtdsl.v4_fixed_radius` wrapper as the product front door. It excludes fixture
construction, Torch tensor construction, prepare, and correctness host
reductions. It includes the prepared RTDL device-column query, native OptiX
launch, synchronization, and output writes into reused Torch CUDA columns.

Results:

| copies | points | device-array median | prior summary median | Route D rows median | device-array / Route D rows | gap reduction |
|---:|---:|---:|---:|---:|---:|---:|
| 8,192 | 65,536 | 0.000278s | 0.284516s | 0.000629s | 0.44x | 1022.93x |
| 32,768 | 262,144 | 0.000311s | 1.193533s | 0.001542s | 0.20x | 3841.66x |
| 131,072 | 1,048,576 | 0.000546s | 5.290915s | 0.004641s | 0.12x | 9699.17x |

Correctness passed on all sizes.

The device-array route being faster than Route D rows is not claimed as a pure
kernel win. Route D rows include host query upload and host result download;
the new product front door uses already-resident device input columns and leaves
outputs on device.

## Questions For Review

1. Is this measurement boundary valid for the V4 Python GPU ecosystem
   device-array front door?
2. Does the evidence support saying the fixed-radius product-boundary blocker
   is cleared for GPU-resident Torch columns?
3. Are the correctness checks sufficient for this focused primitive gate?
4. Is the comparison against Route D rows honest, given Route D includes host
   upload/download and this route is GPU-resident?
5. Does this evidence justify continuing to productize the fixed-radius V4 API
   wrapper before adding a second primitive?
6. Does any wording in the report overclaim V4 release, broad speedups, Tier 3
   callbacks, or whole-app performance?
7. What amendments are required before this can be used as the next V4 baseline?

## Non-Authorization

Do not authorize:

- V4 release
- broad V4 speedup wording
- whole-application speedup wording
- Tier 3 callback/PTX claims
- app-specific native engine claims
- claims that every future primitive will match this result
- claims that the old Python point-row app route is now fast

The requested authorization is only whether V4 may continue by productizing the
fixed-radius GPU-array front door as the first Tier 2 public primitive surface.
