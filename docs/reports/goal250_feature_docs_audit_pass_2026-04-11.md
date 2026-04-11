# Goal 250 Report: Feature Docs Audit Pass

Date: 2026-04-11
Status: implemented

## Summary

Goal 250 expands the system audit into the feature-reference layer.

The main issues found were consistent rather than isolated:

- two feature pages still led with unexplained acronyms (`LSI`, `PIP`)
- several feature pages still used the older `cd rtdl` plus `python3` command
  style instead of the released repo-root command style
- several referenced example scripts still failed from a fresh repo-root run
  because they did not bootstrap `src/` onto `sys.path`

## What Changed

Updated feature docs:

- `docs/features/lsi/README.md`
- `docs/features/pip/README.md`
- `docs/features/point_nearest_segment/README.md`
- `docs/features/polygon_pair_overlap_area_rows/README.md`
- `docs/features/polygon_set_jaccard/README.md`
- `docs/features/ray_tri_hitcount/README.md`
- `docs/features/segment_polygon_anyhit_rows/README.md`
- `docs/features/segment_polygon_hitcount/README.md`
- reviewed as already acceptable in this pass:
  - `docs/features/fixed_radius_neighbors/README.md`
  - `docs/features/knn_rows/README.md`
  - `docs/features/overlay/README.md`

Updated example entrypoints:

- `examples/rtdl_polygon_pair_overlap_area_rows.py`
- `examples/rtdl_polygon_set_jaccard.py`
- `examples/reference/rtdl_ray_tri_hitcount.py`
- `examples/reference/rtdl_language_reference.py`
- `examples/reference/rtdl_workload_reference.py`

## Verification

Feature-doc commands validated successfully from the repository root:

- `python3 examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 2`
- `python3 examples/rtdl_segment_polygon_anyhit_rows.py --backend cpu_python_reference --copies 2`
- `python3 examples/rtdl_polygon_pair_overlap_area_rows.py`
- `python3 examples/rtdl_polygon_set_jaccard.py`
- `python3 examples/reference/rtdl_ray_tri_hitcount.py`
- `python3 examples/reference/rtdl_language_reference.py`
- `python3 examples/reference/rtdl_workload_reference.py`

## Outcome

This pass makes the feature-reference layer more consistent with the released
front-door documentation:

- acronym-heavy titles are clearer on first read
- command style is more consistent with the rest of the released docs
- the feature pages no longer point users at example commands that fail in a
  fresh checkout
