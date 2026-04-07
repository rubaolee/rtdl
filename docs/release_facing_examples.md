# Release-Facing Examples

This page is the canonical example index for the frozen RTDL v0.2 surface.

Use these first if you want the examples that best match the current accepted
live workload/package story.

## Core examples

### Segment/Polygon Hit Count

- code:
  - [rtdl_segment_polygon_hitcount.py](../examples/rtdl_segment_polygon_hitcount.py)
- run:

```bash
cd /path/to/rtdl_python_only
python3 examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 16
```

### Segment/Polygon Any-Hit Rows

- code:
  - [rtdl_segment_polygon_anyhit_rows.py](../examples/rtdl_segment_polygon_anyhit_rows.py)
- run:

```bash
cd /path/to/rtdl_python_only
python3 examples/rtdl_segment_polygon_anyhit_rows.py --backend cpu_python_reference --copies 16
```

### Polygon-Set Jaccard

- code:
  - [rtdl_polygon_set_jaccard.py](../examples/rtdl_polygon_set_jaccard.py)
- run:

```bash
cd /path/to/rtdl_python_only
PYTHONPATH=src:. python3 examples/rtdl_polygon_set_jaccard.py
```

### Polygon-Pair Overlap Area Rows

- code:
  - [rtdl_polygon_pair_overlap_area_rows.py](../examples/rtdl_polygon_pair_overlap_area_rows.py)
- run:

```bash
cd /path/to/rtdl_python_only
PYTHONPATH=src:. python3 examples/rtdl_polygon_pair_overlap_area_rows.py
```

## App-style example

- [rtdl_road_hazard_screening.py](../examples/rtdl_road_hazard_screening.py)

This is the best short example of how the segment/polygon line looks in a more
user-facing workflow.

## Generate-only entry point

- script:
  - [rtdl_generate_only.py](../scripts/rtdl_generate_only.py)

Current accepted narrow generate-only example:

```bash
cd /path/to/rtdl_python_only
python3 scripts/rtdl_generate_only.py --workload polygon_set_jaccard --dataset authored_polygon_set_jaccard_minimal --backend cpu_python_reference --output-mode rows --artifact-shape handoff_bundle --output build/generated_polygon_set_jaccard_bundle
```

## Notes

- these are the release-facing examples for the frozen v0.2 scope
- older demos and exploratory examples still exist in the repo, but they are
  not the primary release-facing entry points
