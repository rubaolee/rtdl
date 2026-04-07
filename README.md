# RTDL

RTDL is a research system for writing and running **non-graphical ray-tracing
programs**.

In graphics, ray tracing answers questions like “what does this pixel see?”.
RTDL uses the same traversal machinery for other questions, especially spatial
data questions such as:

- which line segments intersect
- which points fall inside which polygons
- which objects overlap or need exact follow-up checking

The point of RTDL is simple:

- write the workload once
- keep the semantics visible
- run it across multiple backends
- avoid hand-writing backend-specific code for Embree, OptiX, and Vulkan

## Why RTDL Exists

Ray tracing hardware and software are very good at hierarchical geometric
search. That makes them interesting for database-style and spatial workloads,
not only for image rendering.

The motivating application target in this repository is **RayJoin**:

- Liang Geng, Rubao Lee, and Xiaodong Zhang,
  *RayJoin: Fast and Precise Spatial Join*,
  Proceedings of the 38th ACM International Conference on Supercomputing
  (ICS 2024),
  DOI: [10.1145/3650200.3656610](https://dl.acm.org/doi/10.1145/3650200.3656610)

RayJoin showed that ray-tracing cores can be used for spatial join work. RTDL
takes the next step: it asks whether those workloads can be expressed through a
programmable language/runtime surface while staying correct across multiple
backends.

## What RTDL Contains Today

The current repository includes:

- a Python-hosted DSL for authoring kernels
- compiler/lowering code
- a native C/C++ oracle used as an internal correctness reference
- an Embree backend
- an OptiX backend
- a Vulkan backend
- PostGIS-based external checking on accepted workload packages

## Current Main Position

The repository now has two important status layers:

- the archived **v0.1 trust anchor**
- the live **v0.2 midterm branch state on `main`**

The v0.1 anchor remains the bounded, reviewed RayJoin-heavy research slice.

Current `main` is broader than that archived slice:

- it keeps the accepted v0.1 surface
- it adds two closed segment/polygon workload families:
  - `segment_polygon_hitcount`
  - `segment_polygon_anyhit_rows`
- it adds a narrow Jaccard line:
  - `polygon_pair_overlap_area_rows`
  - `polygon_set_jaccard`
- for that Jaccard line, the public `embree`, `optix`, and `vulkan` run
  surfaces now accept the workloads through documented native CPU/oracle
  fallback on Linux
- it adds a narrow generate-only product line covering the segment/polygon
  families plus one authored Jaccard entry
- it has Linux/PostGIS-backed correctness and performance evidence for those
  families

Current `main` still does **not** mean:

- every backend/workload path is equally mature
- exact computational geometry everywhere
- full polygon overlay materialization
- a frozen release promise like the archived `v0.1.0` tag

## Release Reports

The canonical v0.1 release-report package is here:

- [RTDL v0.1 Release Reports](docs/release_reports/v0_1/README.md)

The frozen archived v0.1 baseline is here:

- [RTDL v0.1 Archive](docs/archive/v0_1/README.md)

That archive entry explains which tag and commit define the frozen v0.1
baseline and points readers to the canonical v0.1 release-report package.

## Strongest Current Backend Story

There are now two important performance stories on current `main`:

- the archived **v0.1 trust-anchor** performance surface:
  - long exact-source `county_zipcode`
  - positive-hit `pip`
- the live **v0.2 large-row** performance surface:
  - `segment_polygon_hitcount`
  - `segment_polygon_anyhit_rows`
  - Linux/PostGIS-backed through `x4096`
- the narrow **Jaccard Linux stress** surface:
  - public wrapper-surface consistency through `embree`, `optix`, and `vulkan`
    under documented native CPU/oracle fallback

On the v0.1 trust-anchor surface:

- **Embree** is parity-clean and faster than PostGIS on the published prepared
  and repeated raw-input boundaries
- **OptiX** is parity-clean and faster than PostGIS on the same published
  boundaries
- **Vulkan** is parity-clean and hardware-validated there, but slower

On the live v0.2 large-row surface:

- all four RTDL backends are parity-clean against PostGIS on the accepted
  deterministic segment/polygon rows
- at `x4096`, RTDL backends remain faster than PostGIS on both current
  segment/polygon families

The bounded v0.1 package remains the **trust anchor**, while the v0.2
segment/polygon line is the strongest current large-row live-branch story.
The Jaccard line is real, but still under a narrower workload and backend
maturity boundary.

## Backend Roles

- **Embree**: primary CPU performance backend
- **OptiX**: primary NVIDIA GPU performance backend
- **Vulkan**: portable, correctness-preserving GPU backend
- **Python oracle / native C oracle**: trust references, not release
  performance backends
- **PostGIS**: external indexed comparison baseline

## Current Limits

- GPU traversal still uses approximate floating-point geometry
- RTDL does not claim robust/exact computational geometry everywhere
- current `overlay` is a seed-generation analogue, not full polygon output
  materialization
- Vulkan is supported and parity-clean on the accepted long exact-source
  surface, but is not currently performance-competitive there
- the Jaccard line is public on `embree`, `optix`, and `vulkan` only through
  documented native CPU/oracle fallback, not native backend-specific kernels

## Future Direction

RTDL is meant to be broader than the current RayJoin slice. The research
direction is toward a larger family of non-graphical ray-tracing applications.

The papers below are part of **Rubao Lee's ray-tracing research line with
collaborators**. Copyright belongs to the respective authors and publishers.

Current future-direction references, listed in chronological order, are:

- **2024.** Liang Geng, Rubao Lee, and Xiaodong Zhang,
  *RayJoin: Fast and Precise Spatial Join*,
  Proceedings of the 38th ACM International Conference on Supercomputing
  (ICS 2024).
  DOI: [10.1145/3650200.3656610](https://dl.acm.org/doi/10.1145/3650200.3656610)
- **2024.** Yangming Lv, Kai Zhang, Ziming Wang, Xiaodong Zhang, Rubao Lee,
  Zhenying He, Yinan Jing, and X. Sean Wang,
  *RTScan: Efficient Scan with Ray Tracing Cores*,
  Proceedings of the VLDB Endowment 17(6), 1460--1472, 2024.
  DOI: [10.14778/3648160.3648183](https://doi.org/10.14778/3648160.3648183)
- **2025.** Liang Geng, Rubao Lee, and Xiaodong Zhang,
  *LibRTS: A Spatial Indexing Library by Ray Tracing*,
  Proceedings of the 30th ACM SIGPLAN Annual Symposium on Principles and
  Practice of Parallel Programming (PPoPP 2025).
  DOI: [10.1145/3710848.3710850](https://dl.acm.org/doi/10.1145/3710848.3710850)
- **2025.** Zhixiong Xiao, Mengbai Xiao, Yuan Yuan, Dongxiao Yu, Rubao Lee,
  and Xiaodong Zhang,
  *A Case Study for Ray Tracing Cores: Performance Insights with Breadth-First Search and Triangle Counting in Graphs*,
  Proceedings of the ACM on Measurement and Analysis of Computing Systems,
  9(2), 2025.
  DOI: [10.1145/3727108](https://dl.acm.org/doi/10.1145/3727108)
- **2025.** Xuri Shi, Kai Zhang, X. Sean Wang, Xiaodong Zhang, and Rubao Lee,
  *RayDB: Building Databases with Ray Tracing Cores*,
  Proceedings of the VLDB Endowment 19(1), 43--55, 2025.
  DOI: [10.14778/3772181.3772185](https://doi.org/10.14778/3772181.3772185)
- **2026.** Liang Geng, Zhehu Yuan, Rubao Lee, Fusheng Wang, and Xiaodong
  Zhang,
  *X-HD: Fast Hausdorff Distance Computation with Ray Tracing*,
  Proceedings of the 39th ACM International Conference on Supercomputing
  (ICS 2026).
  DOI: not listed in the current public materials yet.

Additional notes and context are collected here:

- [Future Ray-Tracing Directions](docs/future_ray_tracing_directions.md)

## Where To Start

If you are new to the project, start here:

1. [Docs Index](docs/README.md)
2. [RTDL v0.2 User Guide](docs/v0_2_user_guide.md)
3. [Feature Homes](docs/features/README.md)
4. [Quick Tutorial](docs/quick_tutorial.md)
5. [v0.1 Release Notes](docs/v0_1_release_notes.md)
6. [Architecture, API, And Performance Overview](docs/architecture_api_performance_overview.md)
7. [v0.1 Reproduction And Verification](docs/v0_1_reproduction_and_verification.md)
8. [v0.1 Support Matrix](docs/v0_1_support_matrix.md)
9. [v0.1 Release Reports](docs/release_reports/v0_1/README.md)
10. [RTDL v0.1 Archive](docs/archive/v0_1/README.md)
11. [RayJoin Reproduction Performance Report](docs/reports/goal104_rayjoin_reproduction_performance_report_2026-04-05.md)
12. [RayJoin Target](docs/rayjoin_target.md)

## Project Status

This repository is maintained as a reviewed research/engineering workspace.
Source code, reports, tests, and review artifacts are kept together so the
current RTDL v0.1 package remains understandable and auditable.

Copyright (c) 2026 Rubao Lee. All rights reserved. RTDL and this repository
are owned and maintained by Rubao Lee.
