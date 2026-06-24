# Call For Review: Phoenix V3 Step 2 RayJoin Point-Location Runner Focused POD A/B

Date: 2026-06-22

Requested verdict label: one of the bounded Phoenix V3 protocol labels. This request does not authorize release.

## Review Packet

Please review the focused RayJoin productized-runner A/B:

- Report: `docs/reports/phoenix_v3_step2_rayjoin_point_location_runner_pod_ab_2026-06-22.md`
- Evidence summary: `docs/rebuild/v3/evidence/phoenix_v3_rayjoin_point_location_runner_pod_ab_20260622_175115/summary.json`
- Raw sample directory: `docs/rebuild/v3/evidence/phoenix_v3_rayjoin_point_location_runner_pod_ab_20260622_175115/`
- Runner script: `scripts/v3_phoenix_rayjoin_point_location_runner_pod_ab.py`
- Productized helper: `src/rtdsl/prepared_execution.py`
- App adapter: `examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`

## Facts To Review

- Dataset: `data/rayjoin_public_cdb/br_county.cdb`
- Hardware: same RT pod, NVIDIA RTX 4000 Ada Generation
- Contract: `point_to_shape_positive_hit_count_relation_status_corrected_executor_validated`
- Point order: `y_then_x`
- Repeat / warmup / samples: `50` / `5` / `7`
- Row count: `47262`
- Runner vs legacy OptiX median per-call speedup: `0.9734650006717721x`
- Runner vs legacy OptiX median total-repeat speedup: `0.9737541084926657x`
- Runner runtime trunk executes all samples: `true`
- Runner internal device residency all samples: `true`
- Runner hot-path host materialization any sample: `false`
- Material Set-A candidate: `false`
- Release authorized: `false`
- Broad V3-over-V2 claim authorized: `false`
- Full all-app rerun authorized by this packet: `false`

## Questions

1. Is the no-go interpretation correct: structural Step-2 evidence, but no material performance credit?
2. Is the incumbent comparison basis correct: runner vs current OptiX relation-status executor, not runner vs Embree?
3. Should RayJoin point-location topology stream be stopped as a material Set-A candidate in this wrapper form?
4. Does this evidence show that merely wrapping an already prepared executor in the productized runner is insufficient as a V3 performance source?
5. What should be the next Step-2 family: Barnes-Hut frontier/vector accumulation, a deeper RayJoin multi-phase topology pipeline, or another Set-A candidate?
6. Is any all-app pod run authorized now? My position: no.
7. What concrete return items are required before Phoenix V3 can move from `redo_required` toward release consideration?

## Explicit Non-Authorization

This packet authorizes no release, no public speedup claim, no broad V3-over-V2.x claim, no true-zero-copy wording, no V4/embedding work, and no all-app benchmark run.
