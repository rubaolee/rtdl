# Phoenix V3 Serious V2.x Paired Run Status

Date: 2026-06-22
Status: `analysis_complete_release_blocked_with_focused_runtime_fix`

## Current Decision

Phoenix V3 remains `redo_required`. The scoped 13-row surface is internal
evidence only; it is not a major-version release. The active blocker is broad,
material V2.x performance superiority across serious benchmark-app stress
tests.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

## Local Gate State

Latest full local matrix:

```text
docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_serious_paired_conclusion_sync_20260622.json
106 modules / 509 tests OK
```

Latest strict release check:

```text
docs/rebuild/v3/evidence/phoenix_v3_strict_release_after_serious_analysis_coverage_gate_20260622.stdout.log
expected exit: 1
meaning: release remains blocked
```

The serious paired analyzer now requires:

```text
expected_promoted_app_count: 10
missing_promoted_apps: []
primary_metric_source_mismatch_count: 0
overall_geomean_v3_speedup_vs_v2: >= 1.20x for release consideration
app_geomean_speedup_vs_v2: at least 8 of 10 apps > 1.05x
app_regression_floor: no app geomean < 0.95x without accepted explanation
OptiX-vs-Embree rows include ratio-change interpretation
```

Completed analyzer result:

```text
docs/rebuild/v3/phoenix_v3_serious_v2x_paired_benchmark_2026-06-22.md
docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100/summary.json
same_metric_comparison_count: 52
V3 faster by >5%: 12
Within +/-5%: 35
V3 slower by >5%: 5
Geomean V3 speedup vs V2.14: 1.012x
expected_promoted_app_count: 10
actual_promoted_app_count: 10
missing_promoted_apps: []
primary_metric_source_mismatch_count: 0
actual_app_geomean_wins_gt_1_05x: 1
actual_app_geomean_regressions_lt_0_95x: 2
release_consideration_eligible: false
```

Conclusion: the serious run completed cleanly but failed the preregistered V3
major-release performance bar. V3 remains `redo_required`; the next work is
generic runtime-contract redesign, not repeating the same benchmark run.

Focused runtime follow-up:

```text
docs/reports/phoenix_v3_barnes_hut_symbol_cache_focused_evidence_2026-06-22.md
scope: Barnes-Hut generic prepared OptiX fixed-radius threshold hot path
result: largest OptiX losses recovered from 0.622x/0.591x to 0.999x/1.038x
release_authorized: false
```

Additional focused runtime follow-ups:

```text
docs/reports/phoenix_v3_librts_aabb_count_cache_focused_evidence_2026-06-22.md
scope: LibRTS generic Embree AABB_INDEX_QUERY_2D count hot path
result: Embree count-only regression recovered; OptiX AABB row remains unstable/inconclusive
release_authorized: false

docs/reports/phoenix_v3_rtnn_neighbor_symbol_cache_focused_evidence_2026-06-22.md
scope: RTNN generic prepared Embree/OptiX fixed-radius 3-D neighbor symbol-cache hygiene
result: tests pass, but 12-row RTNN focused geomean is 1.001x; no material release-performance gain
release_authorized: false

docs/reports/phoenix_v3_fixed_radius_symbol_cache_focused_evidence_2026-06-22.md
scope: generic Embree/OptiX prepared fixed-radius count-threshold symbol/library cache
result: 17-row focused geomean is 1.062x; useful runtime cleanup concentrated in Hausdorff XHD OptiX rows, not release proof
release_authorized: false

docs/reports/phoenix_v3_fixed_radius_graph_self_query_refresh_focused_evidence_2026-06-22.md
scope: grouped-stream core-flag refresh uses prepared self-query device-search columns
result: contract/device-residency metadata improved; 3-row CuPy A/B geomean is 0.998x, no material speedup
release_authorized: false
```

## Active Pod Run

