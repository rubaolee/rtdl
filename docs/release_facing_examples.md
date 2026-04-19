# Release-Facing Examples

This page is the canonical example index for the release-facing `examples/`
surface.

It currently covers:

- the released `v0.2.0` geometry workloads
- the released `v0.4.0` nearest-neighbor line
- the released `v0.6.1` RT graph line
- the released bounded `v0.7.0` DB line
- the released `v0.8.0` app-building line on `main` over existing RTDL features
- the released `v0.9.0` HIPRT example, clearly marked as a Linux/HIPRT-SDK
  path with explicit platform boundaries
- the released `v0.9.1` Apple RT example, clearly marked as a
  bounded macOS/Apple-Silicon closest-hit slice

Use these first if you want the examples that best match the current accepted
live workload/package story.

If you want a guided learning order instead of a flat example list, start with:

- [RTDL Tutorials](tutorials/README.md)
- [v0.8 App Building](tutorials/v0_8_app_building.md)

## Choose By Job

| Job | Example | Why this is the right first file |
| --- | --- | --- |
| Verify the checkout runs | `examples/rtdl_hello_world.py` | smallest possible command |
| Learn one kernel across backends | `examples/rtdl_hello_world_backends.py` | shows backend selection without changing the kernel idea |
| Learn every feature shape quickly | `examples/rtdl_feature_quickstart_cookbook.py` | one compact CPU Python reference recipe per public feature |
| Spatial/geometric query | `examples/rtdl_segment_polygon_hitcount.py` | released segment/polygon workload |
| Nearest-neighbor query | `examples/rtdl_fixed_radius_neighbors.py` | released v0.4 nearest-neighbor surface |
| Paper-derived spatial metric app | `examples/rtdl_hausdorff_distance_app.py` | two point sets become nearest-neighbor rows and one Hausdorff distance |
| Paper-derived ANN candidate app | `examples/rtdl_ann_candidate_app.py` | queries and an approximate candidate subset become nearest rows plus recall metrics |
| Paper-derived outlier app | `examples/rtdl_outlier_detection_app.py` | points become density-neighbor rows and outlier labels |
| Paper-derived density clustering app | `examples/rtdl_dbscan_clustering_app.py` | points become fixed-radius neighbor rows and DBSCAN labels |
| Paper-derived robot screening app | `examples/rtdl_robot_collision_screening_app.py` | robot link edge rays become pose collision flags |
| Paper-derived force approximation app | `examples/rtdl_barnes_hut_force_app.py` | bodies and quadtree nodes become candidate rows and approximate force vectors |
| Graph traversal | `examples/rtdl_graph_bfs.py` | frontier data becomes discovered vertices |
| Graph intersection | `examples/rtdl_graph_triangle_count.py` | edge probes become triangle rows |
| Bounded DB filter | `examples/rtdl_db_conjunctive_scan.py` | denormalized rows plus predicates become row IDs |
| Bounded DB aggregate | `examples/rtdl_db_grouped_count.py` / `examples/rtdl_db_grouped_sum.py` | filtered rows become grouped results |
| App integration | `examples/rtdl_v0_7_db_app_demo.py` | Python app stays thin around the RTDL query core |
| HIPRT example | `examples/rtdl_hiprt_ray_triangle_hitcount.py` | 3D rays and 3D triangles become per-ray hit-count rows through `run_hiprt` / `prepare_hiprt` |
| Apple RT example | `examples/rtdl_apple_rt_closest_hit.py` | 3D rays and 3D triangles become nearest-hit rows through `run_apple_rt` |

This is the practical burden reduction: you choose the workload shape and
backend flag; RTDL keeps traversal/refinement/result plumbing consistent.

Before running any command below:

- clone the repo with `git clone https://github.com/rubaolee/rtdl.git`
- enter the checkout with `cd rtdl`
- create a virtual environment and install requirements once:
  - macOS/Linux:
    - `python3 -m venv .venv`
    - `source .venv/bin/activate`
  - Windows:
    - `py -3 -m venv .venv`
    - `.venv\Scripts\activate` in `cmd.exe`
    - `.venv\Scripts\Activate.ps1` in PowerShell
  - then:
    - `python -m pip install --upgrade pip`
    - `python -m pip install -r requirements.txt`
