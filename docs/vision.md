# Vision

## Goal

Reduce the difficulty of programming non-graphics ray tracing applications by roughly an order of magnitude.

The project targets workloads where ray tracing hardware is useful as a traversal and candidate-generation engine, but where users should not need to directly manipulate OptiX program groups, shader binding tables, PTX modules, payload registers, or backend launch code.

## Problem Statement

Today, building systems like RayJoin requires developers to simultaneously handle:

- domain decomposition,
- ray-tracing problem reformulation,
- OptiX/CUDA implementation details,
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
   Materialize the formulation for RayJoin/OptiX first, then expand to other RT-capable runtimes.

The user writes layer 1 with a small amount of optional control over layer 2. The compiler owns layer 3.

## Design Principles

- Preserve performance visibility. The DSL should expose important cost drivers such as query type, geometry role, precision mode, and expected output cardinality.
- Use Python as host language, not as the semantic core. Only a constrained RT kernel subset should be compiled.
- Default to exactness. Non-graphics workloads often require correctness properties stronger than graphics rendering does.
- Make data roles explicit. The language should distinguish build-side geometry, probe-side geometry, and emitted results.
- Treat ray tracing as an execution strategy, not as the source language.
- Keep lowering inspectable. Users should be able to see the generated backend plan and understand why it performs a certain way.

## Near-Term Research Questions

- Which RayJoin concepts are fundamental and should appear in the source language?
- Which OptiX/CUDA concepts should remain purely backend internal?
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

It does not yet attempt full code generation or OptiX runtime integration inside this repository.
