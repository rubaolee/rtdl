# NVIDIA RT-Core Work-In-Progress Report

Date: 2026-04-23

Repository: `/Users/rl2025/rtdl_python_only`

Branch: `codex/rtx-cloud-run-2026-04-22`

Current head when written: `34f21ae0873bf45678dc0a4659f30481463f3b9b`

## Purpose

This report summarizes the current NVIDIA RTX / OptiX / RT-core app-promotion
work for independent review. It is a work-in-progress report, not a release
authorization and not a public speedup claim.

The project goal is to make RTDL apps honestly use NVIDIA RT cores where that
is technically true: the dominant RTDL operation should use OptiX traversal
over an acceleration structure on RTX-class hardware, with correctness and
phase-clean timing evidence. A CLI flag such as `--backend optix` is not by
itself an RT-core acceleration claim.

## Current Decision State

The current NVIDIA work is in local-first mode:

- Do local implementation, local tests, docs, manifests, dry-runs, and review
  packets before using paid cloud GPUs.
- Run cloud only as one consolidated batch, not one pod restart per app.
- Preserve all cloud artifacts and replay logs.
- Treat every app claim as bounded by the exact measured sub-path.
- Require 2-AI consensus for goals finished since the last Claude availability
  window. Claude was quota-blocked in the most recent attempts, so current
  consensus evidence uses Codex + Gemini 2.5 Flash where applicable.

## Claim Rule

Allowed internal wording today:

Selected prepared RTDL OptiX paths build and run on real RTX-class hardware,
with preserved phase artifacts. The strongest prepared scalar paths have very
small warm native query phases on RTX 4090.

Disallowed public wording today:

RTDL apps broadly beat existing systems on RTX hardware, RTDL is a SQL/DBMS
replacement, or every OptiX app path is NVIDIA RT-core accelerated.

## Cloud Evidence So Far

The RTX cloud work produced successful one-shot benchmark evidence on multiple
RTX-class GPUs. These runs are not all apples-to-apples because the code path
changed during optimization.

| GPU | Source report | Commit / state | Outcome |
| --- | --- | --- | --- |
| RTX A5000 | `/Users/rl2025/rtdl_python_only/docs/reports/goal765_rtx_a5000_cloud_benchmark_results_2026-04-23.md` | `e74c54e89e3548627b69b24a73d36870b7b6d08e` | OptiX 9.0 headers corrected; bootstrap passed; 5/5 manifest entries ran. |
| RTX 3090 | `/Users/rl2025/rtdl_python_only/docs/reports/goal772_rtx3090_one_shot_benchmark_results_2026-04-23.md` | `cb752c09bef24338321ddea3787c5bc877da1566` | One-shot runner completed; artifact failure count 0. |
| RTX 4090 | `/Users/rl2025/rtdl_python_only/docs/reports/goal776_rtx4090_one_shot_benchmark_results_2026-04-23.md` | `9a1edc1570e810f733752e06ae3fb39614c1aac1` | Goal773 scalar fixed-radius ABI validated after Goal775 build fix; artifact failure count 0. |
| RTX 4090 follow-up | `/Users/rl2025/rtdl_python_only/docs/reports/goal795_rtx4090_preserved_evidence_interpretation_2026-04-23.md` | `259c0c2dcdda373c8003cf3409a387ab61c5f407` | Preserved final RTX-only evidence with bounded interpretation. |

Representative preserved timings from the final RTX 4090 interpretation:

| App path | Prepared / pack phase | Warm native query median | Result mode | Correct interpretation |
| --- | ---: | ---: | --- | --- |
| Database analytics, sales risk | prepare total `0.257902s` | `0.090205s` | prepared query | Prepared OptiX DB-session phase evidence, not SQL superiority. |
| Database analytics, regional dashboard | prepare total `0.329046s` | `0.145297s` | prepared query | Prepared OptiX DB-session phase evidence, not DBMS claim. |
| Outlier detection | pack `0.138852s`, prepare `0.593074s` | `0.000409s` | `threshold_count` | Native prepared scalar fixed-radius summary only. |
| DBSCAN clustering | pack `0.121584s`, prepare `0.002743s` | `0.000405s` | `threshold_count` | Native prepared core-count summary only; Python clustering is separate. |
| Robot collision screening | pose-index prepare `0.000523s` | `0.000179s` | `pose_count` | Native prepared scalar pose-count traversal only. |

## Active RT-Core Candidate Apps

These are the current strongest NVIDIA candidates. They still require careful
review before public claims.