```text
run_id: phoenix_v3_serious_v2x_paired_20260622_074100
pod: root@213.173.108.14 -p 11592
key: C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
remote_base: /root/rtdl_v3_rebuild_20260620
remote_run_dir: /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_serious_v2x_paired_20260622_074100
hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.05, 20475 MiB
```

Suites:

```text
goal2626_large: --scale large --case-repeat 3 --timeout-sec 2400
goal2636_stress: --tier stress --case-repeat 3 --timeout-sec 3600
goal3828_full: full current benchmark scale profile runability/status evidence
```

Last observed live state:

```text
2026-06-22T13:28:31+00:00
completed suites:
  v2_14 goal2626_large, rc=0, 2026-06-22T07:40:55+00:00 to 2026-06-22T10:19:58+00:00
  v2_14 goal2636_stress, rc=0, 2026-06-22T10:19:58+00:00 to 2026-06-22T10:33:38+00:00
  v2_14 goal3828_full, rc=0, 2026-06-22T10:33:38+00:00 to 2026-06-22T10:34:24+00:00
  current goal2626_large, rc=0, 2026-06-22T10:34:24+00:00 to 2026-06-22T13:13:42+00:00
  current goal2636_stress, rc=0, 2026-06-22T13:13:42+00:00 to 2026-06-22T13:26:41+00:00
  current goal3828_full, rc=0, 2026-06-22T13:26:41+00:00 to 2026-06-22T13:27:23+00:00
active suite: none
active case: none
active child: none
active suite elapsed: complete
completed long same-case Embree children:
  PID 786678 completed after at least 24:52 elapsed
  PID 787204 completed after at least 24:49 elapsed
  PID 787709 completed after at least 25:04 elapsed
completed long same-case OptiX children:
  PID 788214 completed after at least 24:58 elapsed
  PID 788715 completed after at least 24:51 elapsed
  PID 789261 completed after at least 24:42 elapsed
cpu sample: no benchmark process active
memory sample: no benchmark process active
gpu sample: 0% util, 2 MiB, 13.98 W
status.tsv: all six suites complete rc=0
current_goal2626_large artifact directory: copied back and hash-verified
current goal2636_stress completed cases observed in log:
  hausdorff_embree_threshold_copies_16384
  hausdorff_optix_threshold_copies_16384
  hausdorff_embree_threshold_copies_65536
  hausdorff_optix_threshold_copies_65536
  hausdorff_embree_threshold_copies_262144
  hausdorff_optix_threshold_copies_262144
  hausdorff_optix_exact_grouped_seeded_pruned_points_32768
  hausdorff_optix_exact_grouped_seeded_pruned_points_131072
  rayjoin_embree_pip_tiled_x2048
  rayjoin_optix_promoted_pip_tiled_x2048
  rayjoin_embree_lsi_tiled_x2048
  rayjoin_optix_promoted_lsi_tiled_x2048
  rayjoin_embree_overlay_seed_tiled_x2048
  rayjoin_optix_promoted_overlay_seed_tiled_x2048
  rtnn_embree_uniform_65536_ranked_summary
  rtnn_optix_uniform_65536_ranked_summary
  rtnn_embree_clustered_65536_ranked_summary
  rtnn_optix_clustered_65536_ranked_summary
  rtnn_embree_shell_65536_ranked_summary
  rtnn_optix_shell_65536_ranked_summary
  rtnn_embree_uniform_262144_ranked_summary
  rtnn_optix_uniform_262144_ranked_summary
  rtnn_embree_clustered_262144_ranked_summary
  rtnn_optix_clustered_262144_ranked_summary
  rtnn_embree_shell_262144_ranked_summary
  rtnn_optix_shell_262144_ranked_summary
  barnes_hut_embree_node_coverage_bodies_32768
  barnes_hut_optix_node_coverage_bodies_32768
  barnes_hut_embree_node_coverage_bodies_131072
  barnes_hut_optix_node_coverage_bodies_131072
  triangle_counting_embree_rt_graph_2a1_cliques_20000
  triangle_counting_optix_rt_graph_2a1_cliques_20000
  triangle_counting_embree_rt_graph_2a1_cliques_80000
  triangle_counting_optix_rt_graph_2a1_cliques_80000
current goal3828_full cases observed in log:
  hausdorff_xhd_scale_default_optix_threshold
  spatial_rayjoin_public_cdb_representative_mixed_route_scale_default
  rt_dbscan_optix_numba_scale_default_65536_no_validation
  robot_collision_optix_scale_default_1024_no_probe_reference
  contact_manifold_optix_scale_default_grid64
  raydb_style_optix_count_scale_default_262k
  barnes_hut_numba_scale_default_8192
  librts_spatial_index_optix_scale_default_32768
  rtnn_prepared_optix_scale_default_65536
  triangle_counting_optix_rt_graph_2a1_scale_default_2048
```

