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
| `bfs` | frontier vertices, visited set, graph CSR | newly discovered vertex rows |
| `triangle_count` | seed edges and graph CSR | unique triangle rows |

The public examples are bounded kernel steps. Python still owns whole-algorithm
orchestration such as multi-level BFS loops or full-graph accumulation, while
RTDL owns the candidate discovery/refinement step.

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

These native commands still reject `--require-rt-core` intentionally until the
combined Goal889/905 RTX cloud gate proves row-digest parity on real RTX
hardware. Visibility rows are the only graph sub-path that can use
`--require-rt-core` before that gate, and even then it is bounded to
line-of-sight filtering, not shortest path, graph databases, distributed graph
analytics, or whole-app graph-system speedup.

---

## Next

- [Release-Facing Examples](../release_facing_examples.md)
- [RTDL v0.6 Release Statement](../release_reports/v0_6/release_statement.md)
- [RTDL v0.6 Support Matrix](../release_reports/v0_6/support_matrix.md)
