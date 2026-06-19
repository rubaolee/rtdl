# RTDL V4.0 Pre-M8 Boundary

Status: superseded pre-M8 boundary stub, not a release approval.
Date: 2026-06-19.

This note records the ordering decision that preceded the M8 packet. It is now
superseded by:

`docs/engineering/rtdl_v4_0_m8_release_candidate_packet_2026-06-19.md`

Neither this note nor the M8 packet authorizes release approval, front-door
switch, package promise, speedup claim, async claim, or true-zero-copy claim.

## Current Position

The current user release remains `v3.0.2`.

V4.0 has experimental M1 evidence for the fixed-radius Python device-array
operator route, including CuPy, bounded Numba `DeviceNDArray`, narrow legacy
DLPack capsule intake, PyTorch CUDA tensors with a compatibility matrix,
caller-stream propagation, same-stream ordering, narrow fixed-radius
prepare/query event-wait ordering across distinct streams, and Linux
source-tree runtime preflight with CuPy, Numba, PyTorch, and OptiX.

V4.0 remains blocked from current-release/front-door promotion until the M8
packet receives external review and the remaining release gates are either
closed or explicitly excluded from V4.0 release scope.

## Next Work Order

1. Keep the M1 route reproducible.
2. Use the M8 packet as the critical-review input.
3. Close or explicitly scope-exclude package/runtime, front-door, speed,
   true-zero-copy, async, full partner-surface, and SDK claims before any
   release action.
4. Refresh blockers only for exact passing evidence.
5. Move V4 to a current user front door only after external review and explicit
   user release authorization.

## Not Yet Authorized

- V4.0 current release/front-door wording;
- stable SDK, PyPI, wheel, generated bindings, or public multi-language C ABI;
- full DLPack support or arbitrary DLPack capsule support;
- PyTorch support beyond the exact fixed-radius M1 route evidence;
- full Numba partner surface;
- public true-zero-copy or no-copy wording;
- async/nonblocking completion;
- RT-core, RTX, or public speedup wording;
- general cross-stream event-wait or public event-handle ownership.

## Governing Decision Record

`docs/reviews/codex_v4_next_step_pre_m8_dlpack_3ai_consensus_2026-06-19.md`

Superseding M8 decision record:

`docs/reviews/codex_v4_after_runtime_preflight_m8_next_step_2ai_consensus_2026-06-19.md`
