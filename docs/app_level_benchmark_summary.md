# V4 App-Level Benchmark Summary

This page is the current public app-level performance boundary for V4.0.0.

## Current Decision

The V4.0.0 release matrix completed a serious NVIDIA RT-core POD run for the 10
promoted benchmark apps:

- V2.14, V3.0.2, and V4.0 rows are present for every app.
- All 30 rows returned success and parseable JSON.
- Embree is not used as a primary denominator.
- The Spatial RayJoin row uses generated grid64 shape-pair input, not a tiny
  overlay smoke input.
- The table has no `n/a` rows.

Decision label:

```text
complete_rt_core_app_matrix__bounded_material_wins__no_broad_all_app_speedup_claim
```

V4.0.0 is a published Python eDSL/operator-pushdown release and a V2/V3
superset. The complete app matrix supports bounded claims: two material hot-path
rows over V2.14, similar-speed control rows elsewhere, and no hot-path
regressions in this run. The supported reading is the distribution of rows
below, not "all benchmark apps are faster."

## Current 10-App RT-Core Rows

| App | V4/V2.14 hot | V4/V3.0.2 hot | Current reading |
| --- | ---: | ---: | --- |
| RTDBSCAN | `0.998x` | `0.993x` | Similar-speed control row. |
| RayDB-style | `1.113x` | `1.111x` | Modest RT-core hot gain; below broad-app headline bar. |
| Triangle counting | `4.360x` | `1.021x` | Material hot-path row. |
| LibRTS spatial index | `0.999x` | `1.002x` | Similar-speed control row. |
| Hausdorff XHD threshold route | `1.032x` | `0.983x` | Same-primitive threshold row with similar speed. |
| Robot collision | `1.020x` | `1.000x` | Similar-speed row; inherited OptiX primitive remains usable in V4. |
| Contact manifold | `1.116x` | `1.477x` | Similar-speed to modest gain on the measured hot subpipeline. |
| RTNN | `1.029x` | `1.024x` | Similar-speed control row. |
| Spatial RayJoin shape-pair | `1.000x` | `1.004x` | Serious generated-input row with similar speed. |
| Barnes-Hut aggregate frontier | `286.142x` | `0.993x` | Material V3/V4-over-V2.14 row; not a new V4-over-V3 speed claim. |

Hot-path geomean V4/V2.14: `2.10069x`.

Do not headline that geomean. It is dominated by Barnes-Hut and Triangle. The
honest public reading is the distribution above.

## Supplemental Semantic Notes

Hausdorff exact nearest-witness:
V2.14 does not expose an RT-core exact nearest-witness route. Its RT-core
Hausdorff path is the threshold-decision route. V3 and V4 do expose exact
nearest-witness; current V4 exact hot is `0.005547s` versus V3 exact hot
`0.006413s`, or `1.156x`. This is a V3/V4 exact capability comparison, not a
same-primitive V2/V3/V4 row.

Barnes-Hut:
The large V4/V2.14 win is a host-frontier bottleneck removal preserved from the
V3/Phoenix device-continuation direction and packaged into V4. Because V4/V3 is
near parity, public wording must not describe it as a new V4-only speedup.
RT-BarnesHut paper-reproduction wording remains outside the V4.0.0 public
claim; this benchmark row is not a public claim that RTDL fully reproduces the
paper implementation.

Spatial RayJoin:
The previous smoke-scale overlay row has been replaced in the runner by
generated grid64 shape-pair data. The result is serious parity, not a speed win.

## V4-Only Workflow Row

The V4 custom predicate early-exit workflow is not part of the legacy 10-app
matrix. It is the clearest V4-specific eDSL/operator-pushdown workflow win:

| Workflow | V4/V2.14 | V4/V3.0.2 | Current reading |
| --- | ---: | ---: | --- |
| Custom predicate early-exit | `4.633x` | `4.633x` | RTDL evaluates a constrained Numba predicate inside the OptiX any-hit path and owns the early-exit action, avoiding all-hit materialization. |

## Allowed Wording

Use:

```text
RTDL V4.0.0 is a published Python eDSL/operator-pushdown release and V2/V3
superset. On the current NVIDIA RT-core 10-app matrix, all apps have V2.14,
V3.0.2, and V4.0 rows; V4.0 has two material hot-path rows over
V2.14 and similar-speed control rows elsewhere. Separate V4 operator surfaces and the
custom predicate early-exit workflow show additional bounded V4 value.
```

Do not use:

```text
All benchmark apps are faster in V4.
```

Do not use:

```text
V4 is broadly faster than V2.14 or V3 across every app.
```

## Evidence Path

The first-time user path is the table above plus the runnable examples. Compact
machine-readable evidence is retained with the release files for maintainers who
need to reproduce the numbers.
