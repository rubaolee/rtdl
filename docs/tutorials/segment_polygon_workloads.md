# Tutorial: Segment And Polygon Workloads

This tutorial covers the current v2.0-facing segment and polygon workload
families.

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
PYTHONPATH=src:. python examples/rtdl_segment_polygon_anyhit_rows.py --backend optix --output-mode rows --optix-mode native --copies 4 --output-capacity 1000000
```

Important boundary:

- these commands are useful for local compatibility and future promotion work
- they are compatibility/native-mode examples, not broad NVIDIA RT-core
  speedup claims
- road-hazard has a bounded claim-review path with
  `--output-mode summary --optix-mode native --require-rt-core`; that path is
  limited to prepared compact summary traversal, not full GIS/routing or
  default-app speedup
- segment/polygon hit-count has a bounded prepared compact-summary claim path,
  not a broad default-app claim
- `segment_polygon_anyhit_rows --output-mode rows --optix-mode native` uses the
  bounded native pair-row emitter. The v2.0 path also documents streaming
  witness-column output for larger summaries. Public wording must still stay
  limited to the reviewed output capacity; unbounded row-volume speedup remains
  outside the claim.

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
PYTHONPATH=src:. python examples/rtdl_polygon_pair_overlap_area_rows.py --backend optix --output-mode summary
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_polygon_pair_overlap_area_rows.py
python examples\rtdl_polygon_pair_overlap_area_rows.py --backend embree
```

Embree/OptiX modes are native-assisted: the backend performs LSI/PIP candidate
discovery and current compact summary paths use backend-neutral exact
grid-cell area summary plumbing.

The OptiX path is bounded to RT-assisted candidate discovery plus documented
exact continuation. It is not a monolithic GPU polygon-area kernel or whole-app
polygon speedup claim. For claim-sensitive runs:

```bash
PYTHONPATH=src:. python examples/rtdl_polygon_pair_overlap_area_rows.py --backend optix --require-rt-core
```

The segment/polygon road-screening and direct segment/polygon lines have
bounded claim-review paths, but the release boundary remains narrow: prepared
compact road-hazard summary, prepared compact hit-count summary, streaming
witness columns, and prepared bounded pair-row traversal only. Default app
behavior, full GIS/routing, broad segment/polygon acceleration, and unbounded
row-volume speedup remain outside the claim.

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
PYTHONPATH=src:. python examples/rtdl_polygon_set_jaccard.py --backend optix
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_polygon_set_jaccard.py
python examples\rtdl_polygon_set_jaccard.py --backend embree
```

This workload is packaged under a bounded pathology-style overlap contract. It
is not framed as a generic polygon-similarity engine for every use case. Its
Embree/OptiX modes are native-assisted: the backend performs candidate
discovery and current compact summary paths use native bounded collection plus
backend-neutral set-area summary plumbing before computing the Jaccard ratio.

The OptiX path is correctness-ready at chunk `1024`, but no positive public
Jaccard speedup wording is authorized because current evidence still has OptiX
slower than Embree. This is not a monolithic GPU Jaccard or whole-app speedup
claim. For claim-sensitive runs:

```bash
PYTHONPATH=src:. python examples/rtdl_polygon_set_jaccard.py --backend optix --require-rt-core
```

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