- on Debian/Ubuntu, if `python3 -m venv` fails because `ensurepip` is
  unavailable, install `python3-venv` first:
  - `sudo apt install python3-venv`
- keep the `PYTHONPATH=src:.` prefix so Python imports the local `rtdsl`
  package from `src/rtdsl/`
- commands below use `python` as the public convention
- if your shell only provides `python3`, substitute `python3` for `python`
- optional Embree build/probe: `make build-embree`
- optional v0.9 HIPRT build on Linux:
  `make build-hiprt HIPRT_PREFIX=/path/to/hiprtSdk`
- optional v0.9.1 Apple RT build on Apple Silicon macOS:
  `make build-apple-rt`
- Windows Embree users should set `RTDL_EMBREE_PREFIX` to an x64 Embree prefix
  and `RTDL_VCVARS64` if Visual Studio Build Tools are not in the default
  location; copied binary snapshots must carry the matching
  `build/librtdl_embree.dll` or allow first-use rebuild from source

Windows shell note:

- `cmd.exe`:
  - `set PYTHONPATH=src;.`
- PowerShell:
  - `$env:PYTHONPATH = "src;."`

Then run the same `python ...` command from the repo root.

## Feature Cookbook

Run one compact recipe for every current public feature:

```bash
PYTHONPATH=src:. python examples/rtdl_feature_quickstart_cookbook.py
```

Read the companion tutorial:

- [Feature Quickstart Cookbook](tutorials/feature_quickstart_cookbook.md)

## v0.8 App-Building Examples

The `v0.8` app line demonstrates complete Python applications that reuse
existing RTDL row kernels instead of changing language internals first.

Read the tutorial:

- [v0.8 App Building](tutorials/v0_8_app_building.md)

Run the portable app suite:

```bash
PYTHONPATH=src:. python examples/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_ann_candidate_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_outlier_detection_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_dbscan_clustering_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_robot_collision_screening_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_barnes_hut_force_app.py --backend cpu_python_reference
```

Linux users with built backend libraries can also run the Hausdorff app through
RTDL's native nearest-neighbor backends:

```bash
PYTHONPATH=src:. python examples/rtdl_hausdorff_distance_app.py --backend embree
PYTHONPATH=src:. python examples/rtdl_hausdorff_distance_app.py --backend optix
PYTHONPATH=src:. python examples/rtdl_hausdorff_distance_app.py --backend vulkan
```

Performance evidence:

- [Goal507 Hausdorff Linux Performance Report](reports/goal507_hausdorff_linux_perf_report_2026-04-17.md)
- [Goal509 Robot/Barnes-Hut Linux Performance Report](reports/goal509_robot_barnes_linux_perf_report_2026-04-17.md)
- [Goal524 Stage-1 Proximity Linux Performance Report](reports/goal524_v0_8_stage1_proximity_linux_perf_2026-04-17.md)

Boundary: the Goal507 Linux evidence shows working multi-backend RTDL execution
and strong OptiX/Vulkan speedups over RTDL Embree, but it does not show RTDL
beating mature exact 2D nearest-neighbor baselines such as SciPy `cKDTree` or
FAISS `IndexFlatL2`.

Goal509 covers the robot collision screening and Barnes-Hut apps. It accepts
CPU/Embree/OptiX for robot collision screening, rejects robot Vulkan because it
fails per-edge hit-count parity, and accepts CPU/Embree/OptiX/Vulkan for
Barnes-Hut candidate generation while keeping Python force reduction separate.

Goal524 characterizes the ANN candidate, outlier detection, and DBSCAN apps on
Linux across RTDL CPU/oracle, Embree, OptiX, and Vulkan backends. It does not
claim a speedup against SciPy, scikit-learn, FAISS, or production ANN,
anomaly-detection, or clustering systems; SciPy was not installed in the Linux
validation checkout used for that artifact.

