# RTDL

RTDL is a Python-hosted DSL and runtime/compiler stack for **non-graphical
ray-tracing-based applications**. The project goal is to let users write
high-level kernels once and execute them across multiple ray-tracing backends
without programming backend-specific details directly.

## Current Position

RTDL is no longer only a design sketch.

Current validated execution surface:

- native C/C++ oracle via `rt.run_cpu(...)`
- Intel Embree backend via `rt.run_embree(...)`
- NVIDIA OptiX backend via `rt.run_optix(...)` on `192.168.1.20`

Current supported workloads:

- `lsi`
- `pip`
- `overlay`
- `ray_tri_hitcount`
- `segment_polygon_hitcount`
- `point_nearest_segment`

Current v0.1 application slice:

- RayJoin-style workloads
- exact-source and bounded reproduction work on Embree
- first real-data OptiX validation on the Linux GPU host

Important current boundaries:

- precision is still `float_approx`
- RTDL does not claim robust/exact computational geometry yet
- the generated OptiX/CUDA skeleton path is not the trusted runtime path
- large-scale GPU scaling still needs further work

## Project Goal

The whole-project goal is broader than RayJoin and broader than the currently
validated backends.

RTDL is intended to become a language/runtime system for non-graphical RT
applications across multiple backend families, including:

- Embree / CPU
- OptiX / CUDA
- AMD HIP RT
- Intel RT stacks
- Apple RT ecosystems
- Qualcomm/mobile RT ecosystems

The current repository should be read as:

- **whole project**: multi-backend DSL for non-graphical RT applications
- **current v0.1 slice**: RayJoin-focused validation path
- **currently validated backends**: native oracle, Embree, OptiX

## Read This First

Start here:

1. [Project Vision](/Users/rl2025/rtdl_python_only/docs/vision.md)
2. [v0.1 Plan](/Users/rl2025/rtdl_python_only/docs/v0_1_final_plan.md)
3. [Docs Index](/Users/rl2025/rtdl_python_only/docs/README.md)

Language docs:

- [RTDL Language Docs](/Users/rl2025/rtdl_python_only/docs/rtdl/README.md)
- [Feature Guide](/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md)

Project/workflow docs:

- [RayJoin Target](/Users/rl2025/rtdl_python_only/docs/rayjoin_target.md)
- [Dataset Summary](/Users/rl2025/rtdl_python_only/docs/rayjoin_datasets.md)
- [Public Dataset Sources](/Users/rl2025/rtdl_python_only/docs/rayjoin_public_dataset_sources.md)
- [Reliability Process](/Users/rl2025/rtdl_python_only/docs/development_reliability_process.md)
- [AI Collaboration Workflow](/Users/rl2025/rtdl_python_only/docs/ai_collaboration_workflow.md)

## Repository Layout

- `src/rtdsl/`: DSL frontend, IR, lowering, and Python runtime surface
- `src/native/`: native C++ runtime backends and oracle
- `scripts/`: experiment and validation harnesses
- `tests/`: unit and integration tests
- `examples/`: small example programs
- `apps/`: standalone validation or demo programs
- `docs/`: live guidance and active project docs
- `docs/reports/`: accepted reports and experiment writeups
- `history/`: archived review, revision, and consensus artifacts

## Build And Test

Core local commands:

```sh
make build
make test
make verify
```

These do not require Embree or OptiX just to validate the compiler/language
surface.

## Backend Notes

### Native Oracle

- `rt.run_cpu(...)` is the current ground-truth native C/C++ oracle path
- `rt.run_cpu_python_reference(...)` preserves the old Python reference
  semantics for regression checks

### Embree

- `rt.run_embree(...)` is the controlled CPU backend
- `result_mode="raw"` and prepared raw execution are the main low-overhead
  paths
- current large real-data validation exists for multiple RayJoin-style families

### OptiX

- `rt.run_optix(...)` is the controlled GPU backend
- current trusted host: `192.168.1.20`
- current trusted PTX path on that host uses the `nvcc` fallback
- current real-data OptiX validation exists for bounded `County ⊲⊳ Zipcode`
  and larger Goal 41-style checks

## Current Documentation Policy

The authoritative current-state story should come from:

- this README
- `docs/vision.md`
- `docs/v0_1_final_plan.md`
- `docs/rtdl/`
- the workflow and dataset guidance docs

Goal plans and archived reports remain important, but they are reference
material, not the primary current-state narrative.
