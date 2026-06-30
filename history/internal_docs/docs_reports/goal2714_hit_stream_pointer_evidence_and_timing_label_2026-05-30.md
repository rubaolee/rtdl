# Goal2714 - Hit-Stream Pointer Evidence And Timing Label Fix

Date: 2026-05-30

Status: implemented locally; pod rerun required for refreshed evidence.

## Purpose

The first Goal2712 pod run completed and produced correct RayDB results, but it
showed two evidence-quality gaps:

1. The RayDB device-column path reported native traversal under
   `hit_stream_rt_traversal`, while the v2.4 phase metadata looked only for
   `traversal`, so `rt_traversal` in the phase table could be incorrectly
   recorded as `0.0`.
2. The artifact showed that a CUDA-array-interface adapter was selected, but it
   did not record whether the torch carrier preserved the native hit-column
   pointer.

## Changes

- `gather_typed_payload_columns_for_hit_stream(...)` now records
  `torch_carrier_execution` metadata when the Triton/Torch carrier path runs.
- The execution metadata includes input and carrier `data_ptr` values for:
  - `primitive_ids`;
  - `primitive_group_ids`;
  - `primitive_values`.
- It records per-column same-pointer booleans and
  `same_pointer_evidence_observed`.
- It still keeps:
  - `adapter_execution_proven_on_hardware = False`;
  - `true_zero_copy_authorized = False`;
  - `public_speedup_claim_authorized = False`.
- The RayDB v2.5 phase metadata now reads `traversal` or `rt_traversal`, fixing
  the device-column timing label.

## Validation

Windows focused validation:

```text
py -3 -m unittest \
  tests.goal2710_raydb_native_device_hit_stream_path_test \
  tests.goal2708_hit_stream_cuda_array_torch_carrier_adapter_test \
  tests.goal2706_native_optix_hit_stream_device_columns_test \
  tests.goal2704_native_hit_stream_output_abi_contract_test \
  tests.goal2703_neutral_buffer_lease_state_machine_test \
  tests.goal2702_raydb_explicit_partner_planner_integration_test \
  tests.goal2700_explicit_hit_stream_gather_partner_test \
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

Ran 106 tests in 7.979s
OK (skipped=5)
```

## Boundary

This goal improves evidence fidelity. It does not change the public claim state:
same-pointer metadata is evidence to review, not an automatic true-zero-copy
claim.
