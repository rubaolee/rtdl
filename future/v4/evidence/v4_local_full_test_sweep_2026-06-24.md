# V4 Local Full Test Sweep

Date: 2026-06-24

Status: passed

Latest rerun:

- time: 2026-06-24 14:07 -04:00
- base runtime commit under test: `c9586813b5769d9bff32d7974063b594c04a8997`
- working-tree delta under test:
  - `future/v4/evidence/v4_final_release_scope_catalog_gate_gpu_32768_2026-06-24.json`
  - `future/v4/evidence/v4_final_release_scope_catalog_gate_gpu_2026-06-24.json`
  - `future/v4/v4_0_release_candidate_packet_2026-06-24.md`
- reason: revalidated after Claude release-candidate amendments; targeted
  packet/gate tests also passed after the latest POD evidence refresh

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

Note: local Python emitted the known `Could not find platform independent libraries <prefix>` warning, but all tests passed.

## Non-Authorization

This test sweep does not authorize V4 release, broad V4 speedup wording,
whole-application speedup wording, Tier-3 callback/PTX support claims, raw OptiX
callback support, CuPy performance claims, embedding/C-ABI claims, non-Python
host binding claims, or app-specific native engine kernels.
