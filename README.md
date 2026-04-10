# RTDL

RTDL is a research runtime for **non-graphical geometric-query workloads**
built on ray-tracing traversal machinery.

It is designed for problems such as:

- segment/polygon hit counting
- segment/polygon any-hit row emission
- bounded polygon-set similarity
- Python applications that need a fast geometric-query core

RTDL is **not** positioned as a general-purpose renderer or graphics engine.
Its primary domain is non-graphical spatial computation. The visual demo is
included as proof that the same query core can also support a bounded
Python-hosted 3D application.

Current checkout identity:

- repo state anchor: `v0.3.0`
- stable released workload surface inside this release: `v0.2.0`
- released application/demo proof layer: `v0.3.0` on top of the same RTDL core

## Before Your First Run

Clone the repo like this:

```bash
git clone https://github.com/rubaolee/rtdl.git
cd rtdl
```

Runtime basics:

- use Python `3.10+`
- the local Python package name is `rtdsl`
- the repository name is `rtdl`
- `PYTHONPATH=src:.` tells Python to import the local `rtdsl` package from
  `src/rtdsl/` in this checkout

Minimal Python dependency guidance:

- required for the documented first-run path:
  - Python `3.10+`
- recommended for smoother demo/application runs:
  - `numpy`
- native backends also require their local host libraries/SDKs:
  - Embree for `embree`
  - NVIDIA OptiX SDK and CUDA for `optix`
  - Vulkan SDK / loader for `vulkan`
  - GEOS/PostGIS only for the documented external-checking and broader
    validation surfaces

Fastest safe install path for new users:

```bash
python3 -m pip install -r requirements.txt
```

## See It Quickly

<table>
  <tr>
    <td valign="top">

Primary front-door links:

