# Segment/Polygon Any-Hit Rows

## Purpose

`segment_polygon_anyhit_rows` emits one `(segment_id, polygon_id)` row per true
segment/polygon hit.

Use it when you want explicit join rows and plan to aggregate or analyze them
outside RTDL.

## Docs

- canonical example:
  - [rtdl_segment_polygon_anyhit_rows.py](../../../examples/rtdl_segment_polygon_anyhit_rows.py)
- shared reference kernel:
  - [rtdl_workload_reference.py](../../../examples/reference/rtdl_workload_reference.py)
- PostGIS SQL comparison:
  - [v0_2_segment_polygon_postgis_workloads.sql](../../sql/v0_2_segment_polygon_postgis_workloads.sql)

Kernel shape:

```python
segments = rt.input("segments", rt.Segments, role="probe")
polygons = rt.input("polygons", rt.Polygons, role="build")
candidates = rt.traverse(segments, polygons, accel="bvh")
hits = rt.refine(candidates, predicate=rt.segment_polygon_anyhit_rows(exact=False))
return rt.emit(hits, fields=["segment_id", "polygon_id"])
```

## Code

- predicate:
  - `rt.segment_polygon_anyhit_rows(exact=False)`
- canonical reference kernel:
  - [segment_polygon_anyhit_rows_reference](../../../examples/reference/rtdl_workload_reference.py)

## Example

Run:

```bash
python examples/rtdl_segment_polygon_anyhit_rows.py --backend cpu_python_reference --copies 16
```

Use `python3` instead if that is what your shell exposes.

Compact app surface:

```bash
python examples/rtdl_segment_polygon_anyhit_rows.py --backend cpu_python_reference --output-mode segment_counts --copies 16
python examples/rtdl_segment_polygon_anyhit_rows.py --backend optix --output-mode segment_counts --optix-mode native --copies 16
```

Rows-mode boundary:

```bash
python examples/rtdl_segment_polygon_anyhit_rows.py --backend optix --output-mode rows --optix-mode native --copies 16
```

That command fails intentionally because native OptiX currently exists only for
the compact count/flag path through `segment_polygon_hitcount`; pair-row native output does not exist yet.

Claim-sensitive boundary:

```bash
python examples/rtdl_segment_polygon_anyhit_rows.py --backend optix --output-mode segment_counts --optix-mode native --require-rt-core
```

That command also fails intentionally today. The compact native mode is useful
for local evaluation, but it remains behind strict RTX validation and is not a
released NVIDIA RT-core claim.

## Best Practices

- use this when downstream code needs the exact polygon ids
- prefer it over `segment_polygon_hitcount` when you want custom grouping later
- when only counts or flags are needed, prefer `--output-mode segment_counts`
  or `segment_flags` so the app can reuse the compact hit-count primitive
- keep ids stable and sortable because row shape is the main value of this feature
- compare accepted larger rows against PostGIS on Linux when the goal is correctness evidence

## Try

- join-style auditing
- touched-polygon id extraction
- custom downstream aggregation

## Try Not

- using it when only per-segment counts are needed
- expecting overlay fragments or overlap area
- treating it as generic segment/polygon geometry output

## Limitations

- row materialization can be heavier than aggregated counting if you only need counts
- current geometry path is float-based
- OptiX native mode does not support pair-row output today; it only exists for
  compact flag/count paths
- released OptiX RT-core claims are still blocked; `--require-rt-core` rejects
  this workload today
- strongest evidence remains on the accepted Linux/PostGIS validation surface
