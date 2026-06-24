# v0.8 App Building

`v0.8` is about building useful applications from the existing RTDL language
surface before adding new primitives.

The programming model is the same ITRE shape used by the current language:
`input -> traverse -> refine -> emit`. For the app line, that means RTDL owns
the heavy query/traversal kernel and Python owns the surrounding app. For the
full boundary, read [ITRE App Programming Model](../rtdl/itre_app_model.md).

The pattern is:

1. Python prepares domain data.
2. RTDL emits reusable query rows.
3. Python reduces those rows into application answers.
4. If the app exposes a reusable missing primitive, document the gap before
   changing the language.

This keeps RTDL useful without turning every paper into a one-off language
feature.

## What Data Becomes What Data?

| App | Python input | RTDL row output | Python app output |
| --- | --- | --- | --- |
| Hausdorff distance | two point sets | `knn_rows(k=1)` nearest-neighbor rows in both directions | directed and undirected Hausdorff distance plus witness IDs |
| ANN candidate search | queries, full search points, and a Python-selected candidate subset | `knn_rows(k=1)` rows over the candidate subset | recall and distance-ratio comparison against exact brute-force search |
| Outlier detection | point cloud plus radius/density constants | `fixed_radius_neighbors` rows over the point cloud | local density rows and outlier IDs |
| DBSCAN clustering | point cloud plus `epsilon` / `min_points` constants | `fixed_radius_neighbors` rows over the point cloud | cluster labels, core flags, noise IDs, and brute-force oracle comparison |
| Robot collision screening | robot link edge rays plus obstacle triangles | per-edge ray/triangle hit-count rows | colliding pose IDs and pose summaries |
| Barnes-Hut force approximation | bodies plus Python-built quadtree nodes | body-to-node candidate rows | accepted nodes, exact fallback bodies, approximate force vectors, and oracle error |

## Run The App Suite

All commands below use `cpu_python_reference` so they run on a fresh checkout
without requiring native backend libraries.

```bash
PYTHONPATH=src:. python examples/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_ann_candidate_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_outlier_detection_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_dbscan_clustering_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_robot_collision_screening_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_barnes_hut_force_app.py --backend cpu_python_reference
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_hausdorff_distance_app.py --backend cpu_python_reference
python examples\rtdl_ann_candidate_app.py --backend cpu_python_reference
python examples\rtdl_outlier_detection_app.py --backend cpu_python_reference
python examples\rtdl_dbscan_clustering_app.py --backend cpu_python_reference
python examples\rtdl_robot_collision_screening_app.py --backend cpu_python_reference
python examples\rtdl_barnes_hut_force_app.py --backend cpu_python_reference
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src;."
python examples/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
python examples/rtdl_ann_candidate_app.py --backend cpu_python_reference
python examples/rtdl_outlier_detection_app.py --backend cpu_python_reference
python examples/rtdl_dbscan_clustering_app.py --backend cpu_python_reference
python examples/rtdl_robot_collision_screening_app.py --backend cpu_python_reference
python examples/rtdl_barnes_hut_force_app.py --backend cpu_python_reference
```

## App 1: Hausdorff Distance

Use when you have two point sets and want the largest nearest-neighbor distance
between them.

RTDL owns:

- nearest-neighbor rows from set `A` to set `B`
- nearest-neighbor rows from set `B` to set `A`

Python owns:

- loading point sets
- directed max reduction
- undirected max selection
- witness IDs
- brute-force oracle comparison

Boundary:

- this is not the full X-HD optimization stack
- no grid-cell pruning, prepared point-set reuse, or GPU load-balancing path is
  claimed

Linux performance evidence:

- [Goal507 Hausdorff Linux Performance Report](../reports/goal507_hausdorff_linux_perf_report_2026-04-17.md)
- bounded readout: RTDL OptiX/Vulkan beat RTDL Embree for this app on the
  measured Linux host, but SciPy `cKDTree` and FAISS `IndexFlatL2` remain
  stronger exact 2D nearest-neighbor baselines in that evidence

## App 2: ANN Candidate Search

Use when you want an honest approximate-nearest-neighbor example without
claiming RTDL has a full ANN index. This is candidate-subset kNN reranking:
Python chooses a candidate subset, and RTDL ranks that subset.

RTDL owns:

- nearest-neighbor rows over a Python-selected candidate subset
- optional OptiX prepared fixed-radius candidate-coverage decisions

Python owns:

- candidate-subset selection
- exact brute-force comparison against the full search set
- recall and distance-ratio reporting

OptiX decision mode:

```bash
PYTHONPATH=src:. python examples/rtdl_ann_candidate_app.py \
  --backend optix \
  --optix-summary-mode candidate_threshold_prepared \
  --candidate-radius 0.2 \
  --require-rt-core
```

Boundary:

- this is a bounded candidate-search demo
- `candidate_threshold_prepared` answers "does each query have a candidate
  within radius"; it does not return the nearest candidate
- this is not FAISS, HNSW, IVF, or a trained ANN index
- RTDL does not yet expose ANN index construction, recall tuning, or
  latency/quality optimization

Linux performance evidence:

