# Goal 1488: v1.5.4 CUDA Evidence Boundary Gate

## Verdict

Accepted as the v1.5.4 boundary gate for the current Python+RTDL managed-buffer CUDA evidence.

This gate encodes the distinction between Goal 1486 allocation-only evidence and Goal 1487 explicit content-copy evidence.

## Accepted Evidence

Goal 1486 proves:

- RTDL-owned CUDA Driver API allocation/free can run on real NVIDIA hardware.
- `cuMemAlloc_v2` returned a nonzero device pointer.
- `cuMemFree_v2` succeeded.
- allocation-only host/device transfer counts were `0/0`.
- this can be marked as candidate-only evidence.

Goal 1487 proves:

- RTDL-shaped `int64` rows can be copied host-to-device and back through the CUDA Driver API.
- content roundtrip was verified.
- host/device transfer counts were `1/1`.
- explicit Python-origin content movement is not true-zero-copy evidence.

## Not Proven

This gate explicitly does not prove:

- end-to-end RTDL/OptiX device-buffer execution
- public true-zero-copy
- public speedup
- whole-application speedup
- partner tensor handoff
- release readiness

## Next Required Evidence

The next step needs an OptiX-ready environment or artifact flow that supplies:

- `librtdl_optix.so` or a build toolchain capable of producing it
- an RTDL backend entry that accepts an RTDL-owned device-memory descriptor
- same-contract parity against a host or Embree path
- transfer-count accounting around backend execution
- external AI review before any public claim wording

## Claim Boundary

This gate does not authorize:

- public true-zero-copy wording
- public speedup wording
- whole-application claims
- stable primitive promotion
- partner tensor handoff
- release action

## Files

- `src/rtdsl/v1_5_4_device_zero_copy_boundary.py`
- `src/rtdsl/__init__.py`
- `tests/goal1488_v1_5_4_cuda_evidence_boundary_gate_test.py`
- `docs/reports/goal1488_v1_5_4_cuda_evidence_boundary_gate_2026-05-07.md`

