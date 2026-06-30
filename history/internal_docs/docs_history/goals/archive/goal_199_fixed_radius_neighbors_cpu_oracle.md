# Goal 199: Fixed-Radius Neighbors CPU/Oracle Closure

Date: 2026-04-10
Status: planned

## Goal

Make `fixed_radius_neighbors` fully working on the correctness-first native
CPU/oracle path.

This goal covers:

- lowering support
- native CPU/oracle execution
- parity against the Python truth path
- bounded baseline-runner `cpu` support

## Why this goal exists

Goal 198 established the Python truth path.

The next milestone is the first fully working RTDL runtime path for the
workload. That means users can author the kernel, lower it, and execute it
through `run_cpu(...)` with row parity against the Python reference.

## Required result

This goal is complete when:

- `rt.lower_to_execution_plan(...)` supports `fixed_radius_neighbors`
- `rt.run_cpu(...)` supports the workload through the native oracle runtime
- authored and fixture cases match the Python truth path
- `run_baseline_case(..., backend="cpu")` works for the workload
- bounded tests prove the new path end to end

## Non-goals

This goal does not:

- add Embree support
- add OptiX or Vulkan support
- make performance claims
- close the external CPU baseline story
