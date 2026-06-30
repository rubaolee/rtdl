# Goal 1482: Python RTDL Managed Buffer Descriptor

## Verdict

Accepted as a v1.5.4 design-level descriptor contract for Python+RTDL managed buffers.

This does not claim zero-copy, GPU-resident speedup, partner tensor interop, public primitive stability, release readiness, or whole-application acceleration. It records the metadata boundary needed before real allocation, residency measurement, and NVIDIA RT-core validation.

## Scope

The descriptor is for the Python+RTDL roadmap track where RTDL owns the managed buffer boundary. It is intentionally different from the later Python+partner+RTDL track, where partner runtimes own GPU memory and RTDL must attach to externally managed descriptors.

Supported RTDL-owned buffer kinds are:

- `prepared_host`
- `pinned_host_staging`
- `rtdl_device_resident`
- `rtdl_managed_unified`

Required descriptor metadata includes:

- buffer kind
- backend
- device
- dtype
- shape
- owner
- lifetime
- copy boundary
- residency state
- transfer-count state

## Semantics

`prepared_host` and `pinned_host_staging` remain CPU-side reduced-copy buffers. They must use `device="cpu"` and `residency_state="host_resident"`.

`rtdl_device_resident` and `rtdl_managed_unified` are only unmeasured residency candidates. They require a non-CPU device and keep all zero-copy and speedup claims blocked until a real backend path records transfer counts, residency state, parity, and measured hardware evidence.

All descriptors must keep `owner="rtdl"` and `partner_owned=False`.

## Guardrails

The implementation rejects:

- host managed buffers placed on GPU devices
- device-resident candidates assigned to CPU devices
- unsupported dtype, shape, lifetime, residency state, or transfer-count state
- partner-owned descriptors in the Python+RTDL path
- any descriptor that enables zero-copy, public speedup, whole-app speedup, partner handoff, stable public primitive, or release claims

## Files

- `src/rtdsl/v1_5_4_device_zero_copy_boundary.py`
- `src/rtdsl/__init__.py`
- `tests/goal1482_python_rtdl_managed_buffer_descriptor_test.py`
- `docs/reports/goal1482_python_rtdl_managed_buffer_descriptor_2026-05-07.md`

## Validation

Expected validation command:

```bash
PYTHONPATH=src:. python -m unittest tests.goal1482_python_rtdl_managed_buffer_descriptor_test tests.goal1481_python_rtdl_managed_buffer_design_gate_test tests.goal1480_gpu_memory_architecture_gate_test tests.goal1478_v1_5_4_device_memory_measurement_envelope_test
```

Expected broader slice:

```bash
PYTHONPATH=src:. python -m unittest tests.goal1482_python_rtdl_managed_buffer_descriptor_test tests.goal1481_python_rtdl_managed_buffer_design_gate_test tests.goal1480_gpu_memory_architecture_gate_test tests.goal1479_gpu_memory_architecture_consensus_test tests.goal1478_v1_5_4_device_memory_measurement_envelope_test tests.goal1477_v1_5_4_device_memory_descriptor_contract_test tests.goal1476_v1_5_4_device_zero_copy_entry_gate_test tests.goal1475_v1_5_3_post_consensus_checkpoint_gate_test tests.goal1473_v1_5_3_evidence_summary_test
```

## Next Work

The next implementation step is to connect this descriptor contract to a real RTDL-owned allocation lifecycle:

- allocate or prepare the buffer
- record copy-boundary events
- measure transfer counts
- preserve parity
- collect backend evidence on real NVIDIA hardware only when the backend path is ready

