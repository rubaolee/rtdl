# V4 Closure Key Conversation Summary

Date: 2026-06-27

## Purpose

This document records the key conclusions from the V4 closure discussion. It is
intended to prevent future confusion between benchmark apps, paper-reproduction
apps, V2/V3 historical implementation origins, and the current V4 user-facing
programming model.

## 1. Two App Lines Are Now Explicit

RTDL has two separate app lines:

| Line | Purpose | Current members |
| --- | --- | --- |
| Traditional benchmark apps | The long-running 10-app RTDL benchmark suite for V2.14 / V3.0.2 / V4.0 comparison | RTDBSCAN, RayDB-style, Triangle counting, LibRTS spatial index, Hausdorff XHD, Robot collision, Contact manifold, RTNN, Spatial RayJoin, Barnes-Hut |
| Paper-reproduction apps | Independent author/paper-semantics apps for reproducing external programs | RT-BarnesHut, RayJoin |

These lines must not be merged silently. A benchmark-app row can inform system
development, but it does not automatically authorize paper-reproduction claims.

## 2. Paper-Reproduction Suite Status

| Paper-reproduction app | Main current version origin | Current status |
| --- | --- | --- |
| RT-BarnesHut | V4 | V4 has a checksum-valid native RT-core author-semantics route at 10M, with Author-vs-V4 phase/timing evidence. |
| RayJoin | V2.x / V2.14-era assets | RayJoin has a bounded / partial-exact paper-facing suite from the V2.x period, including same-query-stream and authors-code comparison assets. It is not the same as the current V4 Spatial RayJoin benchmark row. |

Important boundaries:

- Benchmark Barnes-Hut is not the same as RT-BarnesHut paper reproduction.
- Benchmark Spatial RayJoin is not the same as RayJoin paper reproduction.
- RT-BarnesHut currently has Author-vs-V4 same-contract evidence.
- RayJoin paper-reproduction assets exist historically, but full unrestricted
  public exact reproduction claims remain claim-limited.

Reference classification:

- `future/v4/v4_rayjoin_benchmark_vs_paper_reproduction_classification_2026-06-27.md`
- `future/v4/v4_goal4772_rt_barneshut_four_way_fair_compare_2026-06-26.md`

## 3. Traditional Benchmark App Matrix Final Result

Goal4756 completed the serious NVIDIA RT-core POD matrix:

- 10 promoted benchmark apps;
- 30/30 rows present for V2.14, V3.0.2, and V4.0;
- no `n/a` rows;
- primary denominator is NVIDIA OptiX/RT-core, not Embree;
- broad "all apps are faster" wording is not authorized.

Current table:

| App | V3/V2.14 hot | V4/V2.14 hot | V4/V3.0.2 hot | Reading |
| --- | ---: | ---: | ---: | --- |
| RTDBSCAN | `1.005x` | `0.998x` | `0.993x` | parity/control |
| RayDB-style | `1.001x` | `1.113x` | `1.111x` | modest gain |
| Triangle counting | `4.273x` | `4.360x` | `1.021x` | material hot-path win |
| LibRTS spatial index | `0.997x` | `0.999x` | `1.002x` | parity/control |
| Hausdorff XHD threshold | `1.050x` | `1.032x` | `0.983x` | parity/control |
| Robot collision | `1.020x` | `1.020x` | `1.000x` | parity/control |
| Contact manifold | `0.756x` | `1.116x` | `1.477x` | modest/subpipeline gain |
| RTNN | `1.006x` | `1.029x` | `1.024x` | parity/control |
| Spatial RayJoin shape-pair | `0.996x` | `1.000x` | `1.004x` | parity/control |
| Barnes-Hut aggregate frontier | `288.155x` | `286.142x` | `0.993x` | material V3/V4-over-V2 win |

The V4/V2.14 hot geomean is `2.10069x`, but it must not be used as a headline
because it is dominated by Triangle counting and Barnes-Hut.

Primary references:

- `docs/app_level_benchmark_summary.md`
- `future/v4/v4_goal4756_final_rt_core_matrix_analysis_2026-06-26.md`
- `future/v4/v4_goal4756_final_rt_core_matrix_release_readout_2026-06-26.md`

## 4. Why V4 Is Mostly Parity With V3

V4 is mostly `~1.0x` versus V3 because V4 is a V2/V3 superset and productized
front door, not a second complete rewrite of the V3 hot paths.

The major performance repairs already landed in V3/Phoenix-style routes:

- Barnes-Hut aggregate frontier already removed the V2.14 host-frontier
  bottleneck.
