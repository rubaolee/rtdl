# Goal3755 Robot Collision HIPRT Route Readiness

Date: 2026-06-07

## Purpose

Goal3753 identified robot collision as the first v2.10 AMD/HIPRT benchmark app
that can reach a functional pod before deeper generic HIPRT extensions are
added. This goal closes the app-surface gap: the robot collision screening app
now exposes the existing generic HIPRT `ray_triangle_any_hit` row path through
its public backend selector.

## Change

- Added `--backend hiprt` to
  `examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py`.
- Routed the app's row mode through `rt.run_hiprt(robot_edge_any_hit_kernel, ...)`.
- Updated `rtdsl.app_engine_support_matrix()` and
  `docs/app_engine_support_matrix.md` so robot collision HIPRT is visible as
  `direct_cli_native`.
- Added `tests.goal3755_robot_collision_hiprt_route_readiness_test`.

## Boundary

This goal does not provide AMD performance evidence. The current A5000 pod is
NVIDIA hardware, and the current pod probe found no HIPRT SDK/runtime install.
So the evidence here is source, CLI, matrix, and import/validation readiness
only. The next AMD pod should run the same app command:

```bash
PYTHONPATH=src:. python examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py --backend hiprt --output-mode pose_flags
```

Prepared OptiX summary modes remain OptiX-only. HIPRT currently exposes the
row-producing any-hit path for this app, not the OptiX prepared pose-flag
summary path.

## Acceptance

- `--backend hiprt` is a real app CLI choice.
- The backend dispatch calls `rt.run_hiprt` exactly once for this app route.
- The app-support matrix documents robot collision HIPRT as exposed while
  explicitly stating it is ready for AMD functional validation, not AMD
  performance evidence.
- Static and source-tree tests pass locally and on the current pod.

## Validation

Local Windows:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3755_robot_collision_hiprt_route_readiness_test tests.goal3753_amd_hiprt_benchmark_parity_plan_test
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal503_robot_collision_screening_app_test tests.goal3755_robot_collision_hiprt_route_readiness_test
py -3 -m py_compile examples\v2_0\apps\robotics\rtdl_robot_collision_screening_app.py src\rtdsl\app_support_matrix.py tests\goal3755_robot_collision_hiprt_route_readiness_test.py
```

Current A5000 pod:

```bash
cd /root/rtdl_goal3737_clean
source /root/rtdl_numba_venv/bin/activate
export PYTHONPATH=src:.
timeout 120 python -m unittest tests.goal3755_robot_collision_hiprt_route_readiness_test tests.goal3753_amd_hiprt_benchmark_parity_plan_test
timeout 60 python -m py_compile examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py src/rtdsl/app_support_matrix.py tests/goal3755_robot_collision_hiprt_route_readiness_test.py
```

All listed focused checks passed. The pod run is still not HIPRT runtime
evidence because the pod is NVIDIA hardware and does not have the HIPRT
SDK/runtime installed.