Copied local artifacts:

```text
docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100/v2_14_goal2626_large/summary.json
docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100/v2_14_goal2636_stress/summary.json
docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100/v2_14_goal3828_full/*.stdout.json
docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100/current_goal2626_large/summary.json
docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100/current_goal2626_large/summary.md
docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100/current_goal2636_stress/summary.json
docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100/current_goal2636_stress/summary.md
docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100/current_goal3828_full/*.stdout.json
docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100/current_goal3828_full/*.stderr.txt
docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100/current_goal3828_full.json
docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100/status.tsv
docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100/main.log
```

`current_goal2626_large` copy-back was revalidated after a truncated `scp`
attempt:

```text
summary.json 4366360 f5b285ebb14bc85a57fcf3cc6d19edd228bf8793d96c080450cb12db47371516
summary.md 5529 322af5d89885cb7909b92ce083dfb34319da1b0b3323ba77632fb2163c906a74
remaining_analysis_artifacts.tgz d1843aac162859c817194ba00746ef6d9f22334f063bc27540af4d210c99da88
status.tsv 456 405b0422c74f65765f1171d030f49ddf23d7f94397155c186f2654b5c11cf22b
main.log 315738 bbeb5a9191e722d397dac34fbae46faea50c100191059741b5de751dec0421d2
current_goal2636_stress/summary.json 1334509 a894cafe005fc2521e6e3229fc62ade966248ce987dc3954429f69279e2e3eac
current_goal2636_stress/summary.md 8053 5146aa3176c1973632586d268df7af25a56b3e42e5ff6ffb4fe9e9994211dc24
current_goal3828_full.json 149906 506f43277ae869ef8261c8b308c96ef200d3bd873f6fdc0ba96921b162d98acc
current_goal3828_full file count: 20
```

Diagnostic correction from the completed V2.14 `goal2626_large` suite:

- The active Robot Collision command does not pass
  `--lowering-mode numpy_arrays` or `--skip-group-metadata`, so the app default
  is `python_objects` lowering.
- `/proc` and `ps -L` sampling showed one Python thread at ~100% CPU and no
  meaningful GPU activity during this child.
- The completed V2.14 `goal2626_large` summary confirms this was not OptiX
  traversal slowness for Robot Collision: `probe_reference_sec` was about
  1495 seconds, while OptiX `tail_phase_traversal_sec` was about 0.00025 sec
  and OptiX `tail_total_run_sec` was about 0.00854 sec.
- V2.14 Robot Collision `goal2626_large` shows OptiX 8.482x faster than Embree
  on the same prepared flags contract. The slow wall time is therefore a
  benchmark validation/probe-reference cost to account for, not an OptiX
  performance loss.

## Decision Audit

Decision: keep the serious paired run alive and do not launch a competing heavy
benchmark process.

1. Was I foolish? No for this decision.
2. If yes, what actions made the decision foolish? The foolish path would be
   launching overlapping heavy benchmark jobs and contaminating timing.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: kill the run and switch to smaller tests, but that would not satisfy
   the user's serious all-app evidence requirement.