- [Watch The Public Demo Video](https://youtube.com/shorts/VnzVWAPln3k?si=O1iet-3uFm2gpPes)
- [3D Rendering Source](examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py)
- [Quick Tutorial](docs/quick_tutorial.md)
- [RTDL v0.2 User Guide](docs/v0_2_user_guide.md)
- [Release-Facing Examples](docs/release_facing_examples.md)

   </td>
    <td valign="top" width="260">
      <a href="https://youtube.com/shorts/VnzVWAPln3k?si=O1iet-3uFm2gpPes">
        <img src="docs/assets/rtdl_visual_demo_thumb.png" alt="RTDL visual demo" width="240">
      </a>
    </td>
  </tr>
</table>

## What RTDL Is

In graphics, ray tracing answers questions like “what does this pixel see?”.
RTDL reuses that traversal machinery for non-graphical geometric questions,
especially spatial data questions such as:

- which line segments intersect
- which points fall inside which polygons
- which objects overlap or need exact follow-up checking

The core idea is simple:

- write the workload once
- keep the query semantics visible in Python
- run the same workload across multiple backends
- avoid hand-writing backend-specific code for Embree, OptiX, and Vulkan

## Why It Is Useful

RTDL is a good fit when you want to:

- express a geometric query once and run it on different backends
- keep the query logic visible in Python instead of burying it in backend code
- get row outputs such as counts, hit rows, or bounded aggregate metrics
- build a Python application where RTDL is the heavy geometric-query core

The current strongest released workload surfaces are:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

And the current strongest application-style proof is:

- a bounded RTDL-plus-Python 3D demo line with Windows Embree as the polished
  main public artifact and Linux OptiX/Vulkan as supporting backend artifacts

## Start Fast

If you want the shortest path to seeing RTDL do something real:

1. run the hello-world program
2. run one released workload example
3. continue into the quick tutorial and user guide

Repository-root commands:

```bash
PYTHONPATH=src:. python3 examples/rtdl_hello_world.py
PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 16
```

The `PYTHONPATH=src:.` prefix tells Python to import the local RTDL package
from this checkout.

If you omit that prefix, Python will usually fail with:

```text
ModuleNotFoundError: No module named 'rtdsl'
```

Then continue with:

1. [Quick Tutorial](docs/quick_tutorial.md)
2. [RTDL v0.2 User Guide](docs/v0_2_user_guide.md)
3. [Release-Facing Examples](docs/release_facing_examples.md)
4. [Feature Homes](docs/features/README.md)

## What The Video Means

RTDL also works well inside larger Python applications. A user does not need
to stay inside a fixed list of named workloads. RTDL can provide the
geometry-query core while Python handles surrounding application logic,
aggregation, reporting, or visual output.

That is what the visual demo is meant to show:

- RTDL is still the query engine
- Python is handling the surrounding application pipeline
- the movie demonstrates versatility, not a change in RTDL’s primary product
  definition

RTDL already includes a small example of that model:

- [examples/visual_demo/rtdl_lit_ball_demo.py](examples/visual_demo/rtdl_lit_ball_demo.py)

The repo currently has two layers:

- the released `v0.2.0` workload surface for row-oriented geometric-query work
- the newer `v0.3` application/demo layer built on the same RTDL core

The v0.3 line is now a released proof-of-capability layer showing that RTDL can
act as the geometric-query core inside a larger Python application. It does
not replace the bounded `v0.2.0` workload definition inside the same repo.

The bounded 3D RTDL ray/triangle surface is already closed across `embree`,
`optix`, and `vulkan` on Linux, while the current recommended public-facing
movie artifact is now presented through a single public video URL:

- [RTDL Visual Demo Video](https://youtube.com/shorts/VnzVWAPln3k?si=O1iet-3uFm2gpPes)

The current primary preserved 3D demo source inside the repo is the
hidden-star stable Earth line:

- [examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py](examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py)

It keeps RTDL in both the camera-hit and shadow-visibility stages while
avoiding the unstable self-shadow construction from the earlier moving-light
path.

The smoother one-light camera-orbit line remains preserved as a stable
comparison path:

- [examples/visual_demo/rtdl_smooth_camera_orbit_demo.py](examples/visual_demo/rtdl_smooth_camera_orbit_demo.py)

The moving-star orbit line remains preserved as a more intuitive but still more
artifact-prone comparison path:

- [examples/visual_demo/rtdl_orbiting_star_ball_demo.py](examples/visual_demo/rtdl_orbiting_star_ball_demo.py)

The repo still preserves the accepted local movie artifacts and the supporting
Linux backend demo artifacts in the deeper reports, but the front surface now
uses the single public video link rather than local GIF previews.

## Example Layout

The `examples/` directory is organized by audience:

- top-level `examples/`: first-run and release-facing examples
- `examples/reference/`: readable reference kernels and fixture builders
- `examples/generated/`: preserved generated bundles and generated example output
- `examples/visual_demo/`: RTDL-plus-Python application demos
- `examples/internal/`: preserved internal and historical artifacts

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
- the live **released v0.2.0 state on `main`**

The v0.1 anchor remains the bounded, reviewed RayJoin-heavy research slice.

Current `main` is broader than that archived slice. The accepted v0.2.0 surface
is exactly:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

Plus:

- the current narrow generate-only surface
- the feature-home documentation layer
- Linux-backed correctness/performance evidence
- explicit fallback-vs-native backend honesty boundaries

Current `main` therefore:

- keeps the accepted v0.1 surface
- adds two closed segment/polygon workload families:
  - `segment_polygon_hitcount`
  - `segment_polygon_anyhit_rows`
- adds a narrow Jaccard line:
  - `polygon_pair_overlap_area_rows`
  - `polygon_set_jaccard`
- for that Jaccard line, the public `embree`, `optix`, and `vulkan` run
  surfaces now accept the workloads through documented native CPU/oracle
  fallback on Linux
- adds a narrow generate-only product line covering the segment/polygon
  families plus one authored Jaccard entry
- has Linux/PostGIS-backed correctness and performance evidence for those
  families
- keeps Linux as the primary validation platform
- keeps local macOS as a limited platform

Current `main` still does **not** mean:

- every backend/workload path is equally mature
- exact computational geometry everywhere
- full polygon overlay materialization
- native Embree/OptiX/Vulkan Jaccard kernels
- that every possible future workload/application shape is already first-class

## Release Reports

The canonical released v0.2.0 package is here:

- [RTDL v0.2 Release Reports](docs/release_reports/v0_2/README.md)

The archived v0.1 trust-anchor package is here:

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

- [Workloads And Research Foundations](docs/workloads_and_research_foundations.md)
- [Future Ray-Tracing Directions](docs/future_ray_tracing_directions.md)

## Where To Start

If you are new to the project, start here:

1. [Docs Index](docs/README.md)
2. [RTDL v0.2 User Guide](docs/v0_2_user_guide.md)
3. [Release-Facing Examples](docs/release_facing_examples.md)
4. [Quick Tutorial](docs/quick_tutorial.md)
5. [Feature Homes](docs/features/README.md)

## Project Status

This repository is maintained as a reviewed research/engineering workspace.
Source code, reports, tests, and review artifacts are kept together so the
current RTDL v0.1 trust anchor and released v0.2.0 package remain
understandable and auditable.

Copyright (c) 2026 Rubao Lee. All rights reserved. RTDL and this repository
are owned and maintained by Rubao Lee.
