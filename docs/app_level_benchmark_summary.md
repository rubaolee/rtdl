# V4 App-Level Benchmark Summary

This page is the current public app-level performance boundary for V4.0.

## Current Decision

Goal4756 completed a serious NVIDIA RT-core POD matrix for the 10 promoted
benchmark apps:

- V2.14, V3.0.2, and V4.0 rows are present for every app.
- All 30 rows returned success and parseable JSON.
- Embree is not used as a primary denominator.
- The Spatial RayJoin row uses generated grid64 shape-pair input, not the old
  tiny overlay smoke input.
- The table has no `n/a` rows.

Decision label:

```text
complete_rt_core_app_matrix__bounded_material_wins__no_broad_all_app_speedup_claim
```

V4.0 is a Python eDSL/operator-pushdown release candidate and a V2/V3 superset.
The complete app matrix supports bounded claims: two material hot-path candidate
rows over V2.14, broad parity/control elsewhere, and no hot-path regressions in
the Goal4756 run. It does not authorize "all benchmark apps are faster" wording.

## Current 10-App RT-Core Rows

| App | V4/V2.14 hot | V4/V3.0.2 hot | Current reading |
| --- | ---: | ---: | --- |
| RTDBSCAN | `0.998x` | `0.993x` | Parity/control. |
| RayDB-style | `1.113x` | `1.111x` | Modest RT-core hot gain; below broad-app headline bar. |
| Triangle counting | `4.360x` | `1.021x` | Material hot-path candidate. |
| LibRTS spatial index | `0.999x` | `1.002x` | Parity/control. |
| Hausdorff XHD threshold route | `1.032x` | `0.983x` | Same-primitive threshold row is parity/control. |
| Robot collision | `1.020x` | `1.000x` | Parity/control; inherited OptiX primitive remains usable in V4. |
| Contact manifold | `1.116x` | `1.477x` | Parity/control/modest gain on the measured hot subpipeline. |
| RTNN | `1.029x` | `1.024x` | Parity/control. |
| Spatial RayJoin shape-pair | `1.000x` | `1.004x` | Serious generated-input parity/control. |
| Barnes-Hut aggregate frontier | `286.142x` | `0.993x` | Material V3/V4-over-V2.14 candidate; not a new V4-over-V3 speed claim. |

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

Supplemental RT-BarnesHut author-semantics route:
The newer native V4 RT-BarnesHut route is checksum-valid at 10M and wins on
comparable internal program time (`~7.513s` RTDL including input download
versus `10.4391s` author total program) with full phase accounting. This is
still not public paper-reproduction wording, not a no-copy tree-build claim,
and not a V2/V3/V4 public RT-BarnesHut speed table.

Spatial RayJoin:
The previous smoke-scale overlay row has been replaced in the runner by
generated grid64 shape-pair input. The result is serious parity, not a speed
win.

## V4-Only Workflow Row

The V4 custom predicate early-exit workflow is not part of the legacy 10-app
matrix. It is the clearest V4-specific eDSL/operator-pushdown workflow win:

| Workflow | V4/V2.14 | V4/V3.0.2 | Current reading |
| --- | ---: | ---: | --- |
| Custom predicate early-exit | `4.633x` | `4.633x` | RTDL evaluates a constrained Numba predicate inside the OptiX any-hit path and owns the early-exit action, avoiding all-hit materialization. |

## Allowed Wording

Use:

```text
RTDL V4.0 is a Python eDSL/operator-pushdown release candidate and V2/V3
superset. On the current NVIDIA RT-core 10-app matrix, all apps have V2.14,
V3.0.2, and V4.0 rows; V4.0 has two material hot-path candidate wins over
V2.14 and parity/control elsewhere. Separate V4 operator surfaces and the
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

## Evidence

- `future/v4/evidence/v4_goal4756_serious_all30_generated_spatial_2026-06-26/`
- `future/v4/evidence/v4_goal4756_final_rt_core_matrix_analysis_2026-06-26.json`
- `future/v4/v4_goal4756_final_rt_core_matrix_analysis_2026-06-26.md`
- `future/v4/v4_goal4756_final_rt_core_matrix_release_readout_2026-06-26.md`
- `future/v4/v4_goal4759_final_review_evidence_manifest_2026-06-26.md`
