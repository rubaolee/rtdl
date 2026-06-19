# V4 Next Step After PyTorch Route: 2-AI Consensus

Date: 2026-06-19
Status: decision record for the next engineering cut, not a release approval.

## Current State

V4 remains an experimental Python GPU RT-core operator track. The fixed-radius
M1 route has evidence for CuPy, Numba, legacy DLPack capsules, and a narrow
PyTorch CUDA tensor route. The current user front door remains v3.0.2.

Latest pushed validation before this decision:

- commit: `d5605cd36`
- Linux host: `192.168.1.20`
- `make build-optix`: pass
- `v4_active`: 64 tests, pass
- PyTorch CUDA tensor probe: pass
- claim scan, JSON validation, diff check, clean worktree: pass

## Inputs

Peirce, from a product/release-gate view, ranked package/runtime story first:
V4 cannot become a user front door while it remains source-tree-only. Peirce
ranked M8 packet scaffolding second and RTX/RT-core speed evidence third.

Beauvoir, from an implementation/risk view, ranked PyTorch compatibility matrix
first: the narrow PyTorch route is proven, but the remaining risk around
PyTorch behavior is still mostly Python-side validation and probe work.
Beauvoir ranked framework-neutral DLPack second and async/lifetime third.

## Decision

Proceed first with a PyTorch compatibility matrix, scoped strictly to the
existing fixed-radius M1 route.

Rationale:

- It reduces the closest open engineering blocker without widening the native
  route.
- It is immediately actionable on the available Linux GPU host.
- It keeps the V4 claim surface honest: exact fixed-radius M1 PyTorch CUDA
  tensor compatibility, not a full PyTorch partner surface.
- It produces stronger evidence before package/runtime or M8 release-packet
  work tries to describe the route to users.

## Non-Goals

This decision does not authorize:

- full PyTorch partner-surface wording;
- arbitrary PyTorch program acceleration;
- framework-neutral DLPack support;
- async/nonblocking completion;
- public true-zero-copy wording;
- package, PyPI, wheel, or stable SDK wording;
- RTX/RT-core speedup claims.

## Required Evidence For This Cut

The PyTorch compatibility matrix should cover:

- accepted contiguous detached CUDA tensors;
- direct `torch.cuda.Stream` object handling, not only pre-extracted stream
  pointers;
- caller-owned output columns;
- same-stream execution;
- distinct prepare/query streams through the existing prepared route;
- rejected CPU tensors;
- rejected wrong dtypes;
- rejected rank, length, missing/extra-column, and output-contract failures;
- rejected non-contiguous or sliced views;
- rejected grad-enabled input and output tensors.

After the matrix passes on `192.168.1.20`, update the PyTorch report, blocker
manifest, status docs, and tests. Keep `full_pytorch_partner_surface` open
unless a later review explicitly narrows and closes that blocker.

## Next Release-Gate Work

After this matrix, return to Peirce's package/runtime recommendation: produce a
clean package-flow packet or an explicit source-tree-only M8 packet. Do not
promote V4 to the current front door without that release-gate work and fresh
2+ AI/external review.
