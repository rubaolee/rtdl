# Segment/Polygon Hit Count

## Purpose

`segment_polygon_hitcount` counts how many polygons each segment hits.

Use it when you want a compact per-segment summary rather than one row per
segment/polygon pair.

## Docs

- canonical example:
  - [rtdl_segment_polygon_hitcount.py](/Users/rl2025/rtdl_python_only/examples/rtdl_segment_polygon_hitcount.py)
- app-style example:
  - [rtdl_road_hazard_screening.py](/Users/rl2025/rtdl_python_only/examples/rtdl_road_hazard_screening.py)
- PostGIS SQL comparison:
  - [v0_2_segment_polygon_postgis_workloads.sql](/Users/rl2025/rtdl_python_only/docs/sql/v0_2_segment_polygon_postgis_workloads.sql)

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
  - [segment_polygon_hitcount_reference](/Users/rl2025/rtdl_python_only/examples/rtdl_goal10_reference.py)

## Example

Run:

```bash
cd /Users/rl2025/rtdl_python_only
python3 examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 16
```

App-style run:

```bash
cd /Users/rl2025/rtdl_python_only
python3 examples/rtdl_road_hazard_screening.py --backend cpu_python_reference
```

## Best Practices

- use this when downstream code wants screening, ranking, or compact summaries
- use `--copies N` for deterministic larger examples
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
- large-row validation is strongest on Linux with PostGIS as the external checker
