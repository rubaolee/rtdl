# Internal Multihead Review Amendments: V4.0 Release Candidate

Date: 2026-06-24

Status: amendment record, not release authorization

## Reviewer Verdicts

- claim/scope reviewer: `approve_with_required_amendments`
- implementation/API reviewer: `approve_with_required_amendments`

## Required Amendments Applied

1. Public and machine non-authorization boundaries now include CuPy performance
   claims and non-Python host binding claims everywhere the V4.0 release
   candidate lists V4.x deferred work.
2. `src/rtdsl/v4_scope.py` now validates the full deferred-capability set and
   exposes explicit false flags for CuPy performance and non-Python host binding
   claims.
3. `src/rtdsl/v4.py` now exposes the same false flags through the unified front
   door.
4. `src/rtdsl/v4_fixed_radius.py` now fails closed for non-Torch partners in
   the V4.0 fixed-radius device-array API. CuPy remains V4.x, not a declared
   V4.0 execution surface.
5. `scripts/v4_catalog_regression_gate.py` now validates Tier-2 planner,
   scalar-callback Tier-3 deferral, and complex-callback rejection statuses.

## Local Verification

Command:

```bash
py -3 -m unittest \
  tests.v4_catalog_regression_gate_test \
  tests.v4_fixed_radius_device_array_api_test \
  tests.v4_fixed_radius_docs_and_example_test \
  tests.v4_frontdoor_test \
  tests.v4_operator_catalog_test \
  tests.v4_ray_triangle_device_array_api_test \
  tests.v4_release_candidate_packet_test \
  tests.v4_scope_gate_test \
  tests.v4_section8_any_hit_flags_device_frontdoor_validation_test \
  tests.v4_section8_closest_hit_grouped_argmin_device_frontdoor_validation_test \
  tests.v4_section8_device_array_frontdoor_validation_test \
  tests.v4_section8_fixed_radius_count_threshold_validation_test \
  tests.v4_section8_route_d_reference_validation_test \
  tests.v4_tier3_numba_ptx_probe_test \
  tests.v4_tier3_optix_module_link_probe_test
```

Result:

- modules: 15
- tests: 55
- status: OK

## Non-Authorization

This amendment record does not authorize V4 release, broad V4 speedup wording,
whole-application speedup wording, Tier-3 callback/PTX support claims, raw OptiX
callback support, CuPy performance claims, embedding/C-ABI claims, non-Python
host binding claims, or app-specific native engine kernels.
