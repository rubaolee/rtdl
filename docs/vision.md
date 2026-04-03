# Vision

## Whole-Project Goal

Build a DSL and runtime/compiler stack for **non-graphical, re-purposed
ray-tracing-based applications** across multiple backend libraries, hardware
targets, and software ecosystems.

RTDL is not intended to be:

- only a RayJoin reimplementation
- only an Embree wrapper
- only an OptiX experiment

It is intended to become a language/runtime system for writing a broader class
of RT-style applications once and mapping them onto different backend families.

## Thesis

Today, non-graphics RT systems often require users to simultaneously manage:

- problem decomposition
- ray-tracing reformulation
- backend-specific launch/runtime details
- backend-specific precision/performance tradeoffs
- dataset and memory layout details

RTDL aims to separate those concerns:

1. the user writes a compact kernel in Python
2. the compiler owns lowering into RT-style execution structure
3. the backend owns realization for the available runtime

## Backend Ambition

The long-term backend picture includes:

- Intel Embree / CPU
- NVIDIA OptiX / CUDA
- AMD HIP RT
- Intel RT stacks
- Apple RT ecosystems
- Qualcomm/mobile RT ecosystems

The current repo validates only a subset of that ambition, but the project
framing should stay multi-backend.

## Current v0.1 Slice

The current **v0.1** slice is intentionally narrower than the whole vision.

v0.1 means:

- application focus: RayJoin-style workloads
- language focus: Python-hosted RTDL kernels
- correctness focus: native C/C++ oracle as project ground truth
- backend focus: controlled Embree and OptiX execution paths

Current reality:

- Embree is the stronger, more mature backend today
- OptiX is now real and validated, but still earlier in maturity
- the validated surface is bounded and workload-specific, not a full general RT
  language yet

## Design Principles

- Keep the source language smaller than the implementation ambition.
- Preserve performance visibility rather than hiding all cost drivers.
- Keep lowering inspectable.
- Make correctness boundaries explicit.
- Treat ray tracing as an execution strategy, not the source language.
- Prefer a stable oracle-backed runtime surface before broad backend expansion.

## Near-Term Goal

The next practical phase is not a redesign of RTDL’s vision.

It is to keep strengthening the same v0.1 slice by:

- tightening correctness and performance on Embree and OptiX
- expanding real-data validation
- improving documentation and trustworthiness
- moving closer to a bounded, honest RayJoin-style reproduction package across
  both current backends
