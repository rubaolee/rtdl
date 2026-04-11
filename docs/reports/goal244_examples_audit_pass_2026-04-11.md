# Goal 244 Report: Examples Audit Pass

Date: 2026-04-11
Status: implemented

## Summary

This goal records the examples tier into the system audit database after the
front page, tutorials, and public docs tiers.

## Important Fix Made During The Pass

The pass surfaced a real user-facing inconsistency:

- `examples/rtdl_hello_world.py` and `examples/rtdl_hello_world_backends.py`
  previously imported `rtdsl` directly without the local checkout bootstrap
  used by other release-facing examples

That was repaired before recording the pass, so the examples tier is now
audited against the corrected `v0.4.0` state rather than against a known-bad
first-run script.

## Live Validation Used In This Pass

The pass is backed by direct example execution, including:

- `python3 examples/rtdl_hello_world.py`
- `python3 examples/rtdl_hello_world_backends.py --backend cpu_python_reference`
- `python3 examples/rtdl_fixed_radius_neighbors.py --backend cpu_python_reference`
- `python3 examples/rtdl_knn_rows.py --backend cpu_python_reference`
- `python3 examples/rtdl_service_coverage_gaps.py --backend cpu_python_reference --copies 2`
- `python3 examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 2`
- `python3 examples/visual_demo/rtdl_lit_ball_demo.py --backend cpu_python_reference --compare-backend none --width 32 --height 16 --triangles 64 --output build/rtdl_lit_ball_demo_audit.pgm`

## Outcome

After this pass, the audit database covers:

- front page
- tutorials
- public docs
- release-facing examples

That means the next major audit stage can move into the code-facing surface
instead of staying on user-entry layers.
