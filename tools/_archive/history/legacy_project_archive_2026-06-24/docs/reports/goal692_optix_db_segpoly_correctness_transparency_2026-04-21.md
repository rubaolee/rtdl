# Goal692: OptiX DB/Segment-Polygon Correctness And Transparency

Date: 2026-04-21

Inputs:

- Goal691 Claude DB/segment-polygon action review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal691_claude_db_segpoly_optix_action_review_2026-04-21.md`

## Scope

This goal executes the first part of Claude's accepted action plan:

- DB-1: portable DB correctness gate for the public unified DB app shape.
- SP-1: portable segment/polygon correctness gate for app outputs.
- SP-2: visible OptiX performance classification in public app JSON outputs.
- SP-5 first slice: compact output modes for segment/polygon any-hit rows.

## Changes

Updated public app outputs:

- `examples/rtdl_database_analytics_app.py`
- `examples/rtdl_road_hazard_screening.py`
- `examples/rtdl_segment_polygon_hitcount.py`
- `examples/rtdl_segment_polygon_anyhit_rows.py`

Each now includes `optix_performance`, sourced from
`rtdsl.optix_app_performance_support(app)`.

The current classifications are intentionally conservative:

- `database_analytics`: `python_interface_dominated`
- `road_hazard_screening`: `host_indexed_fallback`
- `segment_polygon_hitcount`: `host_indexed_fallback`
- `segment_polygon_anyhit_rows`: `host_indexed_fallback`

Updated `examples/rtdl_segment_polygon_anyhit_rows.py` with:

```bash
--output-mode rows
--output-mode segment_flags
--output-mode segment_counts
```

The default remains `rows`. The summary modes avoid emitting full
segment/polygon pair rows when the app only needs per-segment flags or counts.

## Boundaries

- This goal does not make segment/polygon OptiX a native RT-core traversal
  path.
- This goal does not optimize DB native aggregation yet.
- This goal makes correctness support and performance classification visible
  to users before deeper optimization work.

## Verification

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal692_optix_app_correctness_transparency_test \
  tests.goal691_optix_robot_summary_profiler_test \
  tests.goal690_optix_performance_classification_test \
  tests.goal513_public_example_smoke_test \
  tests.goal686_app_catalog_cleanup_test
```

Additional checks:

```bash
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
python3 -m py_compile \
  examples/rtdl_database_analytics_app.py \
  examples/rtdl_road_hazard_screening.py \
  examples/rtdl_segment_polygon_hitcount.py \
  examples/rtdl_segment_polygon_anyhit_rows.py \
  tests/goal692_optix_app_correctness_transparency_test.py
git diff --check
```

## Next

The next coding goal should implement DB-2: phase-split profiling for
`database_analytics`, including Python input construction, packing/native
prepare, native execute, copy-back, row materialization, and Python
post-processing.

## External Review

Claude finish review:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal692_claude_finish_review_2026-04-21.md`
- Verdict: ACCEPT.

Claude verified that the four app classifications are conservative and
accurate, that compact segment/polygon any-hit summary modes suppress full row
payloads when requested, and that no OptiX RT-core acceleration claim is
introduced or implied.
