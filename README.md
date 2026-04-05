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

## Current v0.1 Position

RTDL v0.1 is a **bounded, reviewed research slice**.

What that means:

- the main language/runtime path exists
- the core RayJoin-style workload family runs end-to-end
- the bounded package has been checked carefully
- the project now has strong long-workload backend evidence on an accepted
  exact-source surface

What that does **not** mean:

- full paper-identical reproduction of every RayJoin dataset family
- exact computational geometry everywhere
- full polygon overlay materialization
- equal maturity across all backends and workloads

## Strongest Current Backend Story

The strongest current performance surface is:

- long exact-source `county_zipcode`
- positive-hit `pip`

On that accepted surface:

- **Embree** is parity-clean and faster than PostGIS on the published prepared
  and repeated raw-input boundaries
- **OptiX** is parity-clean and faster than PostGIS on the same published
  boundaries
- **Vulkan** is parity-clean and hardware-validated there, but slower

The bounded package still remains the **v0.1 trust anchor** even though the
strongest performance evidence is now the long exact-source `county_zipcode`
row.

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

## Future Direction

RTDL is meant to be broader than the current RayJoin slice. The research
direction is toward a larger family of non-graphical ray-tracing applications.

The papers below are part of **Rubao Lee's ray-tracing research line with
collaborators**. Copyright belongs to the respective authors and publishers.

Current future-direction references, listed in chronological order, are:

- **2024.** Liang Geng, Rubao Lee, and Xiaodong Zhang,
  [*RayJoin: Fast and Precise Spatial Join*](https://dl.acm.org/doi/10.1145/3650200.3656610),
  Proceedings of the 38th ACM International Conference on Supercomputing
  (ICS 2024).
  DOI: [10.1145/3650200.3656610](https://dl.acm.org/doi/10.1145/3650200.3656610)
- **2024.** Yangming Lv, Kai Zhang, Ziming Wang, Xiaodong Zhang, Rubao Lee,
  Zhenying He, Yinan Jing, and X. Sean Wang,
  [*RTScan: Efficient Scan with Ray Tracing Cores*](https://www.vldb.org/pvldb/vol17/p1460-lv.pdf),
  Proceedings of the VLDB Endowment 17(6), 1460--1472, 2024.
  DOI: [10.14778/3648160.3648183](https://doi.org/10.14778/3648160.3648183)
- **2025.** Liang Geng, Rubao Lee, and Xiaodong Zhang,
  [*LibRTS: A Spatial Indexing Library by Ray Tracing*](https://dl.acm.org/doi/10.1145/3710848.3710850),
  Proceedings of the 30th ACM SIGPLAN Annual Symposium on Principles and
  Practice of Parallel Programming (PPoPP 2025).
  DOI: [10.1145/3710848.3710850](https://dl.acm.org/doi/10.1145/3710848.3710850)
- **2025.** Zhixiong Xiao, Mengbai Xiao, Yuan Yuan, Dongxiao Yu, Rubao Lee,
  and Xiaodong Zhang,
  [*A Case Study for Ray Tracing Cores: Performance Insights with Breadth-First Search and Triangle Counting in Graphs*](https://dl.acm.org/doi/10.1145/3727108),
  Proceedings of the ACM on Measurement and Analysis of Computing Systems,
  9(2), 2025.
  DOI: [10.1145/3727108](https://dl.acm.org/doi/10.1145/3727108)
- **2025.** Xuri Shi, Kai Zhang, X. Sean Wang, Xiaodong Zhang, and Rubao Lee,
  [*RayDB: Building Databases with Ray Tracing Cores*](https://www.vldb.org/pvldb/vol19/p43-shi.pdf),
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
2. [Quick Tutorial](docs/quick_tutorial.md)
3. [v0.1 Release Notes](docs/v0_1_release_notes.md)
4. [Architecture, API, And Performance Overview](docs/architecture_api_performance_overview.md)
5. [v0.1 Reproduction And Verification](docs/v0_1_reproduction_and_verification.md)
6. [v0.1 Support Matrix](docs/v0_1_support_matrix.md)
7. [RayJoin Reproduction Performance Report](docs/reports/goal104_rayjoin_reproduction_performance_report_2026-04-05.md)
8. [RayJoin Target](docs/rayjoin_target.md)

## Project Status

This repository is maintained as a reviewed research/engineering workspace.
Source code, reports, tests, review artifacts, and manuscript files are kept
together so the current RTDL v0.1 package remains understandable and auditable.
