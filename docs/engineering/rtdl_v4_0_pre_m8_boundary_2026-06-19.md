# RTDL V4.0 Pre-M8 Boundary

Status: pre-M8 boundary stub, not a release-candidate packet.
Date: 2026-06-19.

This note records the current V4.0 ordering decision. It must not be read as an
M8 release-candidate packet, release approval, front-door switch, package
promise, speedup claim, async claim, or true-zero-copy claim.

## Current Position

The current user release remains `v3.0.2`.

V4.0 has experimental M1 evidence for the fixed-radius Python device-array
operator route, including CuPy, bounded Numba `DeviceNDArray`, caller-stream
propagation, same-stream ordering, and narrow fixed-radius prepare/query
event-wait ordering across distinct streams.

V4.0 is still blocked before M8 because the Python GPU ecosystem headline is
not complete without real DLPack/PyTorch/lifetime evidence.

## Next Work Order

1. Keep the M1 route reproducible.
2. Implement the fixed-radius M1 DLPack capsule/lifetime contract.
3. Use that contract to pursue exact PyTorch CUDA tensor route evidence.
4. Refresh blockers only for exact passing evidence.
5. Draft M8 only after DLPack/PyTorch/lifetime gates are either closed or
   explicitly removed from V4.0 scope.

## Not Yet Authorized

- `v4_release_candidate` test-matrix gate;
- V4.0 current release/front-door wording;
- stable SDK, PyPI, wheel, generated bindings, or public multi-language C ABI;
- full DLPack support or arbitrary DLPack capsule support;
- PyTorch route support;
- full Numba partner surface;
- public true-zero-copy or no-copy wording;
- async/nonblocking completion;
- RT-core, RTX, or public speedup wording;
- general cross-stream event-wait or public event-handle ownership.

## Governing Decision Record

`docs/reviews/codex_v4_next_step_pre_m8_dlpack_3ai_consensus_2026-06-19.md`
