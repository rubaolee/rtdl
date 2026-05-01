# Goal1226 Codex Roadmap Understanding: v1.0, v1.5, v2.0

Date: 2026-05-01

Author: Codex

## Purpose

This document records Codex's current understanding of the RTDL roadmap after
the NVIDIA RT and Embree v0.9.8 release work. It is intended for independent
Gemini comparison and cross-review.

The central thesis is:

> RTDL should prove meaningful application targets first, then reduce engine
> technical debt by turning proven app-specific kernels into generic
> traversal-plus-reduction primitives, and finally integrate cleanly with
> external GPU compute ecosystems rather than becoming a general-purpose
> compiler.

## Current Baseline After v0.9.8

The project now has a credible app-driven foundation:

- Public examples exercise real RT-style workloads rather than toy kernels.
- NVIDIA OptiX/RTX paths have bounded, reviewed public wording where evidence
  supports it.
- Embree serves as a CPU RT backend, fallback path, and comparison baseline.
- Public claims distinguish backend execution, native traversal, likely RT-core
  hardware use, and same-contract speedup evidence.
- Not every app has a public speedup claim, and that is correct. Some apps are
  RT-ready but blocked because valid evidence shows OptiX slower than Embree or
  below the public threshold.

This is the right release foundation. RTDL is meaningful only if its apps are
real enough to expose performance and architecture pressure. The v0.9.8 work did
that: it showed which app phases benefit from RT traversal, which phases are
dominated by Python or postprocess work, and which custom native endpoints are
too application-specific to keep forever.

## v1.0: App Credibility And Honest RT Acceleration

v1.0 should be treated as the first stable app-centered release target.

The goal of v1.0 is not architectural purity. The goal is to prove that RTDL can
make useful application kernels run through RT-capable backends with correct,
bounded, reproducible evidence.

### What v1.0 Should Prioritize

- Preserve working public apps.
- Keep current app-specific native endpoints where they are needed for
  correctness or performance.
- Maintain strict public claim boundaries.
- Keep OptiX, Embree, Apple RT, HIPRT, and future Vulkan wording honest and
  backend-specific.
- Make app docs explain exactly which phase is accelerated and which phase is
  not.
- Keep compatibility wrappers stable so users can run examples without learning
  the internal engine roadmap.

### What v1.0 Should Not Try To Do

- Do not rewrite all C++/CUDA engines into generic primitives before release.
- Do not claim whole-app RTX acceleration where only a sub-path is accelerated.
- Do not hide slower OptiX-vs-Embree evidence.
- Do not treat `--backend optix` as equivalent to a public RT-core speedup
  claim.
- Do not collapse all app-specific lowering into the native engine.

### v1.0 Success Definition

v1.0 succeeds when RTDL has a stable set of public apps with:

- clear app purpose;
- clear accelerated sub-path;
- correct fallback/reference behavior;
- reproducible evidence;
- tested docs and examples;
- public wording that does not overclaim.

In this sense, v1.0 is the "credibility release". It answers why RTDL exists.

## v1.5: Generic Traversal-Plus-Reduction Primitives

v1.5 should be the technical-debt reduction release.

The v0.9.8/v1.0 app work exposed a real problem: too much application logic has
leaked into native C++/CUDA endpoints. That was acceptable for proving apps, but
it is not the right long-term engine architecture.

v1.5 should decouple the engine from hardcoded app names by introducing a small
set of generic primitives. The Python layer remains responsible for
application-specific lowering; the native engine becomes responsible for fast
geometry traversal and simple reductions.

### Accepted Primitive Direction

The prior architecture consensus accepted this refined minimum primitive set:

- `ANY_HIT`
- `COUNT_HITS`
- `REDUCE_FLOAT(MIN|MAX|SUM)`
- `REDUCE_INT(COUNT|SUM)`
- `COLLECT_K_BOUNDED` as experimental only after scalar reductions are stable

The important design shift is not the names themselves. The important shift is
that the engine should operate on generic geometry and payload schemas:

- points;
- segments;
- triangles;
- rays;
- AABBs;
- scalar payloads;
- bounded hit/candidate buffers.

Applications then lower themselves into these shapes.

### Why This Covers Current Apps

| App family | v1.0 style | v1.5 target |
| --- | --- | --- |
| Fixed-radius density, hotspot, coverage | App-specific summary paths | `COUNT_HITS`, `ANY_HIT`, scalar threshold reductions |
| Segment/polygon hitcount and any-hit rows | Native segment/polygon endpoints | Generic segment/polygon traversal plus count/any/bounded collect |
| Hausdorff and nearest-distance decisions | Dedicated Hausdorff/nearest endpoints | `REDUCE_FLOAT(MIN)` per probe plus Python or second-stage max |
| Database compact summaries | App-specific DB compact summary kernels | AABB/payload lowering plus `REDUCE_INT`/`REDUCE_FLOAT` group-like reductions |
| Graph visibility and graph-ray candidates | Graph-specific native paths | Spatial visibility/candidate generation as traversal primitive; BFS/triangle counting remains explicit app logic unless separately lowered |
| ANN/KNN candidate phases | App-specific candidate gates | `COLLECT_K_BOUNDED` or threshold candidate buffers, initially experimental |

