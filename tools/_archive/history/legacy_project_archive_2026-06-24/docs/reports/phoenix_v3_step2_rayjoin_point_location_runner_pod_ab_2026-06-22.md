# Phoenix V3 Step 2: RayJoin Point-Location Runner Focused POD A/B

Date: 2026-06-22

Status: `step2_rayjoin_runner_executes_but_not_material_not_release`

Evidence:
`docs/rebuild/v3/evidence/phoenix_v3_rayjoin_point_location_runner_pod_ab_20260622_175115/summary.json`

## Why This Was Run

Phoenix V3 is being rebuilt around one rule: a V3 optimization only counts if it flows through the productized prepared-execution runtime trunk. RTDBSCAN Step 1 proved the trunk could execute, but did not show a material runtime-sourced gain. This RayJoin run tests a second Set-A family, point-location topology stream, against the correct incumbent: the current OptiX relation-status corrected executor.

This is not a toy run and not an Embree comparison. It uses the serious public CDB county dataset and compares runner vs legacy OptiX on the same row contract; in short, this packet is runner vs the incumbent OptiX route, not against Embree.

## Test Setup

| Field | Value |
| --- | --- |
| Dataset | `data/rayjoin_public_cdb/br_county.cdb` |
| Workload | PIP positive-hit count |
| Output contract | `point_to_shape_positive_hit_count_relation_status_corrected_executor_validated` |
| Point order | `y_then_x` |
| Repeat / warmup / samples | `50` / `5` / `7` |
| Row count | `47262` |
| Hardware | NVIDIA RTX 4000 Ada Generation, driver `550.127.05` |
| Runner route | `runner_point_location_topology_stream_prepared_execution` |
| Legacy route | `legacy_optix_relation_status_corrected_executor` |

## Results

| Metric | Legacy OptiX | Productized Runner | Legacy / Runner |
| --- | ---: | ---: | ---: |
| Median hot query per call | `0.001079664s` | `0.001109093s` | `0.973465x` |
| Median total repeat window | `0.054044224s` | `0.055500895s` | `0.973754x` |
| Median process wall control | `1.684360646s` | `2.120879337s` | `0.794180x` |

Checks passed:

- Same sample count, same row count, same output contract, same point order.
- Runner used `prepared_execution_session_runner` on every runner sample.
- Runner reported `runtime_trunk_executes_end_to_end = true` on every runner sample.
- Runner reported internal device residency on every runner sample.
- Runner reported no hot-path host materialization.
- Claim flags stayed false: no release, no public speedup, no broad V3-over-V2, no true zero-copy, no all-app rerun.

## Interpretation

This is a structural success and a performance no-go.

The productized runner does execute a second Set-A family end to end, but it does not improve the hot route. It is slightly slower than the incumbent OptiX relation-status route: `0.973754x` on the total-repeat metric. Therefore RayJoin point-location topology stream is not a material Set-A candidate for Phoenix V3.

The likely reason is now clear: this runner path wraps the same reusable native relation-status scalar-count executor that the legacy route already uses. It improves product shape and accounting, but it does not remove a dominant phase, fuse an additional continuation, or reduce traversal/refinement work. That is exactly the failure pattern the redesign warned about: a trunk-shaped wrapper without a new physical performance source will show residency and still land near parity.

## Decision Audit

1. Was I foolish?
   No. This run followed the redesign order: focused Set-A probe, same contract, same hardware, no all-app run, no Embree inflation.

2. If yes, what actions made the decision foolish?
   Not applicable for the run itself. The foolish action would be to count this as a V3 win because the runner executes, or to compare against Embree and hide the incumbent OptiX route.

3. Was there another path?
   Yes. We could have skipped RayJoin because the G1 audit already warned the current hot route had removed much host materialization. But RayJoin was still a reasonable Step-2 probe because it exercises a different productized runner family and verifies whether topology-stream residency compounds.

4. Can I now try a different path that actually solves the problem?
   Yes. Stop treating this RayJoin point-location wrapper as a material-performance route. The next Step-2 candidate must be a family where the runtime changes physical work across phases, not merely the accounting wrapper around an already prepared executor.

## Next Work

Do not run all-app yet.

For Phoenix V3 Step 2, either:

- choose a genuinely multi-phase family where the runner removes repeated materialization or repeated planning across phases, such as Barnes-Hut frontier/vector accumulation, or
- redesign RayJoin around a real multi-phase topology pipeline rather than this PIP scalar-count wrapper.

The release gate remains `redo_required`. This packet does not authorize V3 release wording or broad performance claims.
