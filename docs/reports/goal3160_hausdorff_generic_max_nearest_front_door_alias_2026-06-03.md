# Goal3160: Hausdorff Generic Max-Nearest Front Door Alias

Date: 2026-06-03

Status: `implemented_with_compatibility_alias`

## Purpose

Goal3143 made the Hausdorff benchmark use the shared `partner_exact,
partner="numba"` path, but the Python adapter name was still
`directed_hausdorff_2d_partner_columns(...)`. That name is acceptable as a
compatibility alias, but it teaches the primitive as an app-specific Hausdorff
function rather than as the generic continuation it actually is:

1. compute nearest-target distance for each source point;
2. reduce those nearest distances with a directed max;
3. let the app interpret the result as directed Hausdorff when appropriate.

Goal3160 adds the generic front-door alias:

```python
rt.directed_max_of_nearest_distance_2d_partner_columns(...)
```

The old `rt.directed_hausdorff_2d_partner_columns(...)` API remains exported and
unchanged for compatibility.

## Implementation

- Added `directed_max_of_nearest_distance_2d_partner_columns(...)` in
  `src/rtdsl/partner_adapters.py`.
- Exported it from `rtdsl.__init__`.
- Updated the Hausdorff benchmark app's recommended `partner_exact` route to call
  the generic alias.
- Preserved the lower implementation and old metadata shape for callers that
  still use the Hausdorff-named compatibility function.
- The generic alias rewrites only adapter metadata:
  - `adapter: directed_max_of_nearest_distance_2d_partner_columns`
  - `partner_reference_contract: generic_directed_max_of_nearest_distance_2d`
  - `compatibility_adapter_aliases: ("directed_hausdorff_2d_partner_columns",)`
  - `semantic_aliases: ("directed_hausdorff_2d",)`

## Boundary

This is a Python front-door and metadata cleanup. It does not change native code,
Numba kernels, CuPy/Torch/Triton execution, correctness semantics, timing, or
hardware behavior.

Claim flags remain blocked:

- `release_authorized: False`
- `v2_8_release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`
- `automatic_partner_selection_allowed: False`
- `app_specific_engine_logic_allowed: False`

## Validation

Focused validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3160_hausdorff_generic_max_nearest_front_door_alias_test
ss...
----------------------------------------------------------------------
Ran 5 tests in 0.020s

OK (skipped=2)
```

Compatibility validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal3160_hausdorff_generic_max_nearest_front_door_alias_test \
  tests.goal3143_hausdorff_partner_exact_numba_front_door_test \
  tests.goal3150_hausdorff_release_boundary_key_normalization_test \
  tests.goal1975_exact_hausdorff_partner_reference_test \
  tests.goal2044_partner_continuation_numpy_reference_test \
  tests.goal2046_cupy_witness_continuation_surface_test
ss...ss.................s..
----------------------------------------------------------------------
Ran 27 tests in 2.064s

OK (skipped=5)
```

The pod validation should rerun the focused test and Goal3143 compatibility
test from a clean `origin/main` checkout, including the executable Numba CUDA
cases that skip on local Windows.