## HIPRT Backend

This released v0.9.0 path is for Linux users with the HIPRT SDK installed. It
is bounded by the v0.9 support matrix: validated through HIPRT/Orochi CUDA mode
on the Linux NVIDIA host, without AMD GPU validation, HIPRT CPU fallback, or
RT-core speedup claims from the tested GTX 1070 path.

Build and run:

```bash
make build-hiprt HIPRT_PREFIX=/path/to/hiprtSdk
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
export LD_LIBRARY_PATH=/path/to/hiprtSdk/hiprt/linux64:${LD_LIBRARY_PATH:-}
PYTHONPATH=src:. python examples/rtdl_hiprt_ray_triangle_hitcount.py
```

The example first computes a CPU Python reference answer, then attempts HIPRT.
If the HIPRT backend library or runtime is unavailable, it prints a JSON result
with `hiprt_available: false` and exits successfully. If HIPRT is available, it
checks both one-shot `run_hiprt` and repeated-query `prepare_hiprt` parity for
the prepared 3D ray/triangle path.

Current HIPRT boundary:

- `run_hiprt` support: 18 Linux-parity workloads across geometry, 2D
  geometry, nearest-neighbor, graph, and bounded DB-style analytics
- `prepare_hiprt` support: prepared 3D `ray_triangle_hit_count` and
  prepared 3D `fixed_radius_neighbors`, plus prepared graph CSR reuse for
  `bfs_discover` and `triangle_match`
- unsupported claims: AMD GPU validation, RT-core speedup evidence from the
  tested GTX 1070 path, CPU fallback, and OptiX/Vulkan/HIPRT native
  `ray_triangle_closest_hit`

## Apple RT Backend

This released v0.9.1 path is for Apple Silicon macOS users. It is
bounded by Goal578: one 3D closest-hit ray/triangle workload through Apple
Metal/MPS `MPSRayIntersector`.

Build and run:

```bash
make build-apple-rt
PYTHONPATH=src:. python examples/rtdl_apple_rt_closest_hit.py
```

The example first computes a CPU Python reference answer, then attempts Apple
RT. If the Apple RT backend library is unavailable, it prints a JSON result
with `apple_rt_available: false` and exits successfully. If Apple RT is
available, it checks approximate row parity for `run_apple_rt`.

Current Apple RT boundary:

- released `run_apple_rt` native support: 3D `ray_triangle_closest_hit`
- post-`v0.9.1` Goal582 dispatch support: all 18 current predicates are
  callable through `run_apple_rt`, with non-closest-hit predicates explicitly
  marked `cpu_reference_compat`
- validated locally on Apple M4 through Goal578 focused tests and Gemini/Claude
  reviews; Goal582 adds a full-surface dispatch parity test
- unsupported claims: full native Apple backend parity, Apple hardware speedup
  evidence, non-macOS support, and hardware-backed Apple support for the
  broader workload matrix

## v0.4 nearest-neighbor examples

These are the release-facing examples for the released `v0.4.0` nearest-neighbor line.
They are correctness-first nearest-neighbor examples, not a benchmark claim.

### Fixed-Radius Neighbors

- code:
  - [rtdl_fixed_radius_neighbors.py](../examples/rtdl_fixed_radius_neighbors.py)
- run:

```bash
PYTHONPATH=src:. python examples/rtdl_fixed_radius_neighbors.py --backend cpu_python_reference
```

### K-Nearest-Neighbor Rows

- code:
  - [rtdl_knn_rows.py](../examples/rtdl_knn_rows.py)
- run:

```bash
PYTHONPATH=src:. python examples/rtdl_knn_rows.py --backend cpu_python_reference
```

### App-Style Nearest-Neighbor Examples

Code:

