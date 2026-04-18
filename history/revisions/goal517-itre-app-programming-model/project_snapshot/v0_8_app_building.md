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
| Robot collision screening | robot link edge rays plus obstacle triangles | per-edge ray/triangle hit-count rows | colliding pose IDs and pose summaries |
| Barnes-Hut force approximation | bodies plus Python-built quadtree nodes | body-to-node candidate rows | accepted nodes, exact fallback bodies, approximate force vectors, and oracle error |

## Run The App Suite

All commands below use `cpu_python_reference` so they run on a fresh checkout
without requiring native backend libraries.

```bash
PYTHONPATH=src:. python examples/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_robot_collision_screening_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_barnes_hut_force_app.py --backend cpu_python_reference
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_hausdorff_distance_app.py --backend cpu_python_reference
python examples\rtdl_robot_collision_screening_app.py --backend cpu_python_reference
python examples\rtdl_barnes_hut_force_app.py --backend cpu_python_reference
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src;."
python examples/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
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

## App 2: Robot Collision Screening

Use when you have a small discrete pose batch and want to screen which poses
collide with obstacle geometry.

RTDL owns:

- ray/triangle hit-count rows for link edge rays

Python owns:

- pose batch construction
- link edge-ray generation
- pose/link metadata
- hit aggregation into collision flags

Boundary:

- this is bounded 2D discrete-pose screening
- this is not full robot kinematics
- this is not continuous swept-volume CCD
- this is not a full mesh collision engine

Linux performance evidence:

- [Goal509 Robot/Barnes-Hut Linux Performance Report](../reports/goal509_robot_barnes_linux_perf_report_2026-04-17.md)
- bounded readout: CPU, Embree, and OptiX match the CPU hit-count oracle for
  robot collision screening; Embree is the strongest measured backend on the
  Linux host; Vulkan is not exposed for this app because it fails per-edge
  hit-count parity

## App 3: Barnes-Hut Force Approximation

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
- `ray_triangle_hit_count` supports bounded collision-screening apps.
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
