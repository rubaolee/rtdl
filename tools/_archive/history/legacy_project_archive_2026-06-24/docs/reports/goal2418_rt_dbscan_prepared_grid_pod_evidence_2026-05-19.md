# Goal2418 RT-DBSCAN Prepared Grid Pod Evidence

Date: 2026-05-19

Status: pod evidence complete; prepared grid continuation is a useful win over
the prior RT-grid bridge, with remaining sparse-road gap against pure CuPy

## Purpose

Goal2418 measures the Goal2417 prepared CuPy grid continuation on the RTX A5000
pod. It follows the negative Goal2415 microcell result and asks a narrower
question:

```text
Can RTDL improve the existing RT-core DBSCAN bridge by reusing generic partner
grid state and output workspaces across repeated runs?
```

The answer is yes against the prior RT-grid bridge. The prepared mode is faster
than the old RT-count plus fresh CuPy-grid path on every measured row. It also
beats the pure CuPy-grid baseline on clustered data, but sparse road-shaped data
still favors or nearly ties pure CuPy.

## Pod Environment

SSH target:

```text
root@69.30.85.177 -p 22055
```

Evidence checkout:

```text
/root/rtdl_goal2415
commit 225d823cff8dfd2f576343f95f79e76a07ee7035
```

GPU/runtime:

```text
NVIDIA RTX A5000, driver 570.211.01
Python 3.12.3
CuPy 14.0.1
RTDL_OPTIX_LIBRARY=/root/rtdl_goal2415/build/librtdl_optix.so
```

Artifacts:

```text
docs/reports/goal2418_rt_dbscan_prepared_grid_pod_evidence/
```

## Compared Modes

```text
partner_cupy_grid_components_3d
optix_rt_core_flags_cupy_grid_components_3d
optix_rt_core_flags_cupy_prepared_grid_components_3d
```

For the prepared mode, the repeat probe prepares the OptiX scene, CuPy point
columns, cell ids, sorted order, unique-cell ranges, and output workspaces once.
It then repeats only the RT count-threshold pass and the prepared CuPy component
continuation. Each row uses `repeat_count = 3`; timing below is the warm-tail
median of repeats 2 and 3.

All six artifacts report:

```text
signatures_match = true
prepared_grid_reused = [false, true, true]
```

## Timing Summary

| Dataset / points | Pure CuPy grid app sec | Old RT-count + fresh CuPy grid app sec | Prepared RT-count + prepared CuPy grid app sec | Prepared vs old RT-grid | Prepared vs pure CuPy |
| --- | ---: | ---: | ---: | ---: | ---: |
| clustered3d / 32768 | 0.180449 | 0.260300 | 0.179105 | 1.453x faster | 1.008x faster |
| clustered3d / 65536 | 0.514252 | 0.530600 | 0.374435 | 1.417x faster | 1.373x faster |
| clustered3d / 131072 | 1.595031 | 1.406601 | 1.027512 | 1.369x faster | 1.552x faster |
| road3d / 32768 | 0.105955 | 0.235569 | 0.146501 | 1.608x faster | 0.723x of CuPy |
| road3d / 65536 | 0.273780 | 0.403268 | 0.296462 | 1.360x faster | 0.923x of CuPy |
| road3d / 131072 | 0.711260 | 0.963975 | 0.724791 | 1.330x faster | 0.981x of CuPy |

## Interpretation

Prepared reuse solved the main avoidable overhead in the RT-grid bridge:

- the CuPy cell ids, sort order, unique-cell index, starts/counts, and output
  workspaces are no longer rebuilt in the steady-state repeat loop;
- the OptiX prepared scene is reused by the repeat probe;
- no neighbor rows are materialized;
- the native engine remains app-agnostic.

This turns the old RT-count bridge from a repeated setup penalty into a real
composition path. Clustered data now shows the intended result: RT traversal for
core flags plus reusable CUDA partner continuation beats pure CuPy at larger
sizes.

Road-shaped data remains the weak spot. The RT phase is still useful as a true
RT-core phase, but pure CuPy's uniform grid is already very cheap for the sparse
manifold shape, so even after preparation the composed RT path is slower at 32k
and 65k and only near parity at 131k.

## Decision

Promote the prepared grid continuation as the current RT-DBSCAN bridge baseline:

```text
OptiX RT count-threshold device columns
  -> prepared CuPy radius-grid component continuation
```

Do not promote the microcell continuation as the performance path.

The next useful work is not another DBSCAN-specific native function. It is a
larger generic continuation primitive that can avoid redoing radius traversal in
the continuation phase for sparse manifolds, while still preserving correctness:

```text
generic device-resident radius-graph edge stream or grouped union continuation
```

## Claim Boundary

This report authorizes only a narrow engineering conclusion:

```text
Prepared generic partner continuation improves the RTDL RT-DBSCAN bridge over
the old fresh-grid bridge on this RTX A5000 pod.
```

It does not authorize:

- paper reproduction;
- broad DBSCAN acceleration claims;
- whole-application speedup claims beyond the rows above;
- a release gate;
- a DBSCAN-specific native ABI.