| App | Current RT-core status | Evidence level | Current allowed claim |
| --- | --- | --- | --- |
| `examples/rtdl_robot_collision_screening_app.py` | `rt_core_ready` for prepared scalar pose-count sub-path | Real OptiX ray/triangle any-hit traversal; RTX 4090 preserved phase evidence. | Prepared ray/triangle any-hit scalar pose-count sub-path may enter claim review; no full robot-planning or continuous-collision claim. |
| `examples/rtdl_outlier_detection_app.py` | `rt_core_ready` for prepared scalar threshold-count sub-path | Prepared fixed-radius threshold traversal; RTX 4090 preserved phase evidence. | Prepared fixed-radius scalar threshold-count sub-path may enter claim review; no broad anomaly-system claim. |
| `examples/rtdl_dbscan_clustering_app.py` | `rt_core_ready` for prepared core-threshold summary | Prepared fixed-radius core-count traversal; RTX 4090 preserved phase evidence. | Core-threshold summary may enter claim review; no full DBSCAN clustering acceleration claim. |
| `examples/rtdl_database_analytics_app.py` | `rt_core_partial_ready` | Real OptiX DB BVH candidate discovery and native exact filtering/grouping, but interface/materialization phases still matter. | Correctness-capable OptiX prepared DB path only; no broad DB speedup claim. |

## Deferred Candidate Apps

These have plausible RT-core routes but are not active claim paths today.

| App | Current class | Reason for deferral | Next local requirement |
| --- | --- | --- | --- |
| `examples/rtdl_service_coverage_gaps.py` | `optix_traversal_prepared_summary` | Prepared summary surface exists, but RTX phase-clean evidence is not yet reviewed. | Run the Goal811 phase profiler in the next batched cloud session only after local readiness. |
| `examples/rtdl_event_hotspot_screening.py` | `optix_traversal_prepared_summary` | Same as service coverage: prepared summary exists, claim needs phase-clean RTX artifacts. | Include as deferred entries only when intentionally requested with `--include-deferred`. |
| `examples/rtdl_segment_polygon_hitcount.py` | default `host_indexed_fallback`; explicit native mode exists | Native OptiX hit-count mode needs strict native-vs-host-indexed/PostGIS gate on RTX. | Use Goal807/Goal831 artifact contract before promotion. |
| `examples/rtdl_segment_polygon_anyhit_rows.py` | default `host_indexed_fallback` | Compact native hit-count is easier than pair-row native output; pair-row output is not native yet. | Promote compact counts/flags first; native pair-row emitter later. |
| `examples/rtdl_road_hazard_screening.py` | default `host_indexed_fallback` | Depends on segment/polygon core. | Do not claim road-hazard RTX speedup until segment/polygon native gate passes. |

Goal831 specifically prepared the deferred segment/polygon native OptiX gate for
future single-session RTX validation. It added a machine-readable
`cloud_claim_contract` to Goal807 artifacts and taught Goal762 to parse
`segment_polygon_hitcount` artifacts. It did not promote segment/polygon into
the active RTX manifest.

Goal831 files:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal831_segment_polygon_native_artifact_contract_2026-04-23.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal831_two_ai_consensus_2026-04-23.md`

## Non-Claim / Redesign Apps

These apps may still be useful RTDL apps, but they are not NVIDIA RT-core
claim paths today.

| App | Current class | Reason |
| --- | --- | --- |
| `examples/rtdl_graph_analytics_app.py` | `host_indexed_fallback` | Current OptiX-facing graph paths are host-indexed correctness paths, not native OptiX traversal. |
| `examples/rtdl_hausdorff_distance_app.py` | `cuda_through_optix` | Uses CUDA-style KNN rows through the OptiX backend library; useful GPU compute, not RT-core traversal. |
| `examples/rtdl_ann_candidate_app.py` | `cuda_through_optix` | Same issue: candidate search/ranking is not a true OptiX traversal claim. |
| `examples/rtdl_barnes_hut_force_app.py` | `cuda_through_optix` | Candidate generation uses GPU compute and Python force/opening-rule reduction dominates. |
| `examples/rtdl_facility_knn_assignment.py` | `not_optix_exposed` | Public app does not expose OptiX; true nearest/ranking primitive is not implemented. |
| `examples/rtdl_polygon_pair_overlap_area_rows.py` | `not_optix_exposed` | Public app does not expose OptiX. |
| `examples/rtdl_polygon_set_jaccard.py` | `not_optix_exposed` | Public app does not expose OptiX. |
| `examples/rtdl_apple_rt_demo_app.py` | `not_optix_applicable` | Apple-specific app; exclude from NVIDIA cloud batches. |
| `examples/rtdl_hiprt_ray_triangle_hitcount.py` | `not_optix_exposed` | HIPRT-specific app; exclude from NVIDIA OptiX claim tables. |

## Engineering Changes Completed In This NVIDIA Workstream

The recent NVIDIA RT-core workstream includes:

- machine-readable RTX benchmark manifest and runner infrastructure:
  `/Users/rl2025/rtdl_python_only/scripts/goal759_rtx_cloud_benchmark_manifest.py`
  and `/Users/rl2025/rtdl_python_only/scripts/goal761_rtx_cloud_run_all.py`;
- post-cloud artifact analysis:
  `/Users/rl2025/rtdl_python_only/scripts/goal762_rtx_cloud_artifact_report.py`;
- cloud bootstrap check:
  `/Users/rl2025/rtdl_python_only/scripts/goal763_rtx_cloud_bootstrap_check.py`;
- one-shot pod runner:
  `/Users/rl2025/rtdl_python_only/scripts/goal769_rtx_pod_one_shot.py`;
- packed ray input and prepared pose-index buffer for robot collision;
- scalar pose-count output for robot collision;
- packed-query reuse for fixed-radius summaries;
- native scalar threshold-count output for outlier/DBSCAN summaries;
- duplicate-command reuse in cloud runner to avoid paying twice for identical commands;
- local-first cloud-cost policy;
- DB phase accounting;
- app-output transparency for CUDA-through-OptiX apps;
- app maturity matrix and public docs boundaries;
- fail-closed cloud artifact contracts.

## Current Readiness Gate

The local pre-cloud readiness gate is:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 scripts/goal824_pre_cloud_rtx_readiness_gate.py \
  --output-json docs/reports/goal824_pre_cloud_rtx_readiness_gate_2026-04-23.json
```

