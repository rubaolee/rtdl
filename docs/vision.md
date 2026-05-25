# Vision

## Whole-Project Goal

RTDL is a Python-hosted DSL and runtime/compiler stack for non-graphical,
ray-tracing-shaped computation: spatial search, visibility, proximity, compact
candidate generation, and backend-assisted summaries.

RTDL is not intended to be:

- only a renderer;
- only an Embree wrapper;
- only an OptiX experiment;
- only a fixed catalog of applications.

It is intended to be a language/runtime system where users write the Python
program, express the RT-shaped kernel in RTDL, and select a backend without
turning the native engine into an app-specific product.

## Thesis

Non-graphics RT applications often force users to manage too many concerns at
once:

- problem decomposition;
- ray-tracing reformulation;
- backend launch and runtime details;
- memory layout and transfer decisions;
- precision and performance tradeoffs;
- post-traversal reductions and continuation work.

RTDL separates those concerns:

1. Python owns the app and policy.
2. RTDL owns the typed kernel contract.
3. Backends own app-agnostic traversal/refinement execution.
4. Partner libraries own tensor-side continuation when the app needs vectorized
   or GPU-side work outside traversal.

## Backend Ambition

The project is multi-backend by design. The current public docs focus on the
supported v2.x-facing surface, with Embree and OptiX as the primary engineering
targets and other backend families preserved according to their documented
maturity.

Long-term backend families include:

- CPU ray-tracing libraries such as Intel Embree;
- NVIDIA OptiX/CUDA-based GPU backends;
- Vulkan ray-tracing-based GPU backends;
- AMD HIP RT-based backends;
- Apple ray-tracing platforms;
- other hardware or software traversal systems where a clean backend contract
  can be maintained.

## Current Product Direction

The current direction is:

- keep the native engine app-agnostic;
- make Python+RTDL a usable language surface;
- make Python+partner+RTDL useful for high-performance continuation work;
- document exact backend support instead of implying universal acceleration;
- preserve old release evidence in the audit/history archive rather than mixing
  it into learner docs.

For the active user path, start with [Learn RTDL](learn/README.md). For
release evidence and older milestones, use [Audit](audit/README.md) and
[History](history/README.md).
