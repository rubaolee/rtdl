# Goal 702: Robot Collision Profiler Compact Output Modes

Date: 2026-04-21

## Scope

This goal continues the OptiX app-performance cleanup after the cloud RTX VM attempts failed. It does not create RTX hardware evidence. It improves the local and future-cloud measurement surface for the robot collision app by making the existing compact output modes visible in the phase profiler.

## Change

Updated:

- `/Users/rl2025/rtdl_python_only/scripts/goal691_optix_app_phase_profiler.py`

Added:

- `/Users/rl2025/rtdl_python_only/tests/goal702_robot_collision_profiler_output_modes_test.py`

The profiler now accepts:

```bash
PYTHONPATH=src:. python3 scripts/goal691_optix_app_phase_profiler.py \
  --backend cpu_python_reference \
  --iterations 1 \
  --output-mode pose_flags
```

and:

```bash
PYTHONPATH=src:. python3 scripts/goal691_optix_app_phase_profiler.py \
  --backend cpu_python_reference \
  --iterations 1 \
  --output-mode hit_count
```

The profiler output records `output_mode` and a compact `last_output` shape:

- `full`: `row_count`, `colliding_pose_count`, `matches_oracle`
- `pose_flags`: `pose_flag_count`, `colliding_pose_count`, `matches_oracle`
- `hit_count`: `hit_edge_count`, `matches_oracle`
- `prepared_count`: always reports native OptiX scalar `hit_count`
- `prepared_pose_flags`: reports native OptiX pose-level collision flags

## Correctness Boundary

Compact row-mode output still executes the row path internally. It reduces app JSON/Python output burden, but it is not a native OptiX prepared-summary ABI.

Post-Goal753 update: the native OptiX summary paths are now
`--summary-mode prepared_count`, which returns only a scalar hit-edge count,
and `--summary-mode prepared_pose_flags`, which returns pose-level collision
flags. Neither emits edge-level witness rows.

## Verification

Focused test command:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal702_robot_collision_profiler_output_modes_test \
  tests.goal701_robot_collision_compact_output_test \
  tests.goal691_optix_robot_summary_profiler_test
```

Result:

```text
Ran 11 tests in 0.864s
OK
```

Manual profiler checks:

- `full` mode matched oracle and reported `row_count: 16`, `colliding_pose_count: 2`
- `pose_flags` mode matched oracle and reported `pose_flag_count: 4`, `colliding_pose_count: 2`
- `hit_count` mode matched oracle and reported `hit_edge_count: 7`

## Release Claim Status

No release speedup claim is added by this goal.

This goal only improves measurement readiness and app-output transparency so a future RTX-class run can distinguish:

- full emitted-row overhead
- compact app-output overhead
- native scalar prepared-count overhead
- native prepared pose-flag overhead
