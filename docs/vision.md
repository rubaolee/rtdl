# Vision

## Whole-Project Goal

Build a DSL and runtime/compiler stack for **non-graphical, re-purposed ray-tracing-based applications** across multiple underlying RT libraries, hardware targets, and software ecosystems.

The long-term target is not a single backend or a single application. RTDL should eventually support applications where ray tracing is useful as a traversal and candidate-generation engine, while hiding low-level backend details such as OptiX program groups, shader binding tables, CUDA/PTX wiring, HIP RT integration, backend launch code, and other platform-specific runtime mechanisms.

Target backend families over time include:

- CPU RT libraries such as Intel Embree,
- NVIDIA OptiX / CUDA,
- AMD HIP RT,
- Intel RT hardware/software stacks,
- Apple RT ecosystems,
- Qualcomm/mobile RT ecosystems,
- and other practical RT-capable runtimes when they matter for the application class.

## Problem Statement

Today, building non-graphical RT systems often requires developers to simultaneously handle:

- domain decomposition,
- ray-tracing problem reformulation,
- backend-specific implementation details,
- backend-specific performance constraints, and
- numerical correctness issues.

That stack is too deep for most domain experts. The result is that RT cores remain difficult to use outside graphics, even when the algorithmic fit is strong.

## RTDL Thesis

RTDL separates the problem into three layers:

1. Python-hosted frontend
   Express kernels inside Python so users can compose with existing data pipelines and generate specialized kernels programmatically.
2. Ray-tracing formulation
   Lower frontend operations into rays, acceleration structures, hit semantics, and result materialization.
3. Backend realization
   Materialize the formulation for the available local/runtime targets first, then expand across multiple RT-capable runtimes.

The user writes layer 1 with a small amount of optional control over layer 2. The compiler owns layer 3.

## v0.1 Scope Within That Vision

The whole-project vision is broad, but the current **v0.1** target is intentionally narrow.

v0.1 is the first serious vertical slice of the larger project:

- application focus: **RayJoin-style workloads**
- local executable backend: **Intel Embree on this Mac**
- near-term final backend goal: **NVIDIA OptiX / CUDA when hardware becomes available**

So the current repository should be read this way:

- **project vision**: general multi-backend DSL for non-graphical RT applications
- **v0.1 execution target**: RayJoin-focused vertical slice, currently proven on Embree, later extended to NVIDIA

This means RTDL is:

- not just a RayJoin reimplementation,
- not just an Embree wrapper,
- and not just an NVIDIA plan,

but a language/runtime system whose first concrete validation target is RayJoin.

## Design Principles

- Preserve performance visibility. The DSL should expose important cost drivers such as query type, geometry role, precision mode, and expected output cardinality.
- Use Python as host language, not as the semantic core. Only a constrained RT kernel subset should be compiled.
- Default to exactness. Non-graphics workloads often require correctness properties stronger than graphics rendering does.
- Make data roles explicit. The language should distinguish build-side geometry, probe-side geometry, and emitted results.
- Treat ray tracing as an execution strategy, not as the source language.
- Keep lowering inspectable. Users should be able to see the generated backend plan and understand why it performs a certain way.

## Near-Term Research Questions

- Which RayJoin concepts are fundamental and should appear in the source language?
- Which concepts should remain purely backend internal across Embree, OptiX, HIP RT, and future RT ecosystems?
- How should RTDL represent precision modes such as downcast-with-conservative-bounds versus exact integerized execution?
- How much scheduling control is necessary before users lose the simplicity benefit?
- What is the right intermediate representation for multiple non-graphics RT applications beyond spatial join?

## Phase 1 Scope

Phase 1 intentionally focuses on:

- line segment intersection,
- point-in-polygon,
- polygon overlay building blocks,
- RayJoin-compatible data roles, and
- a Python-hosted frontend that can evolve into a stronger compiler pipeline.

It does not yet attempt full multi-backend realization. The current repository first establishes:

- an Embree-backed local baseline,
- a RayJoin-aligned workload surface,
- a stable IR/runtime contract,
- and a performance path that can later be inherited by future backends.
