# Goal3764 Robot Collision HIPRT CUDA-Path App Smoke

Date: 2026-06-07

## Purpose

Goal3763 proved that the HIPRT SDK can be installed, `make build-hiprt` can
build, and focused HIPRT unit tests pass on the NVIDIA A5000 through the
CUDA/Orochi path. Goal3764 moves one step closer to benchmark-app readiness by
running the public robot collision app route itself:

```bash
python scripts/goal3764_robot_collision_hiprt_cuda_path_app_smoke.py
```

The app route is:

- `examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py`
- backend: `hiprt`
- output mode: compact `hit_count` for timing rows and `pose_flags` for
  correctness rows.

This is not AMD hardware performance evidence. It is a functional and timing
smoke for the HIPRT CUDA/Orochi route on NVIDIA.

## Evidence

Artifact:
`docs/reports/goal3764_robot_collision_hiprt_cuda_path_app_smoke_a5000.json`

Clean source evidence:

- source commit: `32f2f011`
- GPU: NVIDIA RTX A5000, driver 580.126.09
- correctness cases: 2
- correctness verdict: all match CPU oracle
- timing warmup / repeat: 1 / 3

Timing rows:

| Poses | Edge rays | Obstacle triangles | Hit edges | HIPRT median sec |
| ---: | ---: | ---: | ---: | ---: |
| 64 | 256 | 128 | 168 | 0.661591 |
| 128 | 512 | 256 | 351 | 0.791469 |
| 256 | 1,024 | 512 | 720 | 0.670851 |
| 512 | 2,048 | 1,024 | 1,500 | 0.685817 |

The timing is intentionally recorded as bounded route behavior, not a speedup
claim. The public HIPRT row path materializes per-edge rows and then summarizes
in Python. The faster prepared pose-flag summary remains OptiX-only until HIPRT
has a generic prepared ray-buffer/group-index contract.

## Interpretation

This is a useful AMD-lane preparation step:

- The public app route now has a real HIPRT smoke path on the pod.
- The output agrees with the CPU oracle for demo and scaled correctness cases.
- The next AMD pod can run the same script first, before deeper prepared HIPRT
  work.

It also shows the current limitation:

- Robot collision's HIPRT route is row-backed.
- It is not yet the optimized prepared pose-level summary route.
- A future HIPRT prepared-buffer/group-index primitive is needed before this
  app can fairly compete with the OptiX prepared pose-flag path.

## Claim Boundary

This goal does not authorize release action, AMD hardware performance wording,
whole-app acceleration wording, broad RT-core wording, paper reproduction
wording, or app-specific native-engine logic.
