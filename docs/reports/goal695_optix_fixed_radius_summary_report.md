# Goal 695: OptiX Fixed-Radius Summary Instrumentation

Date: 2026-04-21

## Scope

This goal integrates and hardens the Gemini-started OptiX fixed-radius summary
instrumentation. The work is intentionally narrow:

- expose C-side phase timings for `fixed_radius_count_threshold_2d_optix`
- preserve the existing fixed-radius summary ABI
- keep app-level RTX claims pending until the profiler runs on an RTX-class
  cloud machine

## Code Changes

- `src/native/optix/rtdl_optix_workloads.cpp`
  - records thread-local C-side timings for BVH build, OptiX launch/traversal,
    and copy-back inside `run_fixed_radius_count_threshold_rt`
  - exports `rtdl_optix_get_last_phase_timings(...)`
- `src/native/optix/rtdl_optix_prelude.h`
  - declares the timing export
- `src/rtdsl/optix_runtime.py`
  - exposes `get_last_phase_timings()`
- `scripts/goal695_optix_fixed_radius_summary_profiler.py`
  - profiles outlier fixed-radius summary execution and reports C-side phase
    timings separately from Python input construction, packing, and
    post-processing

The separate `GpuPoint` 16-byte padding change is a low-risk data-layout polish
for 2D point kernels. It is not, by itself, speedup evidence.

## Linux Validation

Host:

- `/tmp/rtdl_goal731` on `lestat@192.168.1.20`

Commands:

```bash
make build-optix
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal695_optix_fixed_radius_summary_test \
  tests.goal691_optix_robot_summary_profiler_test
PYTHONPATH=src:. python3 scripts/goal695_optix_fixed_radius_summary_profiler.py \
  --iterations 2 --copies 64
```

Results:

- OptiX library built successfully.
- 7 focused tests passed.
- The profiler returned C-side timing fields:
  - `c_bvh_build`
  - `c_optix_launch_and_traversal`
  - `c_copy_back`
  - `c_ffi_overhead`

Important correctness observation:

- `optix_summary.matched_oracle` was `true`.
- `optix_rows.matched_oracle` was `false` for this outlier fixture.

Therefore the accepted claim is limited to the fixed-radius summary path under
the tested conditions. This report does not promote the older row-emission
fixed-radius app path.

## Boundary

This is an instrumentation and layout-polish goal, not a release-level RTX
speedup claim.

Any future claim that an app is accelerated by NVIDIA RT cores must use:

- RTX-class hardware, not the GTX 1070 no-RT-core Linux host
- the isolated `c_optix_launch_and_traversal` metric
- correctness parity against the CPU/oracle result
- a separate whole-app timing table that clearly includes Python packing,
  backend execution, copy-back, and app post-processing

Until that evidence exists, outlier and DBSCAN fixed-radius summary modes may
be described as OptiX traversal-capable prototypes, not broad app-performance
wins.