- Triangle counting already used the segmented generic RT / ray-triangle
  weighted any-hit summary route.

V4 preserves, packages, documents, and exposes these capabilities through a
cleaner current surface. It also adds operator/workflow surfaces and
paper-reproduction routes, but it does not claim broad V4-over-V3 speedup.

## 5. Why V3 Was Mostly Parity With V2.14 Except Two Rows

V3 did not become a universal execution graph / residency / continuation engine
across all 10 apps. Most apps continued to use the same underlying V2.14
OptiX/native primitive families.

The two major exceptions are real:

1. **Barnes-Hut aggregate frontier**
   - V2.14 materialized frontier rows on host and then continued outside the
     hot RT path.
   - V3 turned frontier into device-resident columns and connected
     continuation without the host-frontier bottleneck.
   - This produced the `~288x` V3/V2.14 hot-path win.

2. **Triangle counting**
   - V2.14 used a more old-style "find hits/candidates, then count" pipeline.
   - V3/V4 used segmented generic RT / ray-triangle weighted any-hit summary.
   - This reduced intermediate materialization and outer orchestration on the
     hot path, producing the `~4.27x` V3/V2.14 win.

These are genuine engine/dataflow wins, not app-name backdoors.

## 6. Triangle Counting Is Not A Backdoor

Triangle counting does not mean RTDL has an app-specific triangle-counting
kernel.

The valid interpretation is:

```text
Triangle counting fits a generic operator pattern:
ray/triangle traversal -> any-hit / weighted-hit summary -> grouped or segmented accumulation.
```

Allowed:

- generic ray-triangle weighted any-hit summary;
- generic grouped / segmented reduction;
- operator pushdown based on computation shape.

Not allowed:

- `if app == triangle_counting: run_special_kernel`;
- app-identity native kernels;
- public wording implying a hidden triangle-counting shortcut.

## 7. User-Facing Programming Model

The current V4 capability-release model should present one clean user surface:

```python
import rtdsl.v4 as rtdl_v4
```

From the user perspective:

| Version | User-facing interpretation |
| --- | --- |
| V2.14 | A collection of usable RT-core primitives and benchmark routes. Users often needed to understand route selection, partner choice, and host/device boundaries themselves. |
| V3 | Some multi-stage benchmark routes gained residency and continuation, reducing host materialization in important cases. |
| V4 | The current Python eDSL/operator-pushdown front door and V2/V3 superset. Users should learn V4, not V2/V3 history. |

The V4 contract:

```text
Python owns the application.
RTDL owns generic RT-shaped fused operators and prepared routes.
Users choose measured partners explicitly.
Unsupported custom logic fails closed or remains V4.1/Tier-3 work.
```

## 8. What Users Should Not Need To Know

For the public V4 capability release, users should not need to know:

- which route originated in V2.14;
- which performance repair came from V3/Phoenix;
- old V3/V4 process debates;
- review debt mechanics;
- internal goal numbers;
- historical false starts.

Those belong in evidence, review, or history directories. The user-facing front
door should be:

- `README.md`;
- `docs/current_v4_status.md`;
- `docs/app_level_benchmark_summary.md`;
- `tutorials/current/README.md`;
- `examples/v4/`;
- `future/v4/tier2_operator_catalog.md` for measured operator scope.

## 9. Allowed V4 Release Framing

Allowed:

```text
RTDL V4 is the current Python eDSL/operator-pushdown surface and V2/V3 superset.
The 10-app NVIDIA RT-core matrix is complete for V2.14, V3.0.2, and V4.0.
V4 has bounded material hot-path wins over V2.14 in Triangle counting and
Barnes-Hut, plus parity/control elsewhere. V4 also adds measured operator
surfaces, constrained predicate early-exit, and paper-reproduction app work.
```

Not allowed:

```text
All benchmark apps are faster in V4.
V4 is broadly faster than V3.
Triangle counting uses a hidden app-specific kernel.
Benchmark Barnes-Hut is the same as RT-BarnesHut paper reproduction.
Benchmark Spatial RayJoin is the same as RayJoin paper reproduction.
Arbitrary OptiX callbacks are supported in V4.0.
```

## 10. Immediate Closure Requirement

Before closing V4, ensure the release surface keeps this exact structure:

1. Traditional 10 benchmark apps remain the benchmark suite.
2. Paper-reproduction suite is separate and currently contains:
   - RT-BarnesHut;
   - RayJoin.
3. `rtdsl.v4` is the only current user-facing programming surface.
4. V2/V3 are compatibility/history/evidence layers, not user prerequisites.
5. Performance claims preserve denominator, route, and scope.
