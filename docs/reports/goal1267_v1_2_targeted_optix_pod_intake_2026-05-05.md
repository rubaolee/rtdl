# Goal1267 v1.2 Targeted OptiX Pod Intake

Date: 2026-05-05

Status: `EVIDENCE_READY_FOR_REVIEW`

## Scope

This is internal v1.2 evidence intake only. It does not authorize public wording,
release claims, or positive RTX speedup claims.

Active backends: Embree and OptiX.

Frozen backends before v2.1: Vulkan, HIPRT, Apple RT.

## Artifacts

- Primary pod artifact:
  `docs/reports/goal1267_live_pod_2026-05-05/goal1267_v1_2_optix_targeted_pod_results.tgz`
- Primary SHA256:
  `e3733c48c8401421993763ac0ef4e9ea4ff97df9f7834effa287e1c465f31355`
- Embree4 recovery artifact:
  `docs/reports/goal1267_embree4_recovery_live_pod_2026-05-05/goal1267_embree4_recovery.tgz`
- Embree4 recovery SHA256:
  `65c22860bd263f05b06622ff96fe9e4e90f5143d9c0cab4555abba639570e8fe`
- Source archive SHA256:
  `6527e311da2ee161dadf549ee524de736d9c28508f8701f6b5e5f4f21fd1e52a`

## Environment Finding

The first batch succeeded for OptiX rows but failed every Embree row because the
fresh Ubuntu pod installed `libembree-dev`, which provides Embree 3. Current
RTDL Embree native code requires Embree 4 headers and library:
`embree4/rtcore.h` and `libembree4`.

Recovery installed Embree 4.4.0 under `/opt`, set
`RTDL_EMBREE_PREFIX=/opt`, and reran only the nine failed Embree controls.
Recovery status: `failed_count: 0`.

## Result Summary

| Target | Scale | Embree timing | OptiX timing | Result |
| --- | ---: | ---: | ---: | --- |
| graph visibility | 30000 copies | 1.393945 s total | 1.619791 s total | OptiX still slower; scene prepare dominates |
| graph visibility | 60000 copies | 2.652469 s total | 1.414443 s total | OptiX faster at this scale, but dominated by scene prepare |
| polygon pair candidate discovery | 40000 copies | 6.724403 s | 4.976879 s | OptiX candidate discovery faster; candidate-count diagnostic still mismatched |
| polygon pair candidate discovery | 80000 copies | 13.833394 s | 8.924917 s | OptiX candidate discovery faster; candidate-count diagnostic still mismatched |
| polygon pair candidate discovery | 160000 copies | 25.111407 s | 17.258245 s | OptiX candidate discovery faster; candidate-count diagnostic still mismatched |
| DB sales_risk one-shot | 100000 rows | 4.009535 s | 4.832930 s | OptiX one-shot slower |
| DB sales_risk one-shot | 300000 rows | 12.053396 s | 10.360678 s | OptiX one-shot faster |
| DB sales_risk warm median | 100000 rows | 0.381175 s | 0.508756 s | OptiX warm query slower |
| DB sales_risk warm median | 300000 rows | 1.081152 s | 1.502239 s | OptiX warm query slower |
| Jaccard candidate discovery | 4096 copies, chunk 1024 | 0.746020 s | 2.107985 s | OptiX slower |
| Jaccard candidate discovery | 8192 copies, chunk 1024 | 1.119168 s | 2.865698 s | OptiX slower |

## Graph Finding

Graph visibility OptiX used the intended packed path:

- `all_numpy_packed_rays: true`
- `all_numpy_packed_triangles: true`
- 30000 copies: `query_anyhit_count_sec = 0.000195`, `scene_prepare_sec = 1.301361`
- 60000 copies: `query_anyhit_count_sec = 0.000239`, `scene_prepare_sec = 1.054774`

Interpretation: RT traversal itself is extremely fast. The total path is governed
by scene preparation and host-side packing/preparation, not by any-hit traversal.
For v1.2, graph improvement should focus on prepared-scene reuse or amortization,
not kernel micro-optimization.

## Polygon Pair Finding

OptiX candidate discovery is faster than Embree at all measured polygon-pair
scales, and summary parity is true. However,
`candidate_count_matches_expected` remains false because the OptiX profiler
reports fewer candidate rows than the expected-or-CPU diagnostic count while
still producing the same final summary.

Interpretation: this is useful internal performance evidence, but it remains
blocked for broad public wording until the candidate-count diagnostic is
reconciled or explicitly scoped out by review.

## DB Finding

The DB compact-summary shape preserved the no-row-materialization contract:
`row_materializing_operation_count = 0` for both Embree and OptiX.

OptiX improved one-shot total at 300000 rows, but the prepared warm-query median
remains slower than Embree at both scales. Since v1.2 priority is NVIDIA RT
performance, the next DB step should inspect native DB phase counters and reduce
OptiX warm-query overhead before considering any positive claim path.

## Jaccard Finding

Jaccard used the reviewed public-safe chunk size `1024` and summary parity was
true, but OptiX candidate discovery was slower than Embree at both measured
scales. The candidate-count diagnostic also remains false.

Interpretation: Jaccard should remain `optix_still_slower_with_reason` for v1.2
unless a new lowering or batching change reduces candidate-discovery overhead.

## Decision

Goal1267 gives usable v1.2 evidence. It does not close public wording. It does
identify the next engineering priorities:

- Graph: amortize or reuse OptiX scene preparation for repeated visibility
  batches.
- Polygon pair: fix or formally bound the candidate-count diagnostic while
  preserving the faster OptiX candidate-discovery path.
- DB: reduce OptiX prepared warm-query overhead; do not rely on one-shot 300k
  alone.
- Jaccard: keep safe-chunk correctness, but treat OptiX as slower until a
  different batching/lowering path is implemented.
