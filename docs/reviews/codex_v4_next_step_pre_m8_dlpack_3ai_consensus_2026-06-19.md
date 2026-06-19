# RTDL V4 Next-Step Consensus: Pre-M8 Boundary, Then DLPack Lease

Status: accepted engineering-order decision.
Date: 2026-06-19.

## Question

After the fixed-radius M1 CuPy/Numba route, same-stream ordering, and narrow
cross-stream prepare/query event-wait evidence, should the next V4 work be:

- a PyTorch CUDA tensor route;
- full DLPack capsule/lifetime support;
- broader Numba partner-surface work;
- or an M8 release-candidate packet?

## Reviewer Positions

Product/scope reviewer: draft an M8-style packet first to consolidate current
evidence and prevent accidental overclaiming.

Implementation/risk reviewer: build the real DLPack capsule/lifetime contract
first, because PyTorch would otherwise rest on an undefined ownership bridge.

Tie-breaker: use a narrow hybrid. Add a small pre-M8 boundary note, explicitly
not a release-candidate packet, then implement the fixed-radius M1 DLPack
capsule/lifetime contract before PyTorch route evidence.

## Decision

Adopt the narrow hybrid:

1. Record a pre-M8 boundary stub that says V4 is not release-candidate ready.
2. Implement a narrow DLPack capsule/lifetime contract for
   `fixed_radius_count_threshold_2d`.
3. Use that contract as the prerequisite for PyTorch CUDA tensor evidence.
4. Refresh the blocker manifest only for exact evidence that passes.
5. Draft M8 only after DLPack/PyTorch/lifetime gates are either closed or
   explicitly removed from V4.0 scope.

## Required DLPack Gates

- real `__dlpack__` capsule intake, not a wrapper-provided `data_ptr`;
- explicit legacy/versioned capsule policy;
- consume-once and deleter-once tests;
- producer lifetime retained or fail-closed;
- CUDA, dtype, rank, stride, device, mutability, and mixed-device checks;
- synchronous stream semantics documented and tested;
- Linux evidence with `make build-optix`, `v4_active`, DLPack probe, claim
  scan, JSON validation, `git diff --check`, and clean worktree.

## Claims That Stay Blocked

- V4.0 current release/front door;
- stable SDK, PyPI, wheel, generated bindings, public multi-language C ABI;
- public true zero-copy, end-to-end zero-copy, no copies, no staging;
- async or nonblocking completion;
- RT-core/RTX speedup or broad performance claims;
- full DLPack support or arbitrary framework-neutral DLPack support;
- PyTorch support beyond exact proven route evidence;
- full Numba partner surface;
- general cross-stream event-wait or public event-handle ownership.
