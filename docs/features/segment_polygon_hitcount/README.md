# Segment/Polygon Hit Count

## Purpose

`segment_polygon_hitcount` counts how many polygons each segment hits.

Use it when you want a compact per-segment summary rather than one row per
segment/polygon pair.

## Docs

- canonical example:
  - [rtdl_segment_polygon_hitcount.py](../../../examples/rtdl_segment_polygon_hitcount.py)
- app-style example:
  - [rtdl_road_hazard_screening.py](../../../examples/rtdl_road_hazard_screening.py)
- PostGIS SQL comparison:
  - [v0_2_segment_polygon_postgis_workloads.sql](../../sql/v0_2_segment_polygon_postgis_workloads.sql)

Kernel shape:

```python
segments = rt.input("segments", rt.Segments, role="probe")
polygons = rt.input("polygons", rt.Polygons, role="build")
candidates = rt.traverse(segments, polygons, accel="bvh")
hits = rt.refine(candidates, predicate=rt.segment_polygon_hitcount(exact=False))
return rt.emit(hits, fields=["segment_id", "hit_count"])
```

## Code

- predicate:
  - `rt.segment_polygon_hitcount(exact=False)`
- canonical reference kernel:
  - [segment_polygon_hitcount_reference](../../../examples/reference/rtdl_workload_reference.py)

## Example

Run:

```bash
python examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 16
```

Use `python3` instead if that is what your shell exposes.

OptiX compatibility surface:

```bash
python examples/rtdl_segment_polygon_hitcount.py --backend optix --optix-mode host_indexed --copies 16
python examples/rtdl_segment_polygon_hitcount.py --backend optix --optix-mode native --copies 16
```

Claim-sensitive boundary:

```bash
python examples/rtdl_segment_polygon_hitcount.py --backend optix --optix-mode native --require-rt-core
```

That command currently fails intentionally. The native OptiX path is a public
experimental surface, but it is still behind strict RTX validation and is not a
released NVIDIA RT-core claim.

App-style run:

```bash
python examples/rtdl_road_hazard_screening.py --backend cpu_python_reference
```

## Best Practices

- use this when downstream code wants screening, ranking, or compact summaries
- use `--copies N` for deterministic larger examples
- if you explore OptiX locally, record `--optix-mode` explicitly so later
  reviews can distinguish host-indexed fallback from the experimental native
  path
- compare accepted larger rows against PostGIS on Linux
- remember that the current speed win comes from candidate reduction, not a broad RT-core maturity claim

## Try

- road hazard screening
- parcel contact counts per road segment
- compact ranking pipelines where only counts matter

## Try Not

- expecting polygon ids in the emitted rows
- using it when downstream code needs custom aggregation over exact hit pairs
- describing it as full overlay or full intersection geometry

## Limitations

- current semantics are hit-count semantics, not row materialization
- current geometry path is float-based
- released OptiX RT-core claims are still blocked; `--require-rt-core` rejects
  this workload today even if `--optix-mode native` is selected
- large-row validation is strongest on Linux with PostGIS as the external checker