- [rtdl_service_coverage_gaps.py](../examples/rtdl_service_coverage_gaps.py)
- [rtdl_event_hotspot_screening.py](../examples/rtdl_event_hotspot_screening.py)
- [rtdl_facility_knn_assignment.py](../examples/rtdl_facility_knn_assignment.py)
- [rtdl_hausdorff_distance_app.py](../examples/rtdl_hausdorff_distance_app.py)
- [rtdl_ann_candidate_app.py](../examples/rtdl_ann_candidate_app.py)
- [rtdl_outlier_detection_app.py](../examples/rtdl_outlier_detection_app.py)
- [rtdl_dbscan_clustering_app.py](../examples/rtdl_dbscan_clustering_app.py)

Run:

```bash
PYTHONPATH=src:. python examples/rtdl_service_coverage_gaps.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_ann_candidate_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_outlier_detection_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_dbscan_clustering_app.py --backend cpu_python_reference
```

The Hausdorff app is the first Goal499 paper-derived app pattern: RTDL emits
k=1 nearest-neighbor rows and Python reduces them to directed and undirected
Hausdorff scalars. It is not a claim to implement all X-HD paper optimizations.
On Linux, Goal507 adds bounded Embree/OptiX/Vulkan performance evidence against
SciPy, scikit-learn, and FAISS nearest-neighbor baselines.

The DBSCAN app is the first Goal519 Stage-1 proximity workload: RTDL emits
fixed-radius neighbor rows and Python performs DBSCAN core, border, noise, and
cluster-expansion logic. It is not a claim that RTDL is a full clustering
engine.

The ANN and outlier apps complete the currently supportable Stage-1 proximity
set from Goal519: ANN uses `knn_rows(k=1)` over a Python-selected approximate
candidate subset, and outlier detection uses `fixed_radius_neighbors` plus
Python density thresholding. Neither app claims a full ANN index or anomaly
detection framework.

On Linux, Goal524 adds bounded CPU/oracle, Embree, OptiX, and Vulkan timing
characterization for these three Stage-1 proximity apps. It is a
within-RTDL-backend characterization, not a competitive external-baseline claim.

See [v0.4 Application Examples](v0_4_application_examples.md) for full descriptions and SQL comparisons.

## Goal499 Robot Collision Screening App

The discrete collision screening app is the second Goal499 paper-derived app
pattern. RTDL emits per-edge ray/triangle hit counts; Python maps edge rays back
to pose/link IDs and reports which poses collide.

Code:

- [rtdl_robot_collision_screening_app.py](../examples/rtdl_robot_collision_screening_app.py)

Run:

```bash
PYTHONPATH=src:. python examples/rtdl_robot_collision_screening_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_robot_collision_screening_app.py --backend embree
PYTHONPATH=src:. python examples/rtdl_robot_collision_screening_app.py --backend optix
```

Boundary:

- this is bounded 2D discrete-pose screening
- this is not continuous swept-volume CCD
- this is not full robot kinematics or a full mesh collision engine
- Vulkan is not a supported public backend for this app yet because Goal509
  found a per-edge hit-count correctness mismatch

## Goal499 Barnes-Hut Force App

The Barnes-Hut app is the third Goal499 paper-derived app pattern. It is also
the first one that exposes a real language gap. Current RTDL can emit
body-to-node candidate rows with existing nearest-neighbor machinery, but Python
still owns quadtree construction, the Barnes-Hut opening rule, force-vector
calculation, and oracle comparison.

Code:

- [rtdl_barnes_hut_force_app.py](../examples/rtdl_barnes_hut_force_app.py)

Run:

```bash
PYTHONPATH=src:. python examples/rtdl_barnes_hut_force_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_barnes_hut_force_app.py --backend embree
PYTHONPATH=src:. python examples/rtdl_barnes_hut_force_app.py --backend optix
PYTHONPATH=src:. python examples/rtdl_barnes_hut_force_app.py --backend vulkan
```

Boundary:

- this is a bounded one-level 2D approximation
- this is not a faithful RT-BarnesHut implementation
- RTDL does not yet expose hierarchical tree-node primitives
- RTDL does not yet expose a Barnes-Hut opening predicate
- RTDL does not yet expose grouped vector force reductions
- Goal509 performance evidence times RTDL candidate generation separately from
  full-app Python force reduction; do not read it as full N-body acceleration