4. Can I now try a different path that actually solves the problem? Yes: let
   the serious run finish, copy artifacts back, run the strict paired analyzer,
   and keep V3 blocked unless it clears the pre-registered bar.

Decision: preserve the pre-registered same-contract paired suite even though
Robot Collision has a newer `optix_prepared_device_count` front door that may
be a better current V3 runtime contract than the active
`optix_prepared_device_buffers` flags row.

1. Was I foolish? No for this decision.
2. If yes, what actions made the decision foolish? The foolish action would be
   changing the active benchmark contract mid-run to chase a better-looking
   result.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: stop the run and relaunch around the count-only route, but that would
   no longer answer the pre-registered V2.14-vs-current same-contract question.
4. Can I now try a different path that actually solves the problem? Yes: finish
   the current same-contract run first; if Robot flags-row evidence is weak,
   record it honestly and only then propose a separate reviewed count-contract
   rerun.

Decision: continue the slow current `robot_collision_embree_prepared_buffers`
row instead of killing it or changing benchmark parameters mid-run.

1. Was I foolish? No for this decision.
2. If yes, what actions made the decision foolish? The foolish action would be
   editing the active benchmark when a row becomes embarrassing or expensive.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: terminate and rerun a smaller or newer Robot route, but that would stop
   answering the paired V2.14-vs-current same-contract question.
4. Can I now try a different path that actually solves the problem? Yes: let the
   row finish or timeout, record the result, then decide from evidence whether
   the V3 runtime contract needs redesign or a separately reviewed route update.

Decision: continue the slow current `robot_collision_optix_prepared_device_buffers`
row even though code inspection shows the active command uses the legacy
default `python_objects` lowering and CPU probe-reference validation.

1. Was I foolish? No for this decision.
2. If yes, what actions made the decision foolish? The foolish action would be
   terminating or changing the active row because it exposes an uncomfortable
   V3 path cost.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: relaunch Robot Collision with `--no-probe-reference` and a cleaner
   lowering policy, but doing that inside this run would no longer answer the
   same-contract V2.14-vs-current question.
4. Can I now try a different path that actually solves the problem? Yes: let
   the paired evidence finish, classify this row honestly, and only then create
   a separate reviewed V3 runtime-contract fix if the evidence shows the old
   path is not user-responsible.

Decision: continue `current goal2636_stress` after `current goal2626_large`
finished and was copied back, rather than launching any separate high-load
benchmark or changing the stress suite while Spatial RayJoin is active.

1. Was I foolish? No for this decision.
2. If yes, what actions made the decision foolish? The foolish action would be
   starting another benchmark on the same GPU/CPU while claiming paired timing
   evidence from the active run.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: pause the serious run and chase isolated app wins, but that would
   repeat the earlier failure mode of scattered evidence instead of answering
   the major-version question.
4. Can I now try a different path that actually solves the problem? Yes: finish
   the full V2.14/current paired run, copy the remaining artifacts, run the
   pre-registered analyzer, and let the result either block V3 or identify the
   exact generic runtime contracts that must be rebuilt.

Decision: accept the completed serious paired analyzer result as a V3 release
blocker because the run finished cleanly but produced only 1.012x overall
geomean, one app geomean above 1.05x, and two app geomeans below 0.95x.

1. Was I foolish? No for this decision; it corrects the earlier foolish pattern
   of turning scoped or row-local evidence into a major-release conclusion.
2. If yes, what actions made the decision foolish? The foolish action now would
   be calling 1.012x a major performance win or rerunning the same suite until
   it looks better.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: classify this as a failed release bar immediately and stop spending pod
   time on repeated identical measurement.
4. Can I now try a different path that actually solves the problem? Yes: use
   the failure map to choose generic runtime-contract rebuild work, especially
   rows where V3 lost app geomean or OptiX relative margin, and require a new
   serious paired pass only after the runtime changes.
