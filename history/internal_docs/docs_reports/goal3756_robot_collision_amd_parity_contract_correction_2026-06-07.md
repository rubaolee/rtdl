# Goal3756 Robot Collision AMD Parity Contract Correction

Date: 2026-06-07

## Purpose

Goal3755 exposed `--backend hiprt` for the robot collision screening app using
the generic HIPRT Ray2D/Triangle2D any-hit row path. Goal3756 corrected the
v2.10 AMD/HIPRT parity ledger so the first AMD robot collision target named the
actual 2D contract. Goal3765 extends that state with a HIPRT prepared grouped
visibility-flag summary on the NVIDIA CUDA/Orochi path.

## Correction

The robot collision parity row now requires:

- `ray_triangle_any_hit_2d`
- `visibility_rows`
- `prepared_grouped_visibility_flags_2d`

It no longer names `ray_triangle_any_hit_3d` for this app, because the public
robot collision screening fixture is a 2D edge-ray versus 2D obstacle-triangle
route. After Goal3765, the prepared grouped visibility-flag summary is no longer
OptiX-only; HIPRT now exposes the same generic app-free grouped flag contract.

## Boundary

This is a planning/source correction plus NVIDIA CUDA/Orochi-path evidence. It
still provides no AMD performance evidence. The first AMD pod run should
validate both the row route and the prepared grouped flag route:

```bash
PYTHONPATH=src:. python examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py --backend hiprt --output-mode pose_flags
PYTHONPATH=src:. python examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py --backend hiprt --optix-summary-mode prepared_pose_flags --output-mode pose_flags
```

The target is HIPRT functional parity for the app's row-backed collision flags
and the generic prepared grouped visibility flags.

## Acceptance

- The v2.10 parity ledger names `ray_triangle_any_hit_2d` for robot collision.
- The app support matrix exposes HIPRT for robot collision.
- Goal3765 exposes HIPRT prepared grouped visibility flags without app-specific
  native engine logic.
- Claim boundaries remain false: no release, AMD performance, broad RT-core,
  whole-app, or paper-reproduction claim is authorized.

## Validation

Local Windows:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3756_robot_collision_amd_parity_contract_correction_test tests.goal3755_robot_collision_hiprt_route_readiness_test tests.goal3753_amd_hiprt_benchmark_parity_plan_test tests.goal3765_hiprt_prepared_grouped_anyhit_flags_test.Goal3765HiprtPreparedGroupedAnyhitFlagsPortableTest
py -3 -m py_compile src\rtdsl\v2_10_amd_hiprt_benchmark_parity.py tests\goal3756_robot_collision_amd_parity_contract_correction_test.py tests\goal3765_hiprt_prepared_grouped_anyhit_flags_test.py
```

Current A5000 pod:

```bash
cd /root/rtdl_goal3765_clean
export PYTHONPATH=src:.
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
timeout 120 python3 -m unittest tests.goal3765_hiprt_prepared_grouped_anyhit_flags_test tests.goal674_hiprt_prepared_anyhit_2d_test tests.goal3764_robot_collision_hiprt_cuda_path_app_smoke_test
timeout 900 python3 scripts/goal3765_robot_collision_hiprt_prepared_group_flags_probe.py --timing-pose-counts 64,128,256,512,1024 --correctness-pose-counts 32,128 --warmup 1 --repeat 3 --output docs/reports/goal3765_robot_collision_hiprt_prepared_group_flags_a5000.json
```

All listed focused checks passed. This remains source/planning evidence, not
AMD HIPRT hardware evidence.
