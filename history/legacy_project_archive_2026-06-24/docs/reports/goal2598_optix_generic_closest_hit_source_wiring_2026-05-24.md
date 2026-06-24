# Goal2598: OptiX Generic 3-D Closest-Hit Source Wiring

Date: 2026-05-24

Update: the NVIDIA gate described in this report was completed in
`docs/reports/goal2599_gpu_rmq_optix_closest_hit_pod_validation_2026-05-24.md`.
The claim boundary below documents the source-wiring state before that pod
validation.

## Purpose

GPU-RMQ needs the paper-style RT lowering to use RTDL's generic RT primitive
surface, not a CuPy-only hierarchy and not an RMQ-specific native shortcut. The
missing engine capability was a native OptiX row primitive for:

```text
ray_triangle_closest_hit_3d(rays, triangles) -> rows(ray_id, triangle_id, t)
```

This is app-agnostic. The native engine sees only 3-D rays and 3-D triangles.
RMQ block construction, query scheduling, tie policy, and primitive-id decoding
remain in Python app code.

## Source Changes

- Added `RtdlRayClosestHitRow` and `rtdl_optix_run_ray_closest_hit_3d` to the
  native OptiX ABI.
- Added a generic OptiX custom-primitive closest-hit kernel that reports the
  closest ray/triangle hit per ray and returns hit distance `t`.
- Added the native workload wrapper `run_ray_closest_hit_3d_optix`.
- Exposed the new row contract through `rtdsl.optix_runtime`.
- Allowed `run_generic_ray_triangle_closest_hit(..., backend="optix")` to route
  through the generic OptiX runtime for 3-D inputs.
- Updated GPU-RMQ docs and claim boundaries to distinguish source-wired OptiX
  support from pod-validated readiness.
- Added `scripts/goal2598_optix_closest_hit_validation.py` as the reusable pod
  validation driver.

## Claim Boundary

Allowed now:

- "native OptiX generic closest-hit source path is wired";
- "the path is app-agnostic and uses ray/triangle inputs plus generic rows";
- "GPU-RMQ can request `--rt-backend optix` once an updated native library is
  built on NVIDIA".

Not allowed yet:

- "GPU-RMQ OptiX path is validated";
- "GPU-RMQ uses RT cores in measured evidence";
- "RTDL beats author code/CUDA/CuPy on GPU-RMQ";
- any public speedup wording.

## Validation Performed Locally

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2594_gpu_rmq_benchmark_front_door_test \
  tests.goal2595_gpu_rmq_author_runner_test \
  tests.goal2598_optix_generic_closest_hit_contract_test -v

PYTHONPATH=src:. python3 -m py_compile \
  src/rtdsl/generic_primitives.py \
  src/rtdsl/optix_runtime.py \
  examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py \
  scripts/goal2598_optix_closest_hit_validation.py \
  tests/goal2598_optix_generic_closest_hit_contract_test.py

PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py \
  --mode scope | python3 -m json.tool

PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py \
  --mode paper_rt_lowering_reference --dataset repeated --value-count 257 \
  --query-count 73 --max-width 64 --block-size 16 --no-sample | python3 -m json.tool

PYTHONPATH=src:. python3 scripts/goal2598_optix_closest_hit_validation.py \
  --backend cpu --skip-gpu-rmq | python3 -m json.tool
```

Result: all 18 targeted unit tests passed; syntax checks, JSON smokes, and the
CPU-mode validation driver smoke passed.

## Remaining NVIDIA Gate

This Mac cannot build or execute the CUDA/OptiX native backend. The next pod
step is:

1. Build the native OptiX library from this source tree.
2. Run
   `PYTHONPATH=src:. python3 scripts/goal2598_optix_closest_hit_validation.py --backend optix`
   to check no-tie closest-hit correctness against CPU reference and exercise
   GPU-RMQ through `--rt-backend optix`.
3. Run GPU-RMQ `paper_rt_lowering_reference --rt-backend optix`.
4. Record build environment, git commit, correctness rows, and timing.

Tie policy note: the GPU-RMQ app already encodes a tiny app-side x offset to
preserve leftmost-minimum semantics. The generic OptiX closest-hit path is a
float-approx RT primitive and should be validated first on no-tie geometric
fixtures before app-level tie behavior is claimed.
