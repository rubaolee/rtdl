# Gemini OptiX Goals 695/727 Work Report

Date: 2026-04-21

## Status

This file records the Gemini-started OptiX instrumentation work after Dev AI
review and boundary correction.

Verdict after Dev AI review: accept as instrumentation, not as RTX speedup
evidence.

## Accepted Code Shape

- 2D OptiX `GpuPoint` records are padded to 16 bytes.
- `rtdl_optix_get_last_phase_timings(...)` exposes the latest C-side timing
  split for fixed-radius summary execution.
- Python exposes those timings through
  `rtdsl.optix_runtime.get_last_phase_timings()`.
- Goal695 and Goal727 profiler scripts can report:
  - Python input construction
  - packing
  - C-side BVH build
  - C-side OptiX launch/traversal
  - C-side copy-back
  - FFI/backend-call overhead
  - Python post-processing

## Validation

Linux GTX 1070 host:

- `make build-optix` passed
- `tests.goal695_optix_fixed_radius_summary_test` passed
- `tests.goal691_optix_robot_summary_profiler_test` passed
- Goal695 and Goal727 profilers emitted `c_optix_launch_and_traversal`

## Corrected Boundary

The original draft language implied that the padding change directly proves
RTX speedup. That is too strong and is not preserved.

The accepted boundary is:

- padding is a low-risk data-layout polish
- phase timings are instrumentation for future RTX measurement
- the GTX 1070 host has no RT cores and cannot prove RT-core speedup
- public app-speedup claims require RTX-class hardware evidence

## App Classification

| App family | Current status |
| --- | --- |
| Outlier fixed-radius summary | OptiX traversal-capable prototype; RTX claim pending |
| DBSCAN core-flag summary | OptiX traversal-capable prototype; RTX claim pending |
| Robot prepared count | keep existing bounded prepared-count evidence |
| Hausdorff | no RT-core app claim yet |
| ANN/KNN ranking | no RT-core app claim yet |
| Barnes-Hut | no RT-core app claim yet |

The important observed caveat from Goal695 profiling is that fixed-radius
summary mode matched oracle on the profiler fixture, while the older OptiX row
path did not. Do not promote broad row-path claims from this work.
