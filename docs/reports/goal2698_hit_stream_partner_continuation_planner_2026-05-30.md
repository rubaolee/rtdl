# Goal2698 Hit-Stream Partner Continuation Planner

Date: 2026-05-30
Status: local implementation; validation in progress
Depends on: Goal2692, Goal2694, Goal2696

## Purpose

Goal2698 adds the first plan/explain surface that combines:

- neutral buffer seam metadata from the hit-stream handoff;
- typed primitive payload seam metadata;
- the declared v2.5 partner support matrix.

This lets an app ask whether a hit-stream continuation can use a requested
partner for a requested operation before execution. Unsupported cells fail
closed, host staging is explicit, and pod-gated Triton plans remain clearly
bounded.

## What Changed

Added `plan_v2_5_hit_stream_partner_continuation(...)` in
`src/rtdsl/hit_stream_handoff.py`.

The planner returns:

| Field | Meaning |
| --- | --- |
| `support_cell` | The `plan_v2_5_partner_support(...)` row for the requested operation/partner. |
| `neutral_buffer_handoff_summary` | Hit-stream and payload transfer statuses from Goal2694. |
| `current_inputs_device_ready` | Whether all hit/payload seams are device-resident and not host-staged. |
| `current_inputs_satisfy_device_requirements` | Whether the requested partner's device requirements are satisfied by the current handoff. |
| `copy_or_host_stage_required` | Whether the plan requires an explicit copy or host-stage acknowledgement. |
| `fail_closed` | True when the support matrix marks the requested cell unsupported. |
| `runtime_action` | A concise next action, such as `plan_available`, `host_stage_or_copy_must_be_explicit`, `requires_sm70_pod_validation_before_performance_claim`, or `fail_closed_unsupported_partner_operation`. |

The planner is imported at `rtdsl` module scope for experimental use but is not
included in `rtdsl.__all__`.

## Behavior

| Scenario | Planner result |
| --- | --- |
| Reference continuation over host reference columns | Plan available, no copy claim, no speedup claim. |
| Host-row bridge requested for Triton | Supported operation, but current inputs do not satisfy CUDA/device requirements; explicit host-stage/copy action required. |
| CUDA-shaped hit/payload columns requested for Triton | Inputs are device-ready, but `sm_70+` pod validation is still required before performance wording. |
| Unsupported Numba operation such as `grouped_argmin_f64` | Fails closed through the support matrix. |

## Validation

Added `tests/goal2698_hit_stream_partner_continuation_plan_test.py`.

Initial Windows validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal2698_hit_stream_partner_continuation_plan_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2694_hit_stream_neutral_seam_metadata_test \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test
Ran 20 tests in 0.011s
OK
```

Windows focused v2.5 contract validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal2698_hit_stream_partner_continuation_plan_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2694_hit_stream_neutral_seam_metadata_test \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test \
  tests.goal2690_post_goal2689_contract_honesty_test \
  tests.goal2685_device_resident_hit_stream_handoff_test \
  tests.goal2644_raydb_paper_rt_contract_test \
  tests.goal2684_generic_rt_hit_stream_handoff_test \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2681_v2_5_triton_partner_adapter_front_door_test
Ran 77 tests in 7.483s
OK (skipped=5)

py -3 -m py_compile src\rtdsl\hit_stream_handoff.py \
  src\rtdsl\__init__.py tests\goal2698_hit_stream_partner_continuation_plan_test.py
OK
```

## Boundary

Goal2698 does not:

- execute the requested partner continuation;
- add native OptiX CUDA hit-column output;
- add new Triton/Numba/CuPy kernels;
- prove true zero-copy;
- prove performance;
- authorize release claims.

## Next Work

1. Run the expanded focused v2.5 suite on Windows and local Linux.
2. Use this planner in benchmark app code before partner execution paths.
3. On an `sm_70+` pod, collect real device-ready/pod-gated evidence for the
   first native OptiX CUDA hit-column implementation.