- [Goal524 Stage-1 Proximity Linux Performance Report](../reports/goal524_v0_8_stage1_proximity_linux_perf_2026-04-17.md)
- bounded readout: RTDL CPU/oracle, Embree, OptiX, and Vulkan all pass with
  stable recall and distance-ratio metrics on the measured fixture; this is
  not an external ANN-baseline claim because SciPy was not installed in that
  validation checkout and FAISS/HNSW-style indexes were not timed

## App 3: Outlier Detection

Use when you want to classify points by local density.

RTDL owns:

- fixed-radius neighbor rows over the point cloud

Python owns:

- local neighbor-count aggregation
- thresholding into outlier labels
- brute-force oracle comparison

Boundary:

- this is bounded density-threshold outlier detection
- this is not a full anomaly-detection framework
- RTDL does not yet expose density scoring as a language primitive

Linux performance evidence:

- [Goal524 Stage-1 Proximity Linux Performance Report](../reports/goal524_v0_8_stage1_proximity_linux_perf_2026-04-17.md)
- bounded readout: RTDL CPU/oracle, Embree, OptiX, and Vulkan all match the
  brute-force oracle on the measured fixture; this is not a claim against
  SciPy, scikit-learn, or production anomaly-detection systems

## App 4: DBSCAN Clustering

Use when you want to see how a density-clustering workload can be written as
RTDL neighbor-row generation plus Python graph expansion.

RTDL owns:

- fixed-radius neighbor rows over the point cloud
- grouped neighbor-count reduction with `rt.reduce_rows(count)`

Python owns:

- DBSCAN core-point classification from reduced counts
- cluster expansion
- border/noise labeling
- brute-force oracle comparison

Boundary:

- this is a bounded app-level DBSCAN demo
- this is not a clustering engine
- RTDL does not yet expose clustering expansion or connected-component
  reductions as language primitives

Linux performance evidence:

- [Goal524 Stage-1 Proximity Linux Performance Report](../reports/goal524_v0_8_stage1_proximity_linux_perf_2026-04-17.md)
- bounded readout: RTDL CPU/oracle, Embree, OptiX, and Vulkan all match the
  brute-force oracle on the measured fixture; this is not a claim against
  scikit-learn DBSCAN or production clustering systems

## App 5: Robot Collision Screening

Use when you have a small discrete pose batch and want to screen which poses
collide with obstacle geometry.

RTDL owns:

- ray/triangle any-hit rows for link edge rays
- pose-level boolean reduction with `rt.reduce_rows(any)`

Python owns:

- pose batch construction
- link edge-ray generation
- pose/link metadata
- witness edge/ray summaries

Boundary:

- this is bounded 2D discrete-pose screening
- this is not full robot kinematics
- this is not continuous swept-volume CCD
- this is not a full mesh collision engine

Linux performance evidence:

- [Goal509 Robot/Barnes-Hut Linux Performance Report](../reports/goal509_robot_barnes_linux_perf_report_2026-04-17.md)
- bounded readout: Goal509 recorded the earlier hit-count formulation. The
  current app has been rewritten to v0.9.5 any-hit plus `reduce_rows`; keep
  native early-exit speedup claims limited to engines that actually implement
  native any-hit.

## App 6: Barnes-Hut Force Approximation

Use when you want to see how far existing RTDL rows can go on hierarchical
simulation-style workloads.

RTDL owns:

- body-to-node candidate rows through existing nearest-neighbor machinery

Python owns:

- quadtree construction
- node center-of-mass metadata
- Barnes-Hut opening rule
- force-vector math
- exact fallback and brute-force oracle comparison

Boundary:

- this is a bounded one-level 2D approximation
- this is not a faithful RT-BarnesHut implementation
- RTDL does not yet expose hierarchical tree-node types
- RTDL does not yet expose a Barnes-Hut opening predicate
- RTDL does not yet expose grouped vector reductions for force accumulation

Linux performance evidence:

- [Goal509 Robot/Barnes-Hut Linux Performance Report](../reports/goal509_robot_barnes_linux_perf_report_2026-04-17.md)
- bounded readout: CPU, Embree, OptiX, and Vulkan match the candidate-generation
  and full-app reference checks in the measured evidence; RTDL candidate timing
  is reported separately because Python still owns opening-rule and force
  reduction work

## What v0.8 Proved So Far

The current language surface is already enough to write non-trivial apps when
Python handles orchestration and reductions:

- `knn_rows` supports spatial metric apps.
- `knn_rows` can also support bounded ANN candidate-search demos when Python
  owns candidate-set construction and approximation-quality evaluation.
- `fixed_radius_neighbors` supports density-neighborhood apps such as DBSCAN.
- `fixed_radius_neighbors` supports density-threshold outlier detection.
- `ray_triangle_any_hit` plus `rt.reduce_rows(any)` supports bounded
  collision-screening apps when only yes/no collision flags are required.
- `rt.reduce_rows(count)` supports density/core-count app glue without adding
  clustering expansion to the language core.
- `fixed_radius_neighbors` supports candidate discovery in a hierarchical
  approximation app.

The Barnes-Hut app also shows the first concrete `v0.8` language-growth
pressure: future RTDL may need tree-node inputs, opening predicates, and vector
reductions if hierarchical simulation apps become a release target.

## Next

- [ITRE App Programming Model](../rtdl/itre_app_model.md)
- [Feature Quickstart Cookbook](feature_quickstart_cookbook.md)
- [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md)
- [Release-Facing Examples](../release_facing_examples.md)
