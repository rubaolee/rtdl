# Goal3756 Robot Collision AMD Parity Contract Correction

Date: 2026-06-07

## Purpose

Goal3755 exposed `--backend hiprt` for the robot collision screening app. That
route uses the existing generic HIPRT Ray2D/Triangle2D any-hit row path.
Goal3756 corrects the v2.10 AMD/HIPRT parity ledger so the first AMD robot
collision target names that exact contract.

## Correction

The robot collision parity row now requires:

- `ray_triangle_any_hit_2d`
- `visibility_rows`

It no longer names `ray_triangle_any_hit_3d` for this app, because the public
robot collision screening fixture is a 2D edge-ray versus 2D obstacle-triangle
route. It also no longer describes the first AMD target as a prepared summary
route. The prepared pose-flag summary is still an OptiX-only contract until
HIPRT has a generic prepared ray-buffer and group-index path.

## Boundary

This is a planning/source correction and provides no AMD performance evidence.
The first AMD pod run should validate the row route:

```bash
PYTHONPATH=src:. python examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py --backend hiprt --output-mode pose_flags
```

The target is HIPRT functional parity for the app's row-backed collision flags,
not the prepared OptiX pose-flag summary.

## Acceptance

- The v2.10 parity ledger names `ray_triangle_any_hit_2d` for robot collision.
- The app support matrix exposes HIPRT for robot collision.
- Prepared OptiX summary modes remain OptiX-only and fail closed for HIPRT.
- Claim boundaries remain false: no release, AMD performance, broad RT-core,
  whole-app, or paper-reproduction claim is authorized.

## Validation

Local Windows:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3756_robot_collision_amd_parity_contract_correction_test tests.goal3755_robot_collision_hiprt_route_readiness_test tests.goal3753_amd_hiprt_benchmark_parity_plan_test
py -3 -m py_compile src\rtdsl\v2_10_amd_hiprt_benchmark_parity.py tests\goal3756_robot_collision_amd_parity_contract_correction_test.py
```

Current A5000 pod:

```bash
cd /root/rtdl_goal3737_clean
source /root/rtdl_numba_venv/bin/activate
export PYTHONPATH=src:.
timeout 120 python -m unittest tests.goal3756_robot_collision_amd_parity_contract_correction_test tests.goal3755_robot_collision_hiprt_route_readiness_test tests.goal3753_amd_hiprt_benchmark_parity_plan_test
timeout 60 python -m py_compile src/rtdsl/v2_10_amd_hiprt_benchmark_parity.py tests/goal3756_robot_collision_amd_parity_contract_correction_test.py
```

All listed focused checks passed. This remains source/planning evidence, not
AMD HIPRT hardware evidence.
