# Goal2415 RT-DBSCAN Microcell Pod Evidence

Date: 2026-05-19

Status: pod evidence complete; microcell continuation is correctness-valid but
performance-negative

## Purpose

Goal2415 tested the Goal2414 clique-safe microcell continuation on the RTX A5000
pod. The question was whether the corrected microcell graph fast path could beat
the existing Goal2405 path:

```text
OptiX RT count-threshold device columns
  -> CuPy device-grid radius-graph component continuation
```

The answer is no for this implementation.

## Pod Environment

SSH target:

```text
root@69.30.85.177 -p 22055
```

Evidence checkout:

```text
/root/rtdl_goal2415
commit 0d95c04564e9d5f5db8fc1adb7cb306276030028
```

GPU:

```text
NVIDIA RTX A5000, driver 570.211.01
```

CUDA/OptiX:

```text
CUDA 12.8
RTDL_OPTIX_LIBRARY=/root/rtdl_goal2415/build/librtdl_optix.so
libnvrtc.so.12 resolved from /usr/local/cuda-12
```

CuPy:

```text
cupy 14.0.1
```

## Correctness

The focused Goal2414 test passed on the pod:

```text
5 tests OK
```

The timing matrix also reported:

```text
signatures_match = true
```

for all six dataset/size artifacts.

## Timing Method

For each row:

```text
repeat_count = 3
warm-tail median = median(repeats 2 and 3)
```

Compared modes:

```text
partner_cupy_grid_components_3d
optix_rt_core_flags_cupy_grid_components_3d
optix_rt_core_flags_cupy_microcell_graph_components_3d
```

Artifacts:

```text
docs/reports/goal2415_rt_dbscan_microcell_pod_evidence/
```

## Warm-Tail Timing Summary

| Dataset / points | Pure CuPy grid app sec | RT-count + CuPy grid app sec | RT-count + microcell app sec | Microcell vs RT-grid | Microcell fast path |
| --- | ---: | ---: | ---: | ---: | --- |
| clustered3d / 32768 | 0.191363 | 0.209644 | 0.239261 | 1.141x slower | false, fallback |
| clustered3d / 65536 | 0.526624 | 0.543523 | 0.572950 | 1.054x slower | true |
| clustered3d / 131072 | 1.641993 | 1.407486 | 1.412520 | 1.004x slower | true |
| road3d / 32768 | 0.104604 | 0.194789 | 0.298301 | 1.531x slower | true |
| road3d / 65536 | 0.281307 | 0.451593 | 0.748663 | 1.658x slower | true |
| road3d / 131072 | 0.682793 | 1.056031 | 2.162319 | 2.048x slower | true |

## Continuation Timing

When the microcell fast path activated, the continuation itself was also slower
than the existing CuPy device-grid continuation:

| Dataset / points | Existing CuPy-grid continuation sec | Microcell continuation sec | Result |
| --- | ---: | ---: | --- |
| clustered3d / 65536 | 0.1816 | 0.2414 | microcell slower |
| clustered3d / 131072 | 0.5925 | 0.6398 | microcell slower |
| road3d / 32768 | 0.0236 | 0.1331 | microcell much slower |
| road3d / 65536 | 0.0876 | 0.4315 | microcell much slower |
| road3d / 131072 | 0.2898 | 1.5153 | microcell much slower |

## Interpretation

The microcell correction solved a real correctness problem, but it made the
performance model worse:

- `microcell_size = radius / sqrt(3)` is clique-safe, but it creates more cells
  than the radius grid.
- The safe neighbor stencil is `5 x 5 x 5`, not `3 x 3 x 3`.
- Cross-microcell exact pair checks add work.
- Sparse/road-shaped data suffers badly because many microcells have little
  useful aggregation but still pay the wider stencil cost.

For dense clustered 131k, microcell nearly ties the existing RT-grid path, but
does not beat it. For road-shaped data, it is clearly worse.

## Decision

Do not promote the microcell continuation as the next performance path.

Keep the implementation as a correctness-valid experimental generic adapter,
but do not use it as evidence that RTDL improved RT-DBSCAN continuation
performance.

The next implementation target should pivot to Candidate A from Goal2408:

```text
prepared CuPy grid continuation hardening
```

That means caching or reusing the existing grid continuation's stable work:

- point columns;
- cell ids;
- sorted order;
- unique cells;
- starts/counts;
- output buffers;
- repeated-run prepared state.

This is less glamorous than microcell graph compression, but the evidence says
the existing point-grid continuation is already the stronger algorithmic base.

## Boundary

This report does not authorize a release claim, broad RT-core speedup claim,
RT-DBSCAN paper reproduction claim, or v2.x closure. It records a negative
performance result and a next engineering pivot.
