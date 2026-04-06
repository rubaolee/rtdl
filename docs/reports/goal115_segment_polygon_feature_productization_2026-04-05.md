# Goal 115 Segment-Polygon Feature Productization

Date: 2026-04-05
Author: Codex
Status: accepted

## Final conclusion

Goal 115 is finished.

Accepted claim:

- `segment_polygon_hitcount` is now easier to discover and run as a user-facing
  RTDL feature
- the main example now supports larger deterministic tiled datasets directly
- the docs now connect the feature to its current closure, performance, and
  PostGIS validation story

## What changed

### Example surface

Updated:

- `examples/rtdl_segment_polygon_hitcount.py`

What improved:

- `--dataset` now accepts generic representative dataset names instead of a
  hardcoded short list
- `--copies N` now provides a direct shortcut for:
  - `derived/br_county_subset_segment_polygon_tiled_xN`

That means a user can now run:

```bash
cd /Users/rl2025/rtdl_python_only
python3 examples/rtdl_segment_polygon_hitcount.py --backend cpu --copies 64
```

without first learning the internal derived dataset naming convention.

### Docs surface

Updated:

- `docs/rtdl_feature_guide.md`
- `docs/rtdl/workload_cookbook.md`
- `docs/rtdl/dsl_reference.md`

What improved:

- the feature guide now states the strengthened current position of
  `segment_polygon_hitcount`
- the cookbook now points users to the scalable deterministic example path
- the DSL reference now points users to the example and external validation
  story rather than leaving the workload as a bare syntax entry

## Validation

Local checks:

```bash
python3 -m py_compile examples/rtdl_segment_polygon_hitcount.py

cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 16
```

Observed high-level result:

- the example accepted `--copies 16`
- it resolved to:
  - `derived/br_county_subset_segment_polygon_tiled_x16`
- it returned deterministic `segment_id` / `hit_count` rows

## Honest boundary

Goal 115 does not add a new correctness or performance claim.

It improves:

- discoverability
- example usability
- doc alignment

The family’s current architectural honesty boundary remains unchanged.
