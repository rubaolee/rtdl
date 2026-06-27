# V4 App-Level Benchmark Summary

This page gives the current app-level performance table for RTDL V4.0.0 on
NVIDIA RT-core hardware.

## How To Read The Table

- Each promoted benchmark app has V2.14, V3.0.2, and V4.0 rows.
- The comparison uses NVIDIA OptiX / RT-core rows as the primary hardware path.
- Embree is a CPU control in this project, not the primary denominator for this
  table.
- A ratio above `1.0x` means the V4 row is faster for the measured hot path.
- A ratio near `1.0x` means the row is similar-speed on this measurement.
- The table supports row-by-row reading. It does not say every benchmark app is
  faster in V4.

## 10-App RT-Core Table

| App | V4/V2.14 hot | V4/V3.0.2 hot | Reading |
| --- | ---: | ---: | --- |
| RTDBSCAN | `0.998x` | `0.993x` | Similar speed. |
| RayDB-style | `1.113x` | `1.111x` | Modest hot-path gain. |
| Triangle counting | `4.360x` | `1.021x` | Material hot-path gain over V2.14. |
| LibRTS spatial index | `0.999x` | `1.002x` | Similar speed. |
| Hausdorff XHD threshold route | `1.032x` | `0.983x` | Same-primitive threshold row with similar speed. |
| Robot collision | `1.020x` | `1.000x` | Similar speed; the inherited OptiX primitive remains usable in V4. |
| Contact manifold | `1.116x` | `1.477x` | Similar speed to modest gain on the measured hot subpipeline. |
| RTNN | `1.029x` | `1.024x` | Similar speed. |
| Spatial RayJoin shape-pair | `1.000x` | `1.004x` | Serious generated-input row with similar speed. |
| Barnes-Hut aggregate frontier | `286.142x` | `0.993x` | Material V3/V4-over-V2.14 row; V4 is similar-speed to V3 on this route. |

The V4/V2.14 hot-path geomean for this table is `2.10069x`. Treat it as a
summary statistic, not as the headline result, because Triangle counting and
Barnes-Hut dominate it. The table distribution is more informative.

In short: two material hot-path rows over V2.14, with similar-speed or
modest-gain rows elsewhere.

## Notes On Specific Rows

### Hausdorff

The table row uses the threshold route because that is the same RT-core
primitive family available across the compared versions. V3 and V4 also expose
an exact nearest-witness route. That exact route is useful, but it is a richer
query than the V2.14 threshold route, so it is reported separately.

### Barnes-Hut

The large V4/V2.14 number comes from removing a V2.14 host-frontier bottleneck
that was already addressed by the V3 device-continuation direction and is now
available through the V4 system. Because V4 and V3 are similar on this row, read
it as a V3/V4-over-V2.14 result, not as a new V4-over-V3 speedup.

### Spatial RayJoin

This row uses generated grid64 shape-pair input rather than a tiny smoke input.
The current result is a serious similar-speed row, not a speed win.

## V4-Specific Workflow

The custom predicate early-exit workflow is separate from the legacy 10-app
matrix. It shows V4-specific operator pushdown for a constrained Numba
predicate:

| Workflow | V4/V2.14 | V4/V3.0.2 | Reading |
| --- | ---: | ---: | --- |
| Custom predicate early-exit | `4.633x` | `4.633x` | RTDL evaluates a constrained Numba predicate inside the any-hit path and avoids materializing all hits. |

## Next Reading

- Operator surfaces: [learn/operator_catalog.md](learn/operator_catalog.md)
- Benchmark-app recipes: [../examples/benchmark_apps/README.md](../examples/benchmark_apps/README.md)
- Tutorial path: [../tutorials/current/README.md](../tutorials/current/README.md)
