# V3 Scope Correction: No Embedding Work Before V4

Date: 2026-06-18

## Instruction To The Next Primary AI

Treat this document as a hard scope correction.

V3.0 does **not** include embedding work.

Embedding, C ABI, SDK packaging, generated bindings, device-buffer execution,
external stream ordering, zero-copy framework interop, and device-callable
fusion are V4.0 work. They must not be treated as V3.0 blockers, V3.0 release
criteria, or V3.0 success claims.

## Correct V3.0 Scope

V3.0 is about the RTDL benchmark-app/current-route system:

- benchmark apps;
- app-agnostic primitives;
- explicit partner policy;
- fair route comparison;
- evidence/claim boundaries;
- current-route closure for the benchmark suite.

V3.0 is complete only if the benchmark-app/current-route scope is complete and
honestly documented. It is not made more complete by adding embedding features,
and it must not be delayed by unfinished embedding features.

## Incorrect Scope Expansion To Avoid

Do not continue or reopen V3.0 work under any of these labels:

- stable C ABI;
- packaged SDK;
- generated bindings;
- Python/Rust/Julia/C#/Java embedding;
- DLPack support;
- `__cuda_array_interface__` execution support;
- device-buffer query route;
- external CUDA stream adoption;
- true zero-copy public claim;
- OptiX/Embree query execution through the C ABI;
- PTX/OptiX callable fusion;
- framework integration with PyTorch, JAX, CuPy, Numba, or similar runtimes.

Those can be discussed, designed, or implemented only as V4.0 work unless the
user explicitly reopens the scope.

## What To Do With Existing Embedding Artifacts

Existing embedding/C ABI artifacts may remain in the repository as historical
or preparatory evidence, but the next primary AI must read them with this
boundary:

- they do not define V3.0 completion;
- they do not authorize V3.0 release wording;
- they do not make V3.0 an SDK or embeddability release;
- they should not be added to the critical path for V3.0.

If a current document implies that embedding is part of V3.0, correct the
wording. The intended wording is:

```text
V3.0 excludes embedding/SDK/zero-copy work. Those items are V4.0 scope.
```

## Relationship To Goal4614

Goal4614 closed the V3 current scope by separating V3 completion from V4
deferrals. This document makes that separation stricter:

- V3.0 current-scope completion belongs to benchmark-app/current-route work.
- V4.0 owns embedding and external-runtime integration.
- Do not describe embedding as a V3.0 component.

## Human Context

The user explicitly challenged the prior agent:

```text
谁批准你做embedding工作了在V3之前？
```

The answer is: nobody did. The prior expansion into embedding before V3.0 was
scope drift. The next primary AI must not repeat it.

The safest path is to honor the user's intended ordering:

```text
V3.0 first: benchmark apps and current RTDL route system.
V4.0 later: embedding, SDK, generated bindings, zero-copy, and external runtime integration.
```
