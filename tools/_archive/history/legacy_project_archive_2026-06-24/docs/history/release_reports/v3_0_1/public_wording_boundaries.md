# RTDL v3.0.1 Public Wording Boundaries

Status: locked for v3.0.1 publication.

Date: 2026-06-18

## Allowed Thesis

RTDL v3.0.1 is a source-tree patch release that preserves the current ten-app
benchmark route matrix and publishes cleaned primitive-first plus
partner-explicit app author guidance.

Performance wording remains row-scoped, contract-scoped, backend-scoped,
partner-scoped, hardware-scoped, timing-scoped, and caveat-scoped.

Embedding, C ABI, SDK packaging, generated bindings, device-buffer execution,
external stream ordering, zero-copy framework interop, and device-callable
fusion are V4.0 scope, not V3.0 release claims.

## Required Sentence Shape

Every public performance sentence must name:

- app or primitive;
- exact output contract;
- backend pair or route pair;
- partner policy;
- hardware;
- timing protocol;
- speedup direction, parity, or slowdown;
- caveat and reviewed artifact path.

## Allowed Short Release Sentence

```text
RTDL v3.0.1 is the source-tree patch release that preserves the current
ten-app benchmark route matrix and publishes the primitive-first,
partner-explicit RTDL programming surface, with public performance claims kept
row-scoped and evidence-bound.
```

## Blocked Wording

Do not say:

- RTDL accelerates every benchmark app.
- RTDL provides whole-application speedups for all V3 routes.
- `--backend optix` proves RT-core acceleration.
- RTDL beats RayJoin, X-HD, RTNN, RT-Graph, LibRTS, or any specialized author
  implementation as a whole system.
- RTDL reproduces a paper unless a row-specific release packet authorizes that
  exact statement.
- Partner choice is automatic.
- CuPy, Numba, PyTorch, JAX, CUDA, or user kernels are accelerated
  automatically by RTDL.
- V3.0.1 includes a PyPI package, wheel, stable SDK, or generated binding package.
- V3.0.1 includes public true-zero-copy or complete device-resident execution.
- V3.0.1 C ABI queries consume device buffers.
- V3.0.1 proves external CUDA stream ordering.
- V3.0.1 exposes arbitrary raw OptiX callbacks as the stable user API.
- V3.0.1 allows app-specific native-engine logic as the extension model.

## V4 Deferrals

These are explicitly future work and must not be described as V3.0.1 delivered
features:

- stable packaged SDK;
- generated language bindings;
- device-buffer query route;
- external CUDA stream ordering;
- public true-zero-copy proof;
- OptiX/Embree execution through the C ABI;
- optional device-callable fusion;
- AMD/HIPRT timing and parity evidence when hardware exists.

## Release Boundary

The maintainer authorized publication of V3.0.1 on 2026-06-18. That authorization
publishes the source-tree V3.0.1 boundary. It does not widen the technical claim
surface beyond the evidence recorded by Goal4614 and the release docs in this
packet.