## v0.6.1 RT graph line

The released `v0.6.1` graph workloads are:

- `bfs`
- `triangle_count`

Graph docs and package:

- [v0.6 Release Package](release_reports/v0_6/README.md)
- [v0.6 Release Statement](release_reports/v0_6/release_statement.md)
- [v0.6 Support Matrix](release_reports/v0_6/support_matrix.md)

Release-facing graph examples:

- [rtdl_graph_bfs.py](../examples/rtdl_graph_bfs.py)
- [rtdl_graph_triangle_count.py](../examples/rtdl_graph_triangle_count.py)

Run:

```bash
PYTHONPATH=src:. python examples/rtdl_graph_bfs.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_graph_bfs.py --backend cpu

PYTHONPATH=src:. python examples/rtdl_graph_triangle_count.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_graph_triangle_count.py --backend cpu
```

If Embree is available:

```bash
PYTHONPATH=src:. python examples/rtdl_graph_bfs.py --backend embree
PYTHONPATH=src:. python examples/rtdl_graph_triangle_count.py --backend embree
```

On Linux hosts with the GPU stack enabled:

```bash
make build-optix
make build-vulkan

PYTHONPATH=src:. python examples/rtdl_graph_bfs.py --backend optix
PYTHONPATH=src:. python examples/rtdl_graph_bfs.py --backend vulkan
PYTHONPATH=src:. python examples/rtdl_graph_triangle_count.py --backend optix
PYTHONPATH=src:. python examples/rtdl_graph_triangle_count.py --backend vulkan
```

Reference validation/report surfaces:

- [goal389_v0_6_rt_graph_bfs_truth_path_test.py](../tests/goal389_v0_6_rt_graph_bfs_truth_path_test.py)
- [goal390_v0_6_rt_graph_triangle_truth_path_test.py](../tests/goal390_v0_6_rt_graph_triangle_truth_path_test.py)
- [graph_rt_validation_and_perf_report_2026-04-14.md](graph_rt_validation_and_perf_report_2026-04-14.md)

## v0.7.0 bounded DB line

The released `v0.7.0` DB line provides the first bounded database-style RTDL
kernel family. These examples are runnable release-facing entry points.

Kernel examples:

- [rtdl_db_conjunctive_scan.py](../examples/rtdl_db_conjunctive_scan.py)
- [rtdl_db_grouped_count.py](../examples/rtdl_db_grouped_count.py)
- [rtdl_db_grouped_sum.py](../examples/rtdl_db_grouped_sum.py)

App-style example:

- [rtdl_sales_risk_screening.py](../examples/rtdl_sales_risk_screening.py)
- [rtdl_v0_7_db_app_demo.py](../examples/rtdl_v0_7_db_app_demo.py)
- [rtdl_v0_7_db_kernel_app_demo.py](../examples/rtdl_v0_7_db_kernel_app_demo.py)

Run:

```bash
PYTHONPATH=src:. python examples/rtdl_db_conjunctive_scan.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_db_conjunctive_scan.py --backend cpu

PYTHONPATH=src:. python examples/rtdl_db_grouped_count.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_db_grouped_count.py --backend cpu

PYTHONPATH=src:. python examples/rtdl_db_grouped_sum.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_db_grouped_sum.py --backend cpu
PYTHONPATH=src:. python examples/rtdl_db_conjunctive_scan.py --backend embree
PYTHONPATH=src:. python examples/rtdl_db_grouped_count.py --backend embree
PYTHONPATH=src:. python examples/rtdl_db_grouped_sum.py --backend embree

PYTHONPATH=src:. python examples/rtdl_sales_risk_screening.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_sales_risk_screening.py --backend cpu
PYTHONPATH=src:. python examples/rtdl_sales_risk_screening.py --backend embree
PYTHONPATH=src:. python examples/rtdl_v0_7_db_app_demo.py --backend auto
PYTHONPATH=src:. python examples/rtdl_v0_7_db_kernel_app_demo.py --backend auto
```

