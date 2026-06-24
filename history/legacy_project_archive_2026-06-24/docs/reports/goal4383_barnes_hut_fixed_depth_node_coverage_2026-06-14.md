# Goal4383 Barnes-Hut Fixed-Depth Node-Coverage Refresh

Date: 2026-06-14

Status: v2.14 cleanup evidence. This closes the previous "4-node toy" weakness for the measured Barnes-Hut node-coverage primitive, but it is still not a full RT-BarnesHut paper reproduction or whole N-body force-solver speedup claim.

## What Changed

The Barnes-Hut app and research benchmark now expose an explicit node topology for prepared node-coverage mode:

- `one_level`: the legacy default, preserving previous behavior.
- `fixed_depth_cells`: a fixed-depth quadtree-cell node fixture, selected with `--node-topology fixed_depth_cells --max-depth N`.

The large timing rows use the same generic RTDL primitive on both sides:

`PREPARED_FIXED_RADIUS_COUNT_THRESHOLD_2D / scalar threshold count`

The large rows skip the CPU oracle because exact validation is `O(body_count * node_count)`. A smaller 4,096 bodies x 4,096 nodes row validates both backends against the CPU oracle.

## Pod Configuration

- Pod: `root@157.157.221.29 -p 22234`
- Repo: `/workspace/rtdl`
- Embree threads: `RTDL_EMBREE_THREADS=64`
- OptiX library: `/workspace/rtdl/build/librtdl_optix.so`
- Embree library: `/workspace/rtdl/build/librtdl_embree.so`

## Results

| Case | Backend | Bodies | Nodes | Validation | Prepare sec | Hot query median sec | Measured query total sec |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: |
| depth=6 correctness | Embree | 4,096 | 4,096 | oracle match | 0.102677 | 0.015384 | 0.046384 |
| depth=6 correctness | OptiX RT cores | 4,096 | 4,096 | oracle match | 1.005260 | 0.004138 | 0.013005 |
| depth=8 large | Embree | 262,144 | 65,536 | skipped | 0.167346 | 1.076318 | 3.127134 |
| depth=8 large | OptiX RT cores | 262,144 | 65,536 | skipped | 0.769215 | 0.564885 | 1.584282 |
| depth=8 large | Embree | 1,000,000 | 65,536 | skipped | 0.164824 | 3.693226 | 11.312786 |
| depth=8 large | OptiX RT cores | 1,000,000 | 65,536 | skipped | 0.831387 | 1.791480 | 5.716277 |

## Same-Contract Speedups

| Case | Hot query speedup, Embree / OptiX | Interpretation |
| --- | ---: | --- |
| 4,096 bodies x 4,096 nodes | 3.72x | Correctness row; small enough for CPU oracle. |
| 262,144 bodies x 65,536 nodes | 1.91x | Large node-coverage primitive row; RT cores reduce traversal time, but OptiX one-time prepare remains higher. |
| 1,000,000 bodies x 65,536 nodes | 2.06x | Human-scale large row; the measured query phase is now seconds-level on both backends. |

## Conclusion

Barnes-Hut should no longer be described as only a 4-node toy primitive. For the prepared node-coverage threshold contract, v2.14 now has a large same-contract OptiX-vs-Embree row: 1,000,000 bodies against 65,536 fixed-depth quadtree nodes, with OptiX RT cores 2.06x faster on the hot query median.

The app-level claim boundary is unchanged. This is node-coverage traversal evidence, not Barnes-Hut opening-rule evaluation, not force-vector reduction, not timestep integration, not an authors-code comparison, and not public wording for full RT-BarnesHut.
