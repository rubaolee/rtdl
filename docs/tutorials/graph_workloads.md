# Tutorial: Graph Workloads

RTDL `v0.6.1` adds the first released RT graph workload family:

- `bfs`
- `triangle_count`

These graph programs follow the same RTDL shape as the earlier workload lines:

- host Python owns the surrounding program
- RTDL kernels own the bounded RT search step
- backend choice changes execution, not the public kernel contract

## What Data Becomes What Data

| Workload | Input data | Output data |
| --- | --- | --- |
| `bfs` | frontier vertices, visited set, graph CSR | newly discovered vertex rows, or compact native C++ discovery summaries |
| `triangle_count` | seed edges and graph CSR | unique triangle rows, or compact native C++ triangle summaries |

The public examples are bounded kernel steps. Python still owns whole-algorithm
orchestration such as multi-level BFS loops or full-graph accumulation, while
RTDL owns the candidate discovery/refinement step. In `--output-mode summary`,
the emitted BFS and triangle rows are reduced by RTDL's native C++ oracle
continuation instead of Python set/loop summary code.

Command convention used below:

- use `python`
- if your shell only provides `python3`, substitute `python3`
- Windows PowerShell uses:
  - `$env:PYTHONPATH = "src;."`
  - then `python ...`

---

## `bfs`

### Run it

```bash
PYTHONPATH=src:. python examples/rtdl_graph_bfs.py --backend cpu_python_reference
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_graph_bfs.py --backend cpu_python_reference
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src;."
python examples/rtdl_graph_bfs.py --backend cpu_python_reference
```

Expected output excerpt:

```json
{
  "app": "graph_bfs",
  "rows": [
    {"src_vertex": 0, "dst_vertex": 2, "level": 1},
    {"src_vertex": 1, "dst_vertex": 3, "level": 1}
  ]
}
```

### The kernel

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def bfs_expand_kernel():
    frontier = rt.input("frontier", rt.VertexFrontier, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    visited = rt.input("visited", rt.VertexSet, role="probe")
    candidates = rt.traverse(frontier, graph, accel="bvh", mode="graph_expand")
    fresh = rt.refine(candidates, predicate=rt.bfs_discover(visited=visited, dedupe=True))
    return rt.emit(fresh, fields=["src_vertex", "dst_vertex", "level"])
```

Important boundary:

- this public example runs one bounded BFS expansion step
- host-side multi-level BFS control still lives in Python
- `--output-mode summary` uses native C++ continuation for discovery counts,
  not a full native BFS engine

---

## `triangle_count`

### Run it

```bash
PYTHONPATH=src:. python examples/rtdl_graph_triangle_count.py --backend cpu_python_reference
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_graph_triangle_count.py --backend cpu_python_reference
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src;."
python examples/rtdl_graph_triangle_count.py --backend cpu_python_reference
```

Expected output excerpt:

```json
{
  "app": "graph_triangle_count",
  "rows": [
    {"u": 0, "v": 1, "w": 2}
  ]
}
```

### The kernel

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def triangle_probe_kernel():
    seeds = rt.input("seeds", rt.EdgeSet, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    candidates = rt.traverse(seeds, graph, accel="bvh", mode="graph_intersect")
    triangles = rt.refine(candidates, predicate=rt.triangle_match(order="id_ascending", unique=True))
    return rt.emit(triangles, fields=["u", "v", "w"])
```

Important boundary:

- this public example runs one bounded triangle probe step
- whole-graph accumulation still lives in Python or a larger host workflow
- `--output-mode summary` uses native C++ continuation for triangle/touched
  vertex counts, not a full native triangle-analytics engine

---

## Backend progression

Start with:

```bash
PYTHONPATH=src:. python examples/rtdl_graph_bfs.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_graph_triangle_count.py --backend cpu_python_reference
```

Then move to the native CPU path:

```bash
PYTHONPATH=src:. python examples/rtdl_graph_bfs.py --backend cpu
PYTHONPATH=src:. python examples/rtdl_graph_triangle_count.py --backend cpu
```

Then use your machine-specific accelerated backends:

```bash
PYTHONPATH=src:. python examples/rtdl_graph_bfs.py --backend embree
PYTHONPATH=src:. python examples/rtdl_graph_triangle_count.py --backend embree
```

On Linux hosts with the GPU/runtime stack enabled:

```bash
make build-optix
make build-vulkan

PYTHONPATH=src:. python examples/rtdl_graph_bfs.py --backend optix
PYTHONPATH=src:. python examples/rtdl_graph_bfs.py --backend vulkan
PYTHONPATH=src:. python examples/rtdl_graph_triangle_count.py --backend optix
PYTHONPATH=src:. python examples/rtdl_graph_triangle_count.py --backend vulkan
```

OptiX graph commands are compatibility paths by default, not NVIDIA RT-core
claims. The default graph OptiX mode remains a host-indexed CSR fallback so
existing users get the conservative correctness path. An explicit native
graph-ray mode now exists for BFS and triangle-count candidate generation:

```bash
PYTHONPATH=src:. python examples/rtdl_graph_bfs.py --backend optix --optix-graph-mode native
PYTHONPATH=src:. python examples/rtdl_graph_triangle_count.py --backend optix --optix-graph-mode native
```

After the Goal929/Goal930/Goal969 review chain, the unified graph app is ready
for RTX claim review only under a bounded scope: visibility-edge filtering plus
native graph-ray candidate generation. The component BFS and triangle-count
example scripts still reject `--require-rt-core` intentionally; use the unified
app for claim-sensitive graph runs:

```bash
PYTHONPATH=src:. python examples/rtdl_graph_analytics_app.py --backend optix --scenario visibility_edges --require-rt-core
```

The claim remains bounded to graph-edge visibility and candidate generation,
plus native C++ summary continuation where `--output-mode summary` is selected;
it is not a shortest-path, graph database, distributed graph analytics, or
whole-app graph-system speedup claim.

---

## Next

- [Release-Facing Examples](../release_facing_examples.md)
- [RTDL v0.6 Release Statement](../release_reports/v0_6/release_statement.md)
- [RTDL v0.6 Support Matrix](../release_reports/v0_6/support_matrix.md)
