# V4 After Runtime Preflight: M8 Next-Step 2-AI Consensus

Date: 2026-06-19
Status: accepted next-step decision, not release approval.

## Current State

V4.0 remains an experimental Python GPU RT-core operator track. Current
evidence covers the fixed-radius M1 route with:

- CuPy CUDA arrays;
- Numba `DeviceNDArray`;
- narrow legacy DLPack capsule intake;
- PyTorch CUDA tensors with a compatibility matrix;
- same-stream ordering and fixed-radius prepare/query event-wait evidence;
- Linux source-tree runtime preflight with CuPy, Numba, PyTorch, and OptiX;
- `v4_active`: 71 tests, passing.

The current user release remains `v3.0.2`.

## Reviewer Positions

Aristotle, from the release-gate view, ranked:

1. M8 release-candidate packet.
2. External critical review against that packet.
3. Package/runtime story closure or explicit source-tree-only decision.

Chandrasekhar, from the engineering closure view, ranked:

1. M8 release-candidate gate/packet.
2. Package/runtime story closure.
3. Public contract freeze for the narrow `fixed_radius_count_threshold_2d`
   Python route.

Both reviewers warned against broad feature expansion before the release packet:
do not chase full PyTorch, full DLPack, full async, public true-zero-copy,
public speedup, or public multi-language SDK work as the next step.

## Decision

Proceed with the M8 release-candidate evidence packet and non-authorizing gate.

The packet should assemble what V4.0 currently is:

- Python GPU operator direction, not C ABI product headline;
- exact fixed-radius M1 route;
- supported and rejected Python device-array cases;
- stream and lifetime boundaries;
- source-tree runtime evidence;
- claim-boundary scan;
- machine-readable blocker manifest;
- validation commands;
- explicit list of claims that remain blocked.

The packet must not switch the front door or present V4 as the current release.

## Non-Goals For This Cut

This decision does not authorize:

- current-release or user-front-door wording for V4.0;
- public speedup or RTX/RT-core advantage claims;
- public true-zero-copy or async/nonblocking wording;
- full PyTorch, full Numba, or framework-neutral full DLPack support;
- PyPI, wheel, package-install, stable SDK, or generated binding claims;
- public multi-language C ABI or non-Python host support.

## Required Next Evidence

After the M8 packet is written, the next external review request should ask
whether the packet is honest, reproducible, useful, and scoped enough for an
experimental V4.0 candidate. Reviewers should attack installability, claim
language, zero-copy wording, stream/lifetime safety, and whether the M1 operator
route is sufficient as the V4.0 headline.
