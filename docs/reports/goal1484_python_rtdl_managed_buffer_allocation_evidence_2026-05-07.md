# Goal 1484: Python RTDL Managed Buffer Allocation Evidence Envelope

## Verdict

Accepted as a v1.5.4 evidence envelope for RTDL-owned managed-buffer allocation measurements.

This is still not a public zero-copy claim, not a public speedup claim, not a whole-application claim, not partner interop, and not a release action.

## Purpose

Goals 1481-1483 defined the Python+RTDL managed-buffer architecture, descriptors, and lifecycle bookkeeping. Goal 1484 adds the evidence shape that a real backend allocation path must fill before stronger claims can even be reviewed.

The envelope records:

- allocation method
- measurement backend
- measurement scope
- host-to-device transfer count
- device-to-host transfer count
- device residency observation
- real NVIDIA hardware flag
- hardware identity
- backend version

## Allocation Methods

Supported allocation-method labels are:

- `host_prepared`
- `host_pinned_staging`
- `cuda_device_alloc`
- `cuda_managed_alloc`
- `synthetic_contract_only`

Only `cuda_device_alloc` and `cuda_managed_alloc` can become true-zero-copy evidence candidates, and only when the descriptor is a device-residency candidate, residency is observed, both host/device transfer counts are zero, and the measurement is marked as real NVIDIA hardware.

## Claim Boundary

The envelope may set `true_zero_copy_evidence_candidate=True` for a narrow measured candidate, but it keeps these authorization flags false:

- `managed_buffer_zero_copy_authorized`
- `true_zero_copy_authorized`
- `public_speedup_wording_authorized`
- `whole_app_speedup_claim_authorized`
- `stable_public_primitive_authorized`
- `partner_tensor_handoff_authorized`
- `release_action_authorized`

This keeps the distinction between evidence collection and accepted public wording.

## Pod Status

No pod is required for this goal because it only defines and validates the evidence envelope.

A pod will be needed for the next step that attempts real OptiX/CUDA allocation evidence, because that step must record actual NVIDIA hardware identity, residency behavior, and transfer counts.

## Files

- `src/rtdsl/v1_5_4_device_zero_copy_boundary.py`
- `src/rtdsl/__init__.py`
- `tests/goal1484_python_rtdl_managed_buffer_allocation_evidence_test.py`
- `docs/reports/goal1484_python_rtdl_managed_buffer_allocation_evidence_2026-05-07.md`

## Validation

Expected focused validation:

```bash
PYTHONPATH=src:. python -m unittest tests.goal1484_python_rtdl_managed_buffer_allocation_evidence_test tests.goal1483_python_rtdl_managed_buffer_lifecycle_test tests.goal1482_python_rtdl_managed_buffer_descriptor_test
```

Expected broader validation:

```bash
PYTHONPATH=src:. python -m unittest tests.goal1484_python_rtdl_managed_buffer_allocation_evidence_test tests.goal1483_python_rtdl_managed_buffer_lifecycle_test tests.goal1482_python_rtdl_managed_buffer_descriptor_test tests.goal1481_python_rtdl_managed_buffer_design_gate_test tests.goal1480_gpu_memory_architecture_gate_test tests.goal1479_gpu_memory_architecture_consensus_test tests.goal1478_v1_5_4_device_memory_measurement_envelope_test tests.goal1477_v1_5_4_device_memory_descriptor_contract_test tests.goal1476_v1_5_4_device_zero_copy_entry_gate_test tests.goal1475_v1_5_3_post_consensus_checkpoint_gate_test tests.goal1473_v1_5_3_evidence_summary_test
```

## Next Work

The next practical step is pod-backed OptiX/CUDA evidence collection. That work should start from a clean `origin/main` checkout on a real NVIDIA machine, record the commit hash and hardware identity, then produce allocation evidence with exact transfer counts and residency observations.