On Linux hosts with the GPU stack enabled:

```bash
make build-optix
make build-vulkan

PYTHONPATH=src:. python examples/rtdl_db_conjunctive_scan.py --backend optix
PYTHONPATH=src:. python examples/rtdl_db_conjunctive_scan.py --backend vulkan
PYTHONPATH=src:. python examples/rtdl_db_grouped_count.py --backend optix
PYTHONPATH=src:. python examples/rtdl_db_grouped_count.py --backend vulkan
PYTHONPATH=src:. python examples/rtdl_db_grouped_sum.py --backend optix
PYTHONPATH=src:. python examples/rtdl_db_grouped_sum.py --backend vulkan
PYTHONPATH=src:. python examples/rtdl_sales_risk_screening.py --backend optix
PYTHONPATH=src:. python examples/rtdl_sales_risk_screening.py --backend vulkan
```

Current honesty boundary:

- the public DB example surface now exposes:
  - `cpu_python_reference`
  - `cpu`
  - `embree`
  - `optix`
  - `vulkan`
- PostgreSQL is the Linux correctness anchor, not a public example backend flag
- native prepared DB dataset APIs exist for Embree, OptiX, and Vulkan, but the
  public example CLIs intentionally stay small and show the normal backend flag
  path first
- Linux columnar repeated-query performance evidence is now canonically
  summarized in
  [Goal 452](reports/goal452_v0_7_rtdl_vs_best_tested_postgresql_perf_rebase_2026-04-16.md):
  query-only results are mixed against the best PostgreSQL modes tested so far,
  while setup-plus-10-query total time favors RTDL in the measured Linux
  evidence
- Goal 492 records the final release-readiness hold before explicit `v0.7.0`
  release authorization
- `v0.7.0` is now the current tagged mainline release; claims remain bounded by
  the v0.7 release reports and support matrix

### Public CLI Backend Selection

The public nearest-neighbor example CLIs currently support:

```bash
PYTHONPATH=src:. python examples/rtdl_fixed_radius_neighbors.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_fixed_radius_neighbors.py --backend cpu
PYTHONPATH=src:. python examples/rtdl_fixed_radius_neighbors.py --backend embree

PYTHONPATH=src:. python examples/rtdl_knn_rows.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_knn_rows.py --backend cpu
PYTHONPATH=src:. python examples/rtdl_knn_rows.py --backend embree
```

Important boundary:

- OptiX and Vulkan nearest-neighbor closure exists in the runtime and test
  surface
- `examples/rtdl_fixed_radius_neighbors.py` and `examples/rtdl_knn_rows.py`
  still expose only `cpu_python_reference`, `cpu`, and `embree`
- `examples/rtdl_hausdorff_distance_app.py` now exposes `embree`, `optix`, and
  `vulkan` because Goal507 validates that app-specific path on Linux
- `examples/rtdl_robot_collision_screening_app.py` exposes `embree` and
  `optix`, but not `vulkan`, because Goal509 rejects robot Vulkan parity
- `examples/rtdl_barnes_hut_force_app.py` exposes `embree`, `optix`, and
  `vulkan`, but Goal509 reports candidate-generation timing separately from
  Python force-reduction timing
- do not generalize the Hausdorff app's GPU CLI support into a release claim
  for every nearest-neighbor example script

Windows PowerShell example:

```powershell
$env:PYTHONPATH = "src;."
python examples/rtdl_fixed_radius_neighbors.py --backend cpu_python_reference
python examples/rtdl_fixed_radius_neighbors.py --backend cpu
python examples/rtdl_fixed_radius_neighbors.py --backend embree
```

## Core examples

### Segment/Polygon Hit Count

- code:
  - [rtdl_segment_polygon_hitcount.py](../examples/rtdl_segment_polygon_hitcount.py)
- run:

```bash
PYTHONPATH=src:. python examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 16
```

