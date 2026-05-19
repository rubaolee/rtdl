# Goal2401 RT-DBSCAN OptiX Summary Bridge Pod Evidence

Date: 2026-05-19

Status: clean RTX A5000 pod evidence for the Goal2400 bridge

## Environment

Artifacts:

```text
docs/reports/goal2401_rt_dbscan_optix_summary_bridge_pod/
```

The pod runner was executed from a clean checkout of:

```text
00a349c7f60fe814432e1758caf3f531d77bb27b
```

Hardware and runtime recorded by `environment.txt`:

```text
Python 3.12.3
NVIDIA RTX A5000, driver 570.211.01
CuPy 14.0.1
RTDL_OPTIX_LIBRARY=/root/rtdl_goal2392_pod/build/librtdl_optix.so
```

## Results

| Dataset | Points | Mode | Seconds | Signature check | Boundary |
| --- | ---: | --- | ---: | --- | --- |
| `clustered3d` | 4096 | host-bucket CuPy continuation | 2.015462 | same as bridge/grid | old host-index debt |
| `clustered3d` | 4096 | repaired CuPy device grid | 0.546740 | same as bridge/host | CUDA-core partner baseline |
| `clustered3d` | 4096 | OptiX-backend summaries + CuPy device grid | 1.353580 | same as grid/host | prepared uniform-cell CUDA summaries, no neighbor rows |
| `road3d` | 4096 | host-bucket CuPy continuation | 0.955771 | same as bridge/grid | old host-index debt |
| `road3d` | 4096 | repaired CuPy device grid | 0.606979 | same as bridge/host | CUDA-core partner baseline |
| `road3d` | 4096 | OptiX-backend summaries + CuPy device grid | 1.378416 | same as grid/host | prepared uniform-cell CUDA summaries, no neighbor rows |
| `clustered3d` | 1024 | OptiX-backend prepared rows | 1.448650 | timed row only | prepared uniform-cell CUDA rows, host row materialization |
| `road3d` | 1024 | OptiX-backend prepared rows | 1.251717 | timed row only | prepared uniform-cell CUDA rows, host row materialization |

Hybrid bridge phase timing from metadata:

| Dataset | OptiX-backend summary seconds | CuPy continuation seconds | Summary rows | Neighbor rows materialized |
| --- | ---: | ---: | ---: | --- |
| `clustered3d` | 1.072229 | 0.116596 | 4096 | false |
| `road3d` | 1.100715 | 0.111880 | 4096 | false |

## Interpretation

Goal2400 successfully added a generic bridge that avoids O(edges) neighbor-row
materialization. The bridge consumes OptiX-backend per-query fixed-radius
summaries from the prepared uniform-cell CUDA path and feeds threshold core
flags into the CuPy device-grid component continuation.

The evidence is mixed in the useful way:

- Correctness shape is good: the hybrid signatures match the host-bucket and
  pure CuPy device-grid signatures for both 4096-point timed datasets.
- Data movement shape is better than `optix_prepared_rows`: only 4096 summary
  rows are materialized, not hundreds of thousands or millions of neighbor rows.
- Performance is not yet the final win: the hybrid bridge is faster than the
  old host-bucket continuation on `clustered3d`, but slower than the pure CuPy
  device-grid baseline on both datasets because backend summary setup dominates
  at about 1.1 seconds.

## Design Lesson

The bridge proves that RTDL can compose generic backend summary primitives with
generic partner continuation primitives. It also shows the next runtime problem
clearly: for RT-DBSCAN-level performance, either a true RT traversal summary
path must write device-resident outputs into the component continuation, or the
prepared uniform-cell summary path must become much cheaper across repeated
calls.

## Claim Boundary

Goal2401 is `accept-with-boundary`.

- Accept: the generic OptiX-summary-to-CuPy-continuation bridge works, avoids
  neighbor-row materialization, and is supported by clean pod evidence.
- Boundary: this is not paper reproduction, not a paper-speedup claim, and not
  a broad RT-core DBSCAN acceleration claim. The prepared 3-D summary path in
  this evidence is an OptiX-backend uniform-cell CUDA path, not the RT-core
  paper path. The pure CuPy device-grid baseline remains faster on these two
  4096-point synthetic rows.

Short form: this prepared 3-D bridge is not the RT-core paper path.
