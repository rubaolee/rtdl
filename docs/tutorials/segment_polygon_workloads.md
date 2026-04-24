# Tutorial: Segment And Polygon Workloads

This tutorial covers the stable released `v0.2.0` workload families.

These are the best place to learn RTDL through real public workloads instead of
through the tiny hello-world or sorting demos.

Command convention used below:

- use `python`
- if your shell only provides `python3`, substitute `python3`
- Windows PowerShell uses:
  - `$env:PYTHONPATH = "src;."`
  - then `python ...`

---

## Two output styles

RTDL workloads usually emit one of two shapes:

| Style | Example | What you get |
| --- | --- | --- |
| count per probe | `segment_polygon_hitcount` | one row per segment with `segment_id`, `hit_count` |
| row per true pair | `segment_polygon_anyhit_rows` | one row per `(segment, polygon)` true-hit pair |

Count-style output is compact. Row-style output gives you the detailed pairs
for downstream aggregation in Python.

---

## `segment_polygon_hitcount`

Question:

- how many polygons does each segment intersect?

Run:

```bash
PYTHONPATH=src:. python examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 4
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 4
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src;."
python examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 4
```

Expected output excerpt:

```json
{
  "row_count": 40,
  "rows": [
    {"segment_id": 1, "hit_count": 2},
    {"segment_id": 2, "hit_count": 1}
  ]
}
```

Kernel shape:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def segment_polygon_hitcount_kernel():
    segments = rt.input("segments", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    polygons = rt.input("polygons", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(segments, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_polygon_hitcount(exact=False))
    return rt.emit(hits, fields=["segment_id", "hit_count"])
```

Use when:

- you want compact screening or ranking
- you need per-segment summaries

---

## `segment_polygon_anyhit_rows`

Question:

- which `(segment, polygon)` pairs actually intersect?

Run:

```bash
PYTHONPATH=src:. python examples/rtdl_segment_polygon_anyhit_rows.py --backend cpu_python_reference --copies 4
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_segment_polygon_anyhit_rows.py --backend cpu_python_reference --copies 4
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src;."
python examples/rtdl_segment_polygon_anyhit_rows.py --backend cpu_python_reference --copies 4
```

Expected output excerpt:

```json
{
  "rows": [
    {"segment_id": 1, "polygon_id": 3},
    {"segment_id": 1, "polygon_id": 7}
  ]
}
```

Kernel shape:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def segment_polygon_anyhit_rows_kernel():
    segments = rt.input("segments", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    polygons = rt.input("polygons", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(segments, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_polygon_anyhit_rows(exact=False))
    return rt.emit(hits, fields=["segment_id", "polygon_id"])
```

Use when:

- you need the actual pair table
- you want to group or aggregate in Python afterward
- auditing matters more than compactness

---

## `hitcount` vs `anyhit_rows`

| Need | Choose |
| --- | --- |
| one summary row per segment | `segment_polygon_hitcount` |
| every true pair as rows | `segment_polygon_anyhit_rows` |
| compact output | `segment_polygon_hitcount` |
| join-style downstream processing | `segment_polygon_anyhit_rows` |

---

## OptiX mode boundary

The segment/polygon family exposes OptiX for compatibility work, but the public
surface is still split into three distinct states:

| OptiX request | What it means today |
| --- | --- |
| `--optix-mode auto` | preserve the current app default |
| `--optix-mode host_indexed` | force the released host-indexed fallback path |
| `--optix-mode native` | request the experimental native custom-AABB path |

Examples:

```bash
PYTHONPATH=src:. python examples/rtdl_segment_polygon_hitcount.py --backend optix --optix-mode host_indexed --copies 4
PYTHONPATH=src:. python examples/rtdl_segment_polygon_hitcount.py --backend optix --optix-mode native --copies 4
PYTHONPATH=src:. python examples/rtdl_segment_polygon_anyhit_rows.py --backend optix --output-mode segment_counts --optix-mode native --copies 4
```

Important boundary:

- these commands are useful for local compatibility and future promotion work
- they are **not** released NVIDIA RT-core claims
- the segment/polygon app family also rejects
`--require-rt-core` today
- `segment_polygon_anyhit_rows --output-mode rows --optix-mode native` also
  fails intentionally because pair-row native output does not exist yet

---

## The overlap and Jaccard line

The released package also includes two narrower polygon-overlap workloads:

### `polygon_pair_overlap_area_rows`

Question:

- for each overlapping polygon pair, what is the overlap area?

Run:

```bash
PYTHONPATH=src:. python examples/rtdl_polygon_pair_overlap_area_rows.py
PYTHONPATH=src:. python examples/rtdl_polygon_pair_overlap_area_rows.py --backend embree
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_polygon_pair_overlap_area_rows.py
python examples\rtdl_polygon_pair_overlap_area_rows.py --backend embree
```

The Embree mode is native-assisted: Embree performs polygon overlay/candidate
discovery and the app keeps exact grid-cell overlap-area refinement in
CPU/Python.

This app has no OptiX/NVIDIA RT-core surface today. For claim-sensitive scripts,
`--require-rt-core` fails intentionally instead of treating the Embree
native-assisted path as a GPU RT-core result.

The segment/polygon road-screening and direct segment/polygon apps also reject
`--require-rt-core` today, including their current OptiX native-mode
experiments. Those commands remain useful for compatibility work, but they are
not released NVIDIA RT-core claims until strict RTX validation passes.

Kernel shape:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def polygon_pair_overlap_area_rows_kernel():
    left_polygons = rt.input("left_polygons", rt.Polygons, layout=rt.Polygon2DLayout, role="probe")
    right_polygons = rt.input("right_polygons", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(left_polygons, right_polygons, accel="bvh")
    overlaps = rt.refine(candidates, predicate=rt.polygon_pair_overlap_area_rows())
    return rt.emit(overlaps, fields=["left_polygon_id", "right_polygon_id", "overlap_area"])
```

### `polygon_set_jaccard`

Question:

- what is the Jaccard similarity between two polygon sets?

Run:

```bash
PYTHONPATH=src:. python examples/rtdl_polygon_set_jaccard.py
PYTHONPATH=src:. python examples/rtdl_polygon_set_jaccard.py --backend embree
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_polygon_set_jaccard.py
python examples\rtdl_polygon_set_jaccard.py --backend embree
```

This workload is packaged under a bounded pathology-style overlap contract. It
is not framed as a generic polygon-similarity engine for every use case. Its
Embree mode is native-assisted: Embree performs candidate discovery and
CPU/Python computes exact set-area/Jaccard refinement.

This app has no OptiX/NVIDIA RT-core surface today. For claim-sensitive scripts,
`--require-rt-core` fails intentionally instead of treating the Embree
native-assisted path as a GPU RT-core result.

---

## Recommended learning order

1. `segment_polygon_hitcount`
2. `segment_polygon_anyhit_rows`
3. `polygon_pair_overlap_area_rows`
4. `polygon_set_jaccard`

That order moves from the simplest count-style output to the more specialized
overlap and similarity line.

---

## Next

- [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md)
- [Release-Facing Examples](../release_facing_examples.md)
