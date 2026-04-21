# Goal691: OptiX App Action Implementation

Date: 2026-04-21

Inputs:

- Goal689 OptiX app performance review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal689_optix_app_performance_review_2026-04-21.md`
- Goal690 Gemini consensus/action plan:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal690_gemini_optix_consensus_action_plan_2026-04-21.md`

## Goal

Start executing the Codex/Gemini OptiX performance plan without letting
parallel AI work create inconsistent implementations.

This goal makes the first concrete code changes in the highest-priority app
area:

- robot collision / visibility / ray-triangle any-hit;
- native/prepared scalar output path;
- phase profiling foundation;
- scoped external review requests for DB/segment-polygon and CUDA-through-OptiX
  app groups.

## Implementation

### Robot Collision Prepared Count Mode

Updated:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_robot_collision_screening_app.py`

New CLI option:

```bash
PYTHONPATH=src:. python examples/rtdl_robot_collision_screening_app.py \
  --backend optix \
  --optix-summary-mode prepared_count
```

The default remains unchanged:

```bash
PYTHONPATH=src:. python examples/rtdl_robot_collision_screening_app.py \
  --backend cpu_python_reference
```

Behavior:

- `--optix-summary-mode rows` preserves the existing row-emitting behavior.
- `--optix-summary-mode prepared_count` requires `--backend optix`.
- The prepared-count path uses:
  - `rt.prepare_optix_ray_triangle_any_hit_2d(obstacle_triangles)`
  - `rt.prepare_optix_rays_2d(edge_rays)`
  - `prepared_scene.count(prepared_rays)`
- It returns a native scalar hit-edge count instead of materializing per-ray
  Python dict rows.

Boundary:

- This is not yet pose-level native output.
- It is a scalar hit-edge summary path.
- Use row mode when users need per-edge witness rows, pose summaries, or
  debugging details.

This is still the correct first optimization slice: it proves the app can use
the prepared OptiX any-hit count surface directly and avoids the worst
`tuple[dict, ...]` row-materialization overhead for count-only app summaries.

### Phase Profiler

Added:

- `/Users/rl2025/rtdl_python_only/scripts/goal691_optix_app_phase_profiler.py`

Supported detailed app today:

- `robot_collision_screening`

Useful commands:

```bash
PYTHONPATH=src:. python scripts/goal691_optix_app_phase_profiler.py --list-apps
```

```bash
PYTHONPATH=src:. python scripts/goal691_optix_app_phase_profiler.py \
  --app robot_collision_screening \
  --backend cpu_python_reference \
  --iterations 3
```

```bash
PYTHONPATH=src:. python scripts/goal691_optix_app_phase_profiler.py \
  --app robot_collision_screening \
  --backend optix \
  --summary-mode prepared_count \
  --iterations 3
```

The profiler emits:

- `python_input_construction`
- `native_prepare_scene`
- `native_prepare_rays`
- `native_execute`
- `copy_back_and_scalar_materialize`
- `total`

On non-OptiX or row mode, some phases are necessarily coarse. The point of
this first profiler is to establish a common output shape and make the
prepared OptiX count path measurable.

### External AI Work Split

Added handoff request files:

- `/Users/rl2025/rtdl_python_only/docs/handoff/GOAL691_CLAUDE_DB_SEGPOLY_OPTIX_ACTION_REQUEST_2026-04-21.md`
- `/Users/rl2025/rtdl_python_only/docs/handoff/GOAL691_GEMINI_CUDA_THROUGH_OPTIX_ACTION_REQUEST_2026-04-21.md`

Requested split:

- Claude: DB analytics and segment/polygon OptiX action plan.
- Gemini Flash: Hausdorff, ANN, outlier, DBSCAN, and Barnes-Hut
  CUDA-through-OptiX action plan.

Both requests require separating correctness support from RT-core performance
claims.

Claude completed the DB/segment-polygon review:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal691_claude_db_segpoly_optix_action_review_2026-04-21.md`
- Verdict: ACCEPT as action plan.
- Key next goals from Claude:
  - Goal692: DB/segment-polygon correctness gates, classification
    transparency, and segment/polygon output-volume remediation.
  - Goal693: DB phase-split profiler and DB prepared columnar dataset API.
  - Goal694: hardware-gated native OptiX segment/polygon trial or explicit
    reclassification decision plus RTX-class validation.

Gemini Flash was called for the CUDA-through-OptiX app group. At the time this
implementation report was written, that CLI process had not yet produced the
requested report file. The handoff request remains available for manual or
automatic retry.

## Verification

Focused local verification:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal691_optix_robot_summary_profiler_test \
  tests.goal690_optix_performance_classification_test \
  tests.goal513_public_example_smoke_test
```

Result:

- `10` tests OK.

Static checks:

```bash
python3 -m py_compile \
  examples/rtdl_robot_collision_screening_app.py \
  scripts/goal691_optix_app_phase_profiler.py \
  tests/goal691_optix_robot_summary_profiler_test.py
```

Result:

- OK.

```bash
git diff --check
```

Result:

- OK.

## Current Limitations

- The local Mac environment does not validate OptiX native execution.
- The prepared-count path still reports only total hit-edge count, not native
  pose-level flags.
- Full app-scale performance claims still require an RTX-class NVIDIA host.
- The profiler currently has detailed phases for robot collision only.

## Next Action

Implement native pose-level or grouped-summary output for robot collision, or
run the prepared-count path on the Linux OptiX host and compare:

- row mode vs prepared-count mode;
- cold vs warm;
- prepared vs unprepared;
- OptiX vs Embree;
- RTX-class hardware if available.

For DB and other app groups, wait for Claude/Gemini review outputs if
available, then integrate their action plans into the same tested classification
and profiling framework.
