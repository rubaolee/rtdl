# Call For Review: V4 Third Tier-2 Device-Array Surface And Operator Catalog

Date: 2026-06-24
Requested verdict labels:

- `accept_continue_v4_engineering`
- `accept_with_required_amendments`
- `blocked_requires_rework`
- `reject_stop_this_path`

## Scope To Review

This review covers the third measured V4 Tier-2 surface and the first V4
Tier-2 operator catalog. It does not request V4 release authorization.

Changed files:

- `src/rtdsl/v4_ray_triangle.py`
- `future/v4/examples/ray_triangle_any_hit_flags_torch_device_arrays.py`
- `scripts/v4_section8_any_hit_flags_device_frontdoor_validation.py`
- `tests/v4_ray_triangle_device_array_api_test.py`
- `tests/v4_fixed_radius_docs_and_example_test.py`
- `tests/v4_section8_any_hit_flags_device_frontdoor_validation_test.py`
- `future/v4/ray_triangle_device_array_frontdoor.md`
- `future/v4/tier2_operator_catalog.md`
- `future/v4/evidence/v4_section8_any_hit_flags_device_frontdoor_result_2026-06-24.json`
- `future/v4/evidence/v4_section8_any_hit_flags_device_frontdoor_report_2026-06-24.md`
- `future/v4/evidence/v4_any_hit_flags_torch_device_arrays_example_result_2026-06-24.json`

## What Was Implemented

Added `v4_ray_triangle_any_hit_flags_2d_device_arrays`, a V4 Tier-2 device-array
front door over the existing generic OptiX 2-D ray/triangle any-hit flag native
ABI:

- caller-owned Torch CUDA triangle columns and triangle AABBs
- caller-owned Torch CUDA ray columns
- caller-owned or RTDL-allocated Torch CUDA `uint32` output flags
- no Python ray-row result table in the hot path

Also added a development operator catalog listing the three currently measured
Torch CUDA Tier-2 surfaces:

- fixed-radius count-threshold
- closest-hit grouped-argmin
- ray/triangle any-hit flags

## Evidence

Local:

`python -m unittest tests.v4_ray_triangle_device_array_api_test tests.v4_fixed_radius_docs_and_example_test tests.v4_section8_any_hit_flags_device_frontdoor_validation_test tests.v4_section8_closest_hit_grouped_argmin_device_frontdoor_validation_test tests.v4_fixed_radius_device_array_api_test tests.v4_section8_device_array_frontdoor_validation_test`

Result: 22 tests passed.

POD:

`python -m unittest tests.v4_ray_triangle_device_array_api_test tests.v4_fixed_radius_docs_and_example_test tests.v4_section8_any_hit_flags_device_frontdoor_validation_test`

Result: 14 tests passed.

POD measurement:

`python scripts/v4_section8_any_hit_flags_device_frontdoor_validation.py --repeat 5 --warmup 1 --progress --json-out future/v4/evidence/v4_section8_any_hit_flags_device_frontdoor_result_2026-06-24.json`

Result summary:

- 8,192 rays/triangles: correctness passed, direct median 0.000261s
- 32,768 rays/triangles: correctness passed, direct median 0.000282s
- 131,072 rays/triangles: correctness passed, direct median 0.000288s
- 8,192 fixture-analytic Torch reference median 0.002446s, ratio 9.379x

The Torch reference is explicitly scoped as a fixture-analytic same-data device
reference, not a handwritten OptiX ceiling and not a broad speedup basis.

POD example:

`python future/v4/examples/ray_triangle_any_hit_flags_torch_device_arrays.py --ray-count 8192 --json-out future/v4/evidence/v4_any_hit_flags_torch_device_arrays_example_result_2026-06-24.json`

Result: correctness passed.

## Questions

1. Is this a legitimate V4 Tier-2 generic operator surface, not an app-specific kernel?
2. Does the implementation preserve the V4 product boundary: Python GPU arrays in, RTDL generic RT operator, GPU arrays out?
3. Are the claim boundaries clear enough to prevent release, broad speedup, whole-app speedup, Tier-3, and CuPy overclaims?
4. Is the 8K Torch reference ratio honestly scoped, or should it be removed/rewritten?
5. Is the operator catalog useful and honest, or does it overstate V4 readiness?
6. What amendments are required before continuing to the next V4 engineering goal?

## Non-Authorization

This review must not authorize:

- V4 release
- broad V4 speedup wording
- whole-application speedup wording
- Tier-3 callback/PTX claims
- CuPy performance claims
- embedding/C-ABI work
- app-specific native engine kernels

