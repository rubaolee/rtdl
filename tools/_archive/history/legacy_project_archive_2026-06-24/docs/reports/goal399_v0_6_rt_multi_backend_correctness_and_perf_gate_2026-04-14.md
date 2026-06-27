# Goal 399 Report: v0.6 RT Multi-Backend Correctness And Performance Gate

Date: 2026-04-14
Status: implemented, review pending

## Summary

Goal 399 establishes the first bounded integrated gate across the corrected
RT-kernel graph line.

The current repo now has bounded graph workload closure for:

- Python truth path
- native/oracle
- Embree
- OptiX
- Vulkan

for:

- `bfs`
- `triangle_count`

with explicit local honesty about backend availability on this machine.

## Integrated Verification

Integrated graph backend suite:

```text
python3 -m unittest \
  tests.goal389_v0_6_rt_graph_bfs_truth_path_test \
  tests.goal390_v0_6_rt_graph_triangle_truth_path_test \
  tests.goal391_v0_6_rt_graph_bfs_oracle_test \
  tests.goal392_v0_6_rt_graph_triangle_oracle_test \
  tests.goal393_v0_6_rt_graph_bfs_embree_test \
  tests.goal394_v0_6_rt_graph_bfs_optix_test \
  tests.goal395_v0_6_rt_graph_bfs_vulkan_test \
  tests.goal396_v0_6_rt_graph_triangle_embree_test \
  tests.goal397_v0_6_rt_graph_triangle_optix_test \
  tests.goal398_v0_6_rt_graph_triangle_vulkan_test
```

Result:

- `Ran 45 tests`
- `OK (skipped=16)`

Linux integrated graph backend suite:

```text
ssh lestat-lx1 'cd /home/lestat/tmp/rtdl_v0_6_rt_check && \
python3 -m unittest \
  tests.goal389_v0_6_rt_graph_bfs_truth_path_test \
  tests.goal390_v0_6_rt_graph_triangle_truth_path_test \
  tests.goal391_v0_6_rt_graph_bfs_oracle_test \
  tests.goal392_v0_6_rt_graph_triangle_oracle_test \
  tests.goal393_v0_6_rt_graph_bfs_embree_test \
  tests.goal394_v0_6_rt_graph_bfs_optix_test \
  tests.goal395_v0_6_rt_graph_bfs_vulkan_test \
  tests.goal396_v0_6_rt_graph_triangle_embree_test \
  tests.goal397_v0_6_rt_graph_triangle_optix_test \
  tests.goal398_v0_6_rt_graph_triangle_vulkan_test'
```

Result:

- `Ran 45 tests`
- `OK`

Core quality gate:

```text
python3 -m unittest tests.test_core_quality
```

Result:

- `Ran 105 tests`
- `OK`

Linux core quality gate:

```text
ssh lestat-lx1 'cd /home/lestat/tmp/rtdl_v0_6_rt_check && \
python3 -m unittest tests.test_core_quality'
```

Result:

- `Ran 105 tests`
- `OK`

## Current Local Backend Availability

Observed on this macOS machine:

- Embree: available
- OptiX: unavailable
- Vulkan: unavailable

Observed on Linux `lestat-lx1`:

- Embree: available
- OptiX: available after building `librtdl_optix.so`
- Vulkan: available after building `librtdl_vulkan.so`

That means:

- Embree backend tests execute locally
- OptiX backend tests are present and part of the integrated suite, but are
  skipped locally by availability guards
- Vulkan backend tests are present and part of the integrated suite, but are
  skipped locally by availability guards

## Correctness State

Bounded correctness is now represented in the repo for both workloads:

- Python truth path:
  - `bfs`
  - `triangle_count`
- native/oracle:
  - `bfs`
  - `triangle_count`
- Embree:
  - `bfs`
  - `triangle_count`
- OptiX:
  - `bfs`
  - `triangle_count`
- Vulkan:
  - `bfs`
  - `triangle_count`

The checked hosts now split clearly:

- macOS:
  - Embree executes live
  - OptiX and Vulkan remain availability-gated
- Linux `lestat-lx1` after backend library build:
  - Embree executes live
  - OptiX executes live
  - Vulkan executes live

## Performance State

This Goal 399 gate is primarily a correctness/integration gate.

The current performance evidence is uneven by platform:

- Python/oracle paths are locally runnable
- Embree is runnable on both checked hosts
- OptiX and Vulkan are runnable on Linux after building the backend libraries
- macOS still does not provide live OptiX/Vulkan execution

So this goal does not make new OptiX/Vulkan performance claims. Those require
execution on machines where those runtimes are actually available.

## Honesty Boundary

Goal 399 proves:

- the integrated backend graph test surface exists
- the local integrated suite is green
- the Linux integrated suite is green with zero backend skips
- the current host boundaries are explicit

Goal 399 does not prove:

- release-grade multi-platform GPU parity
- final cross-backend performance conclusions
- that OptiX or Vulkan are executable on macOS

It is the first bounded integration gate, not the final release gate.