### Segment/Polygon Any-Hit Rows

- code:
  - [rtdl_segment_polygon_anyhit_rows.py](../examples/rtdl_segment_polygon_anyhit_rows.py)
- run:

```bash
PYTHONPATH=src:. python examples/rtdl_segment_polygon_anyhit_rows.py --backend cpu_python_reference --copies 16
```

### Polygon-Set Jaccard

- code:
  - [rtdl_polygon_set_jaccard.py](../examples/rtdl_polygon_set_jaccard.py)
- run:

```bash
PYTHONPATH=src:. python examples/rtdl_polygon_set_jaccard.py
```

### Polygon-Pair Overlap Area Rows

- code:
  - [rtdl_polygon_pair_overlap_area_rows.py](../examples/rtdl_polygon_pair_overlap_area_rows.py)
- run:

```bash
PYTHONPATH=src:. python examples/rtdl_polygon_pair_overlap_area_rows.py
```

## App-style example

- [rtdl_road_hazard_screening.py](../examples/rtdl_road_hazard_screening.py)

This is the best short example of how the segment/polygon line looks in a more
user-facing workflow.

## RTDL Plus Python App Demo

Primary 3D demo source:

- [rtdl_hidden_star_stable_ball_demo.py](../examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py)

This is the current main 3D RTDL-plus-Python demo source. RTDL handles both:

- primary camera hit queries
- shadow visibility queries

Python still owns the surrounding application layer: animation, shading,
background, and frame output.

Primary hidden-star stable 3D demo sanity check:

```bash
PYTHONPATH=src:. python examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py --backend cpu_python_reference --compare-backend none --width 48 --height 48 --latitude-bands 6 --longitude-bands 12 --frames 1 --jobs 1 --shadow-mode rtdl_light_to_surface --output-dir build/quick_hidden_star_demo
```

Secondary smaller app demo:

- [rtdl_lit_ball_demo.py](../examples/visual_demo/rtdl_lit_ball_demo.py)

This is a small user-authored RTDL-plus-Python application. RTDL handles the
ray/triangle hit relationships. Python handles the visible-span recovery,
brightness calculation, ASCII preview, and `.pgm` image output.

The visual-demo scripts create the output directory automatically when needed,
so an empty fresh clone does not need a pre-existing `build/` directory.

Run:

```bash
PYTHONPATH=src:. python examples/visual_demo/rtdl_lit_ball_demo.py --backend cpu_python_reference --compare-backend none --width 240 --height 240 --triangles 512 --output build/rtdl_lit_ball_demo_hq.pgm
```

Small first sanity check for the smoother comparison line:

```bash
PYTHONPATH=src:. python examples/visual_demo/rtdl_smooth_camera_orbit_demo.py --backend cpu_python_reference --compare-backend none --width 48 --height 48 --latitude-bands 6 --longitude-bands 12 --frames 1 --jobs 1 --output-dir build/quick_smooth_camera_demo
```

Important boundary:

- this is a user-level RTDL-plus-Python application demo
- it is not a claim that RTDL v0.2.0 is a full rendering system

## Generate-only entry point

- script:
  - [rtdl_generate_only.py](../scripts/rtdl_generate_only.py)

Current accepted narrow generate-only example:

```bash
PYTHONPATH=src:. python scripts/rtdl_generate_only.py --workload polygon_set_jaccard --dataset authored_polygon_set_jaccard_minimal --backend cpu_python_reference --output-mode rows --artifact-shape handoff_bundle --output build/generated_polygon_set_jaccard_bundle
```

The repo also preserves example generated output under:

- [examples/generated/](../examples/generated/README.md)

Those files are useful for inspection and handoff workflows, but they are not
the main first-run entry points for new users.

## Notes

- these are the release-facing examples for the current released RTDL line
- if you cloned the repo as `rtdl`, every command above is intended to work
  from that clone root
- do not prepend another `cd rtdl` after you are already at the checkout root
- older demos and exploratory examples still exist in the repo, but they are
  not the primary release-facing entry points
