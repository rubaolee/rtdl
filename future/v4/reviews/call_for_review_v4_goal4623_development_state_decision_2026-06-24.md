# Call For Review: V4 `goal4623` Development-State Decision

Date: 2026-06-24
Requested verdict labels:

- `development_state_documentation_disclosure_not_release`
- `approve_with_required_amendments`
- `reject_goal4623_overclaims_or_insufficient_evidence`

Verdict: `development_state_documentation_disclosure_not_release`

## Review Request

Please critically review `goal4623`: final V4 catalog/readiness gate and
release-candidate or development-state decision.

Recommended decision:

- `development_state_documentation_disclosure_not_release`

This is intentionally not a V4 release and not a V4 release candidate. It says
the current V4 development front door is coherent enough to document as a
development state with measured/candidate labels, while release authorization
remains false.

## Current V4 Truth

Measured Torch CUDA Tier-2 surfaces:

1. `v4_fixed_radius_count_threshold_2d_device_arrays`
2. `v4_closest_hit_grouped_argmin_3d_device_arrays`
3. `v4_ray_triangle_any_hit_flags_2d_device_arrays`
4. `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
5. `v4_point_group_nearest_witness_2d_device_arrays`

Candidate Tier-2 surface:

1. `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`

Tier-3:

- protocol-only, not support
- scalar callback status: `tier3_spike_only_not_v4_0_release_surface`
- protocol status: `tier3_protocol_goal4622_spike_only_not_support`
- action-shaped status: `rejected_action_shaped_callback_deferred`

## Primary Artifacts

- Decision packet:
  `future/v4/v4_0_development_state_decision_packet_2026-06-24.md`
- Current V4 README:
  `future/v4/README.md`
- Scope gate:
  `future/v4/v4_0_scope_gate.md`
- Scope implementation:
  `src/rtdsl/v4_scope.py`
- Front door:
  `src/rtdsl/v4.py`
- Operator catalog:
  `src/rtdsl/v4_operator_catalog.py`
- Catalog regression gate:
  `scripts/v4_catalog_regression_gate.py`
- Tier-3 callback protocol:
  `future/v4/tier3_callback_spike_protocol_2026-06-24.md`

## Evidence

Local scope gate:

- `future/v4/evidence/v4_goal4623_scope_gate_current_2026-06-24.json`
- validation status: `passed`
- included measured surfaces: `5`
- candidate surfaces: `1`
- release authorized: `false`

Local catalog dry-run:

- `future/v4/evidence/v4_goal4623_final_catalog_dry_run_include_candidates_2026-06-24.json`
- `future/v4/evidence/v4_goal4623_final_catalog_dry_run_include_candidates_2026-06-24.md`
- status: `passed`
- examples: `10`
- release authorized: `false`

POD final GPU catalog gate:

- `future/v4/evidence/v4_goal4623_final_catalog_gpu_32768_include_candidates_2026-06-24.json`
- `future/v4/evidence/v4_goal4623_final_catalog_gpu_32768_include_candidates_2026-06-24.md`
- status: `passed`
- mode: `gpu`
- size: `32768`
- measured examples: `5/5` passed
- candidate examples: `1/1` passed as candidate
- planner examples: passed
- release authorized: `false`

Local tests:

```text
py -m unittest tests.v4_scope_gate_test tests.v4_release_candidate_packet_test tests.v4_frontdoor_test tests.v4_operator_catalog_test tests.v4_catalog_regression_gate_test tests.v4_tier3_callback_spike_protocol_test tests.v4_ray_triangle_device_array_api_test tests.v4_point_group_device_array_api_test tests.v4_point_group_nearest_witness_device_outputs_validation_test tests.v4_fixed_radius_docs_and_example_test
Ran 56 tests in 18.988s
OK
```

POD tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.v4_release_candidate_packet_test tests.v4_scope_gate_test tests.v4_frontdoor_test
Ran 11 tests in 1.454s
OK
```

Earlier `goal4622` POD tests:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_v4_candidate_pod/build/librtdl_optix.so RTDL_OPTIX_LIB=/root/rtdl_v4_candidate_pod/build/librtdl_optix.so python3 -m unittest tests.v4_operator_catalog_test tests.v4_tier3_numba_ptx_probe_test tests.v4_tier3_optix_module_link_probe_test tests.v4_tier3_callback_spike_protocol_test tests.v4_catalog_regression_gate_test tests.v4_frontdoor_test
Ran 27 tests in 7.343s
OK
```

## Questions For Review

1. Is the current V4 truth correctly represented as five measured Torch CUDA
   Tier-2 surfaces plus one candidate surface?
2. Does the final POD GPU catalog gate support development-state documentation
   disclosure?
3. Does anything in the packet overclaim release, release candidate, broad
   speedup, whole-app speedup, true zero-copy, Tier-3 callback support, raw
   OptiX callbacks, CuPy performance, C ABI/embedding, non-Python hosts, or
   app-specific native kernels?
4. Is the decision to stop at development-state documentation disclosure
   appropriate, given open review debt and missing release decision record?
5. What, if anything, must change before `goal4623` can be marked complete?

## Non-Authorization

This review and decision packet must not authorize:

- V4 release
- V4 release-candidate status
- broad V4 speedup wording
- whole-application speedup wording
- public true-zero-copy wording
- Tier-3 callback support
- raw OptiX callback support
- CuPy performance claims
- C ABI / embedding / non-Python-host work
- app-specific native kernels