The latest recorded gate result is `valid: true`. It is local readiness only;
it does not start cloud and does not authorize speedup claims.

The current gate counts in the preserved artifact are:

- active manifest entries: `5`;
- deferred manifest entries: `3`;
- excluded entries: `12`;
- public command audit: `252` commands;
- active runner dry-run: `5` entries, `4` unique commands;
- deferred runner dry-run: `8` entries, `7` unique commands.

## Cloud Run Policy

Use the single-session runbook:

- `/Users/rl2025/rtdl_python_only/docs/rtx_cloud_single_session_runbook.md`

Do not ask the user to restart/stop a cloud pod per app. The next cloud use
should happen only after local changes are ready and should run one batched
command. The standard command is:

```bash
cd /workspace/rtdl_python_only
PYTHONPATH=src:. python3 scripts/goal769_rtx_pod_one_shot.py \
  --branch codex/rtx-cloud-run-2026-04-22 \
  --optix-prefix /workspace/vendor/optix-dev-9.0.0 \
  --output-json docs/reports/goal769_rtx_pod_one_shot_summary_latest.json \
  --artifact-json docs/reports/goal762_rtx_cloud_artifact_report_latest.json \
  --artifact-md docs/reports/goal762_rtx_cloud_artifact_report_latest.md \
  --bundle-tgz docs/reports/goal769_rtx_pod_artifacts_latest.tgz
```

Use `--include-deferred` and `--only ...` only when intentionally collecting
deferred evidence in the same paid session.

## Consensus And Review Status

Goals826-831 are the latest completed goals after the user clarified that
finished goals since the last Claude availability window must have 2-AI
consensus.

| Scope | Consensus evidence | Decision |
| --- | --- | --- |
| Goals826-830 | `/Users/rl2025/rtdl_python_only/docs/reports/goal830_two_ai_consensus_2026-04-23.md` | Codex + Gemini 2.5 Flash ACCEPT; Claude quota-blocked, no Claude verdict claimed. |
| Goal831 | `/Users/rl2025/rtdl_python_only/docs/reports/goal831_two_ai_consensus_2026-04-23.md` | Codex + Gemini 2.5 Flash ACCEPT; Claude quota-blocked, no Claude verdict claimed. |

This WIP report itself has not yet been externally reviewed. The user intends
to send it manually to another reviewer.

## Known Risks / Open Problems

1. Public speedup claims still need explicit baselines. Current cloud evidence
   primarily proves selected prepared OptiX paths build/run on RTX and exposes
   phase timings.
2. Robot collision has strong scalar pose-count evidence, but full witness-row
   output and full robot-planning semantics are separate.
3. Outlier and DBSCAN have strong scalar threshold-count evidence, but default
   row paths and full clustering/postprocess are separate.
4. Database analytics has real OptiX work but remains partially interface and
   materialization dominated.
5. Graph, Hausdorff, ANN, Barnes-Hut, facility KNN, polygon overlap, and
   Jaccard need redesign before any NVIDIA RT-core claim.
6. Segment/polygon native mode is prepared for future strict gate collection,
   but it is not promoted yet.
7. Cloud evidence across A5000, RTX 3090, and RTX 4090 is not perfectly
   apples-to-apples because code changed during optimization.

## Requested Reviewer Checks

Please review for:

1. whether the current app classifications are honest;
2. whether the active RT-core candidate list is too broad or too narrow;
3. whether the cloud evidence is interpreted conservatively enough;
4. whether the segment/polygon deferred-gate handling avoids premature claims;
5. whether any public docs still imply `--backend optix` automatically means
   NVIDIA RT-core acceleration;
6. whether the next cloud batch should include only active entries, or active
   entries plus selected deferred service/hotspot and segment/polygon gates;
7. whether any goal since the last Claude availability window lacks required
   2-AI consensus.

## Current Recommended Next Step

Do not start a cloud pod immediately.

First, have this WIP report reviewed. If the reviewer accepts the claim
boundaries, continue local work on the next native-redesign or baseline tasks.
Only then run a single consolidated RTX cloud session.
