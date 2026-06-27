# Goal 727: OptiX RTX Claim Status

Date: 2026-04-21

## Verdict

Status: hold for RTX hardware evidence.

The current OptiX work adds useful fixed-radius summary instrumentation and a
low-risk 16-byte point-layout polish. It does not yet justify a broad public
claim that RTDL apps are accelerated by NVIDIA RT cores.

## What Is Integrated

- `GpuPoint` in the OptiX 2D point kernels is padded from 12 bytes to 16 bytes.
- `rtdl_optix_get_last_phase_timings(...)` exposes C-side timings for:
  - BVH build
  - OptiX launch/traversal
  - copy-back
- Python exposes these timings through
  `rtdsl.optix_runtime.get_last_phase_timings()`.
- Two profiler scripts exist for fixed-radius summary investigation:
  - `scripts/goal695_optix_fixed_radius_summary_profiler.py`
  - `scripts/goal727_optix_fixed_radius_phase_profiler.py`

## App Claim Classification

| App family | Current OptiX status | Public claim allowed now |
| --- | --- | --- |
| Outlier detection fixed-radius summary | OptiX traversal-capable summary prototype | correctness/instrumentation only until RTX timing exists |
| DBSCAN core-flag summary | OptiX traversal-capable summary prototype | correctness/instrumentation only until RTX timing exists |
| Robot collision prepared count | existing prepared OptiX any-hit path | keep previous bounded prepared-count evidence; do not generalize |
| Hausdorff | KNN/row path, not proven RT-core traversal app | no RT-core app claim |
| ANN/KNN ranking | KNN/row path, not proven RT-core traversal app | no RT-core app claim |
| Barnes-Hut | candidate-row path plus Python force reduction | no RT-core app claim |

## Why The Hold Is Required

RTDL needs two separate measurements before making public RTX app-performance
claims:

- backend phase evidence: the isolated `c_optix_launch_and_traversal` metric on
  an RTX-class GPU
- app evidence: whole-app timings showing whether Python packing,
  materialization, copy-back, and post-processing erase or preserve the backend
  gain

The Linux GTX 1070 host can compile and run OptiX, but it has no NVIDIA RT
cores. It is useful for correctness and API validation only.

## Recent Linux Validation

On `lestat@192.168.1.20`:

- `make build-optix` passed
- focused tests passed:
  - `tests.goal695_optix_fixed_radius_summary_test`
  - `tests.goal691_optix_robot_summary_profiler_test`
- the Goal695 profiler emitted phase fields including
  `c_optix_launch_and_traversal`

Observed caveat:

- fixed-radius summary mode matched the CPU/oracle result for the profiler
  fixture
- the older OptiX row path did not match oracle for that same app fixture

This reinforces the current boundary: promote only tested summary-mode
correctness, not broad fixed-radius row-mode app claims.

## Next Required Step

Before release-level RTX wording, run the fixed-radius summary profiler and
app-level benchmarks on rented RTX hardware and compare:

- CPU/oracle correctness
- OptiX rows mode
- OptiX summary mode
- Embree reference timing
- whole-app timing and isolated `c_optix_launch_and_traversal`