### Required v1.5 Contracts Before Implementation

v1.5 should not start with broad backend rewrites. It should start with contracts:

- primitive ABI and versioning;
- input geometry schemas;
- payload layout;
- result shape;
- grouping semantics;
- hit filtering semantics;
- overflow behavior;
- determinism rules;
- backend parity expectations;
- fallback behavior when a backend lacks a primitive;
- public wording rules for generic primitives.

Without these contracts, generic primitives will simply recreate today’s
technical debt under more abstract names.

### Migration Rule

Every migrated app must prove:

- correctness parity against the v1.0 app-specific path;
- performance parity or an explicitly accepted overhead;
- stable fallback behavior;
- unchanged or improved public claim boundaries.

Old v1.0 endpoints should initially remain as compatibility wrappers. Retire
them only after the generic path is proven.

### Recommended First v1.5 Slice

The first implementation slice should be intentionally small:

1. Implement `ANY_HIT` and `COUNT_HITS` for one proven geometry pair in Embree
   and OptiX.
2. Re-express one or two fixed-radius prepared-summary apps through the generic
   wrapper.
3. Compare against the current app-specific path for correctness and speed.
4. Add docs showing that the generic primitive is an implementation mechanism,
   not automatically a public speedup claim.
5. Only then extend to `REDUCE_FLOAT`, `REDUCE_INT`, and experimental bounded
   collection.

## v2.0: Explicit Compute Partnership

v2.0 should be the ecosystem integration release.

The main v2.0 decision is that RTDL should not become an omnipotent Python
compiler. RTDL should not attempt to parse arbitrary Python, infer parallelism,
generate fused CUDA/OptiX/Vulkan kernels, and silently fall back when unsupported
constructs appear.

That path creates performance cliffs, compiler technical debt, and unclear
claim boundaries.

Instead, v2.0 should adopt explicit compute partnership:

- RTDL performs traversal and simple reductions.
- CuPy, PyTorch, Triton, Numba, or other compute tools handle custom dense
  compute.
- DLPack or equivalent zero-copy tensor exchange connects the phases.
- Users can see which phase uses RT traversal and which phase uses general GPU
  compute.

### v2.0 User Model

A v2.0 application should look conceptually like:

1. User prepares arrays/tensors in Python or GPU compute tooling.
2. RTDL lowers geometry and dispatches a generic RT traversal/reduction.
3. RTDL returns masks, counts, distances, candidates, or hit buffers.
4. The user applies custom logic in CuPy, PyTorch, Triton, or Numba.
5. Public claims stay phase-specific.

This gives users performance and control without pretending that RTDL can
compile arbitrary application logic.

### Extension Mechanisms

DLPack/zero-copy handoff is the preferred v1.5-to-v2.0 extension path because it
keeps RTDL’s ABI small while allowing complex downstream work.

PTX/SPIR-V/native plugin mechanisms may be valuable for power users, but they
should be experimental until the project can handle:

- plugin ABI versioning;
- backend divergence;
- security and unsafe code loading;
- reproducibility;
- reviewability;
- public claim ambiguity.

Native plugins should not be the primary v1.5 abstraction and should not be part
of stable public claims until much later.

## Version Boundary Summary

| Version | Primary job | Architecture posture | Public claim posture |
| --- | --- | --- | --- |
| v1.0 | Prove apps and evidence | Keep app-specific endpoints where needed | Strict bounded sub-path claims only |
| v1.5 | Reduce engine technical debt | Introduce generic traversal/reduction primitives and migrate selected endpoints | Generic primitive support is not automatically speedup wording |
| v2.0 | Integrate with compute ecosystem | Explicit zero-copy partnership with CuPy/PyTorch/Triton/Numba | Phase-specific RTDL and compute claims remain separate |

## Key Risks

The biggest v1.0 risk is overclaiming. The mitigation is the current public
wording matrix and review discipline.

The biggest v1.5 risk is designing primitives too broadly and recreating
application-specific logic in the engine. The mitigation is a narrow ABI and a
per-app lowering matrix before implementation.

The biggest v2.0 risk is attempting a magic compiler. The mitigation is explicit
compute partnership and zero-copy handoff.

## Codex Recommendation

Proceed in this order:

1. Treat v1.0 as app credibility plus release stability.
2. Ask Gemini to independently write its own v1.0/v1.5/v2.0 roadmap document.
3. Cross-review both documents and produce a two-AI or three-AI consensus report.
4. Before coding v1.5, write the primitive contract and per-app lowering matrix.
5. Only implement the first generic primitive slice after the contract is
   reviewed.

The guiding rule should remain: applications justify RTDL, generic primitives
make RTDL maintainable, and explicit compute partnership keeps RTDL from
becoming an unbounded compiler project.
