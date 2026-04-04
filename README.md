# RTDL

RTDL is a research system for writing and running **non-graphical ray-tracing
programs**.

In ordinary computer graphics, ray tracing is used to render images. RTDL uses
the same hardware and software ideas for other kinds of problems, especially
spatial data processing. Instead of asking “what color is this pixel?”, RTDL
asks questions such as:

- which line segments intersect
- which points fall inside which polygons
- which geometric objects overlap or need further checking

The goal is to let users write those queries once in a higher-level language,
then run them across multiple backends without hand-writing backend-specific
code for Embree, OptiX, or Vulkan.

## Why This Project Exists

Modern ray-tracing systems are fast at hierarchical geometric search. Research
systems such as RayJoin showed that this can also help database-style spatial
operations, not just graphics.

RTDL is an attempt to make that idea easier to program, test, and reproduce.

## What RTDL Contains Today

The current repository includes:

- a Python-hosted DSL for authoring kernels
- compiler and lowering code
- a native C/C++ oracle used as the main internal correctness reference
- an Embree backend
- an OptiX backend validated on the Linux GPU host `192.168.1.20`
- a Vulkan ray-tracing backend that works on the accepted bounded validation
  surface, but is still considered provisional for larger-scale use
- PostGIS-based external ground-truth checking for accepted bounded packages

## Current Validated Application Slice

The current validated slice is based on **RayJoin-style spatial workloads**.

In simple terms, RTDL currently focuses on operations such as:

- line-segment intersection
- point-in-polygon testing
- bounded overlap/overlay seed generation
- several related geometric counting and nearest-query tasks

The strongest accepted bounded package currently includes:

- `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
- `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`
- bounded `LKAU ⊲⊳ PKAU`
- bounded `LKAU ⊲⊳ PKAU` `overlay-seed analogue`

Across that accepted bounded surface, RTDL has validated comparisons across:

- PostGIS
- native C oracle
- Embree
- OptiX

Vulkan is correctness-closed on the accepted bounded Linux validation surface,
but it is not yet promoted to the same larger-scale maturity level as Embree
or OptiX.

## What v0.1 Means

RTDL v0.1 is reached as a **bounded, audited research slice**.

That means:

- the main language/runtime path exists
- the core spatial workloads run end-to-end
- the accepted bounded package has been checked carefully
- the project has a submission-ready paper package

That does **not** mean:

- full paper-identical reproduction of every RayJoin dataset family
- exact or robust computational geometry in the strongest formal sense
- full polygon overlay materialization
- large-scale Vulkan maturity

## Current Boundaries

Important current limits:

- GPU traversal still uses approximate floating-point geometry
- RTDL does not yet claim robust/exact computational geometry everywhere
- the current `overlay` path is a seed-generation analogue, not full polygon
  overlay materialization
- the generated OptiX/CUDA skeleton path is not the trusted runtime path
- Vulkan still has larger-package scaling limits

## Long-Term Direction

The long-term project vision is broader than the current RayJoin slice.

RTDL is intended to support non-graphical ray-tracing applications across
multiple backend families, including:

- CPU ray-tracing libraries such as Intel Embree
- NVIDIA OptiX/CUDA-based GPU backends
- Vulkan ray-tracing-based GPU backends
- AMD HIP RT-based backends

## Where To Start

If you are new to the project, read these first:

- [Docs Index](docs/README.md)
- [Vision](docs/vision.md)
- [v0.1 Plan](docs/v0_1_final_plan.md)
- [RayJoin Target](docs/rayjoin_target.md)
- [RTDL Feature Guide](docs/rtdl_feature_guide.md)
- [Paper Package](paper/rtdl_rayjoin_2026/README.md)

## Project Status

The repository is maintained as a reviewed research/engineering workspace.
Source code, docs, reports, tests, history, and manuscript artifacts are kept
together so the current bounded RTDL v0.1 package stays understandable and
auditable.
