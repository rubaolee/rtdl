# Tutorial: Segment And Polygon Workloads

This tutorial covers the stable released workload families in `v0.2.0`.

Use it when you want to learn RTDL through real public workloads rather than
through the small hello-world or sorting demos.

## What You Will Learn

- the difference between count-style and row-style outputs
- how RTDL models segment/polygon interaction workloads
- how the overlap and Jaccard line fits beside the segment/polygon line

## Start With These Two Examples

### Segment/Polygon Hit Count

Run:

```bash
PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 16
```

This workload emits one row per segment with:

- `segment_id`
- `hit_count`

Use it when you want:

- screening
- ranking
- compact summaries

### Segment/Polygon Any-Hit Rows

Run:

```bash
PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_anyhit_rows.py --backend cpu_python_reference --copies 16
```

This workload emits one row per true pair:

- `segment_id`
- `polygon_id`

Use it when you want:

- auditing
- join-style output
- custom aggregation in Python after RTDL finishes

## The Overlap And Jaccard Line

The released package also includes:

- [examples/rtdl_polygon_pair_overlap_area_rows.py](../../examples/rtdl_polygon_pair_overlap_area_rows.py)
- [examples/rtdl_polygon_set_jaccard.py](../../examples/rtdl_polygon_set_jaccard.py)

Run:

```bash
PYTHONPATH=src:. python3 examples/rtdl_polygon_pair_overlap_area_rows.py
PYTHONPATH=src:. python3 examples/rtdl_polygon_set_jaccard.py
```

These are narrower than the segment/polygon families. In particular, the
Jaccard line is packaged under a bounded pathology-style overlap contract rather
than as a generic polygon-similarity engine.

## Which One To Learn First

Recommended order:

1. `segment_polygon_hitcount`
2. `segment_polygon_anyhit_rows`
3. `polygon_pair_overlap_area_rows`
4. `polygon_set_jaccard`

That order moves from the easiest output shape to the more specialized overlap
and similarity line.

## Next Pages

For example commands:

- [Release-Facing Examples](../release_facing_examples.md)

For exact workload contracts:

- [Feature Homes](../features/README.md)

For the active preview line:

- [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md)
