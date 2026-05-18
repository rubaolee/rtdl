# Tutorial: Nearest-Neighbor Workloads

This tutorial covers the current v2.0-facing nearest-neighbor workload shapes:
fixed-radius rows, K-closest rows, and Python-level composition for
Hausdorff-style applications.

| Workload | Question it answers | Output shape |
| --- | --- | --- |
| `fixed_radius_neighbors` | Which search points are within radius `r` of each query? | One row per `(query, neighbor)` pair within the radius |
| `knn_rows` | What are the `k` nearest search points to each query? | Ranked nearest-neighbor rows per query |

These row kernels also support app-level composition. For example, the
paper-derived Hausdorff app runs `knn_rows(k=1)` in both directions and lets
Python reduce the emitted rows to directed and undirected Hausdorff scalars.

Command convention used below:

- use `python`
- if your shell only provides `python3`, substitute `python3`
- Windows PowerShell uses:
  - `$env:PYTHONPATH = "src;."`
  - then `python ...`

---

## `fixed_radius_neighbors`

### Run it

```bash
PYTHONPATH=src:. python examples/v2_0/features/neighbors/rtdl_fixed_radius_neighbors.py --backend cpu_python_reference
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_fixed_radius_neighbors.py --backend cpu_python_reference
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src;."
python examples/v2_0/features/neighbors/rtdl_fixed_radius_neighbors.py --backend cpu_python_reference
```

Expected output excerpt:

```json
{
  "app": "fixed_radius_neighbors",
  "radius": 0.5,
  "neighbors_by_query": {
    "100": [
      {"neighbor_id": 1, "distance": 0.0},
      {"neighbor_id": 2, "distance": 0.3}
    ]
  }
}
```

### The kernel

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_neighbors_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=0.5, k_max=3))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])
```

### Parameters

- `radius`: only neighbors with `distance <= radius` are emitted
- `k_max`: maximum neighbors to emit per query

### Use when

- you want all neighbors inside a service radius
- you need local-density row materialization
- you want a bounded neighborhood join with a distance filter

---

## `knn_rows`

### Run it

```bash
PYTHONPATH=src:. python examples/v2_0/features/neighbors/rtdl_knn_rows.py --backend cpu_python_reference
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_knn_rows.py --backend cpu_python_reference
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src;."
python examples/v2_0/features/neighbors/rtdl_knn_rows.py --backend cpu_python_reference
```

Expected output excerpt:

```json
{
  "app": "knn_rows",
  "k": 3,
  "neighbors_by_query": {
    "100": [
      {"neighbor_id": 1, "neighbor_rank": 1, "distance": 0.0},
      {"neighbor_id": 2, "neighbor_rank": 2, "distance": 0.3}
    ]
  }
}
```

### The kernel

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def knn_rows_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.knn_rows(k=3))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])
```

### Parameters

- `k`: number of nearest neighbors to return per query

### Use when

- you need the top `k` nearest neighbors per query
- you want explicit `neighbor_rank` in the output
- you are building graph-style candidate edges

---

## `fixed_radius_neighbors` vs `knn_rows`

| Question | Choose |
| --- | --- |
| "Which points are within 5 km?" | `fixed_radius_neighbors` |
| "What are the nearest 3 facilities?" | `knn_rows` |
| Need distance threshold as part of the contract | `fixed_radius_neighbors` |
| Need ranked nearest rows even when far away | `knn_rows` |

Important difference:

- `fixed_radius_neighbors` is distance-filtered
- `knn_rows` is top-`k` ranked output

---

## App Pattern: Hausdorff Distance

Hausdorff-style directed distance is a strong RTDL + Python app candidate. The
app shape is:

| Data | Becomes |
| --- | --- |
| point set `A`, point set `B` | nearest-neighbor rows for `A -> B` |
| point set `B`, point set `A` | nearest-neighbor rows for `B -> A` |
| both directed row sets | one undirected Hausdorff distance and witness IDs |

Run the bounded app:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
```

On Linux with built RTDL backend libraries, the same app can run through
Embree, OptiX, and Vulkan:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py --backend embree
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py --backend optix
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py --backend vulkan
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_hausdorff_distance_app.py --backend cpu_python_reference
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src;."
python examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
```

RTDL owns the nearest-neighbor row production. Python owns loading point sets,
running the two directed passes, reducing with `max(distance)`, and checking the
small-case brute-force oracle. This app does not claim the paper's full X-HD
performance optimizations such as grid-cell pruning or prepared point-set reuse.

Current performance wording must come from the v2.0 evidence packet, not from a
tutorial. The bounded readout is that RTDL can provide the RT-shaped candidate
or neighbor rows while Python or a partner framework owns the final app answer.

The current exact Hausdorff and ANN ranking paths are not broad NVIDIA RT-core
claims. Prepared decision modes can use bounded fixed-radius traversal; they do
not automatically authorize exact ranking, whole-app speedup, or arbitrary ANN
index claims. Claim-sensitive scripts using `--require-rt-core` keep that
boundary explicit.

---

## Backend progression

The public examples are easiest to learn on:

```bash
PYTHONPATH=src:. python examples/v2_0/features/neighbors/rtdl_fixed_radius_neighbors.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/v2_0/features/neighbors/rtdl_knn_rows.py --backend cpu_python_reference
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_fixed_radius_neighbors.py --backend cpu_python_reference
python examples\rtdl_knn_rows.py --backend cpu_python_reference
```

Then move to the native CPU and accelerated backends that your machine
supports:

```bash
PYTHONPATH=src:. python examples/v2_0/features/neighbors/rtdl_fixed_radius_neighbors.py --backend cpu
PYTHONPATH=src:. python examples/v2_0/features/neighbors/rtdl_knn_rows.py --backend cpu
PYTHONPATH=src:. python examples/v2_0/features/neighbors/rtdl_fixed_radius_neighbors.py --backend embree
PYTHONPATH=src:. python examples/v2_0/features/neighbors/rtdl_knn_rows.py --backend embree
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_fixed_radius_neighbors.py --backend cpu
python examples\rtdl_knn_rows.py --backend cpu
python examples\rtdl_fixed_radius_neighbors.py --backend embree
python examples\rtdl_knn_rows.py --backend embree
```

OptiX and Vulkan availability depends on the machine and local runtime setup.
Use the current feature docs and v2.0 release-candidate packet for the exact
platform story.

---

## Next

- [Feature Homes](../features/README.md)
- [Tutorial Index](README.md)
