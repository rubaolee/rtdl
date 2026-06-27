# Phoenix V3 M22 All-App POD Result

Status: `completed_protocol_failed_not_release`

This report records the single authorized same-RT-hardware all-app comparison
between V2.14 and Phoenix V3. It is evidence for engineering decisions, not a
release authorization document.

```text
run_id: phoenix_v3_m22_all_app_paired_finalrestart_20260623_060315
remote_run_dir: /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m22_all_app_paired_finalrestart_20260623_060315
local_evidence_dir: docs/rebuild/v3/evidence/phoenix_v3_m22_all_app_paired_finalrestart_20260623_060315
paired_summary_json: docs/rebuild/v3/evidence/phoenix_v3_m22_all_app_paired_finalrestart_20260623_060315/summary.json
paired_summary_md: docs/rebuild/v3/evidence/phoenix_v3_m22_all_app_paired_finalrestart_20260623_060315/summary.md
m21_protocol_gate_json: docs/rebuild/v3/evidence/phoenix_v3_m22_all_app_paired_finalrestart_20260623_060315/m21_protocol_gate.json
m21_protocol_gate_md: docs/rebuild/v3/evidence/phoenix_v3_m22_all_app_paired_finalrestart_20260623_060315/m21_protocol_gate.md
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

## Authorization Boundary

```text
valid_completed_all_app_runs_before_start: 0
authorized_valid_all_app_runs_remaining_before_start: 1
invalid_attempts_excluded_from_evidence: 2
release_authorized_by_m21_or_m22: false
public_claim_authorized_by_m21_or_m22: false
```

## Preflight Evidence

The final restarted run passed the fail-closed preflight before benchmark entry:

```text
python_preflight_expected=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
python_preflight_actual=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
gpu_preflight_name=NVIDIA RTX 4000 Ada Generation
gpu_preflight_driver=550.127.05
gpu_preflight_compute_capability=8.9
required_import_preflight_cupy=14.1.1
required_import_preflight_numba=0.65.1
child_interpreter_preflight_current_goal2626_child=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
child_interpreter_preflight_current_goal3828_child=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
child_interpreter_preflight_v2_14_goal2626_child=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
child_interpreter_preflight_v2_14_goal3828_child=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
```

## POD Run Completion

All suite drivers exited with `rc=0`, and the remote runner wrote `exit_code=0`.
The complete run lasted about 5h46m UTC, from 2026-06-23T06:03:22+00:00 to
2026-06-23T11:49:57+00:00.

| Version | Suite | RC | Start UTC | End UTC |
| --- | --- | ---: | --- | --- |
| V2.14 | `goal2626_large` | 0 | 2026-06-23T06:03:22 | 2026-06-23T08:41:58 |
| V2.14 | `goal2636_stress` | 0 | 2026-06-23T08:41:58 | 2026-06-23T08:56:08 |
| V2.14 | `goal3828_full` | 0 | 2026-06-23T08:56:08 | 2026-06-23T08:56:59 |
| Phoenix V3 | `goal2626_large` | 0 | 2026-06-23T08:56:59 | 2026-06-23T11:36:00 |
| Phoenix V3 | `goal2636_stress` | 0 | 2026-06-23T11:36:00 | 2026-06-23T11:49:11 |
| Phoenix V3 | `goal3828_full` | 0 | 2026-06-23T11:49:11 | 2026-06-23T11:49:57 |

Important: `rc=0` only means the suite drivers completed. The M21 gate still
fails because row-level benchmark failures were found inside completed suites.

## Paired Analyzer Result

```text
same_metric_comparison_count: 51
primary_metric_source_mismatch_count: 0
overall_geomean_v3_speedup_vs_v2_14: 1.049x
v3_rows_faster_by_more_than_5_percent: 16
rows_within_plus_minus_5_percent: 31
v3_rows_slower_by_more_than_5_percent: 4
release_consideration_eligible: false
```

The preregistered broad-performance bar was not met:

| Bar | Required | Actual | Result |
| --- | ---: | ---: | --- |
| Overall geomean V3/V2.14 | >= 1.20x | 1.049x | fail |
| App geomeans > 1.05x | >= 8 of 10 | 4 of 10 | fail |
| Severe app geomean regressions | none below 0.95x | 1 app | fail |
| Promoted app coverage | 10 apps | 10 apps | pass |

App-level geomeans:

| App | V3 speedup vs V2.14 | Interpretation |
| --- | ---: | --- |
| `librts_spatial_index` | 1.827x | strong app-level win |
| `contact_manifold` | 1.421x | strong app-level win |
| `hausdorff_xhd` | 1.134x | moderate app-level win |
| `spatial_rayjoin` | 1.068x | small app-level win |
| `robot_collision` | 1.027x | near parity |
| `rtnn` | 1.003x | near parity |
| `rt_dbscan` | 1.002x | near parity |
| `triangle_counting` | 0.987x | near parity / slight loss |
| `raydb_style` | 0.986x | near parity / slight loss |
| `barnes_hut` | 0.831x | severe regression |

Strong individual-row wins exist, but they do not add up to a broad V3 language
performance claim. The strongest wins include `librts_embree_aabb_index`
at 4.156x, `contact_manifold_optix_aabb_broadphase_collect_k` at 1.776x,
`hausdorff_optix_exact_grouped_seeded_pruned_points_131072` at 1.299x,
`rayjoin_embree_pip_tiled_x2048` at 1.265x, and
`hausdorff_optix_exact_grouped_seeded_pruned_points_32768` at 1.221x.

The strongest losses define immediate engineering blockers: Barnes-Hut OptiX
node coverage at 0.577x and 0.598x, LibRTS OptiX AABB index at 0.803x, and
RayDB Embree sum at 0.922x.

## M21 Protocol Gate

The M21 gate returned `protocol_fail_invalid_or_out_of_scope`.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_run_authorized_after_result: false
post_run_interpretation: run is invalid/out-of-scope for performance claims
```

Documented protocol values:

| Metric | Value |
| --- | ---: |
| Overall geomean V3 vs V2.14 | 1.049x |
| Set-A geomean V3 vs V2.14 | 1.013x |
| Set-A apps over 1.05x | 2 |
| Set-B geomean V3 vs V2.14 | 1.210x |
| Same-metric rows | 51 |

Protocol failures:

| Bar | Actual | Threshold |
| --- | ---: | ---: |
| `barnes_hut_app_geomean_floor` | 0.831x | 0.900x |
| `new_app_level_severe_regression_floor` | 0.831x | 0.900x |

Watch alert:

| Row | Actual | Threshold | Policy |
| --- | ---: | ---: | --- |
| `goal2626_large|librts_spatial_index|aabb_index_all_count_only|optix|librts_optix_aabb_index` | 0.803x | 0.950x | flag and report without rationalization |

## Row-Level Correctness Failures

These failures are the reason the completed suite run is still invalid for
public performance claims.

| Suite | App | Case | Backend | Return code | Last error line |
| --- | --- | --- | --- | ---: | --- |
| `v2_14_goal2626_large` | `spatial_rayjoin` | `spatial_rayjoin_optix_prepared_full_route` | `optix` | 1 | `RuntimeError: OptiX error: Invalid value` |
| `v2_14_goal2626_large` | `triangle_counting` | `triangle_counting_optix_rt_graph_2a1_partner` | `optix` | 1 | `RuntimeError: CUDA error during launching 3-D ray-column pack kernel: the provided PTX was compiled with an unsupported toolchain` |
| `v2_14_goal2636_stress` | `triangle_counting` | `triangle_counting_optix_rt_graph_2a1_cliques_20000` | `optix` | 1 | `RuntimeError: CUDA error during launching 3-D ray-column pack kernel: the provided PTX was compiled with an unsupported toolchain` |
| `v2_14_goal2636_stress` | `triangle_counting` | `triangle_counting_optix_rt_graph_2a1_cliques_80000` | `optix` | 1 | `RuntimeError: CUDA error during launching 3-D ray-column pack kernel: the provided PTX was compiled with an unsupported toolchain` |
| `current_goal2636_stress` | `spatial_rayjoin` | `rayjoin_optix_promoted_overlay_seed_tiled_x2048` | `optix` | 1 | `TypeError: run_rayjoin_prepared_optix_shape_pair_active_count_workload() got an unexpected keyword argument 'point_order_mode'` |

## OptiX / Embree Interpretation

The run answers the user's OptiX-vs-Embree concern more cleanly than earlier toy
rows: OptiX is often dramatically faster than Embree for RT-shaped work, but not
uniformly and not automatically. For example, RT-DBSCAN and RayDB count remain
hundreds to thousands of times faster on OptiX than Embree in the paired rows.
However, LibRTS AABB indexing is a counterexample where OptiX is slower than
Embree in both V2.14 and Phoenix V3, and Phoenix V3 made that row worse.

Robot collision also needs careful interpretation. The timed OptiX tail is fast,
but the run spends a large amount of wall time in CPU-side probe/reference work.
That is why GPU monitoring can look idle for long periods. This is not a proof
that OptiX is useless; it is proof that the metric must separate reference/probe
setup from the RTDL timed tail before any public claim is made.

## Engineering Conclusion

Phoenix V3 is not ready as a performance-major release under the M21/M22 bar.
The serious POD result is better than the earlier 1.012x indication, but 1.049x
overall geomean is still not a major-version performance result. The Set-A
residency/multi-phase family is nearly flat at 1.013x, which means the main
runtime trunk is not yet compounding across workloads. Set-B looks better at
1.210x, but Set-B is less representative of the intended Phoenix V3 runtime
breakthrough.

The right next step is not another all-app run. The next work must be focused:

1. Fix row-level correctness failures so the benchmark surface is valid.
2. Investigate and repair the Barnes-Hut regression, especially OptiX node
   coverage.
3. Treat LibRTS OptiX AABB index as a watch-row blocker.
4. Build or prove the shared V3 execution/residency trunk on at least two Set-A
   families before spending another all-app POD cycle.
5. Rerun focused Set-A probes first; only repeat all-app after those probes show
   runtime-sourced gains.

## 2-AI Consensus State

Claude review is recorded. The shared verdict is
`approve_blocked_not_release`.

```text
claude_review_request: docs/reviews/call_for_review_phoenix_v3_m22_all_app_result_facts_only_2026-06-23.md
claude_raw_review: docs/reviews/claude_phoenix_v3_m22_all_app_result_review_2026-06-23.raw.md
codex_claude_consensus: docs/reviews/codex_claude_phoenix_v3_m22_all_app_result_2ai_consensus_2026-06-23.md
consensus_verdict: approve_blocked_not_release
release_authorized_by_consensus: false
public_speedup_claim_authorized_by_consensus: false
```

Claude agrees that the run is serious engineering evidence but not a release.
Claude additionally ranks the current Phoenix V3 RayJoin OptiX `point_order_mode`
defect as the first fix priority because a V3 code defect can invalidate nearby
timing interpretation.

## Goal-Level Decision Audit

1. Was I foolish?

No for accepting this gate result. It would be foolish to treat a completed
suite driver as sufficient when the row-level correctness gate and performance
bar both fail.

2. If yes, what actions made the decision foolish?

No new foolish action is recorded for this decision. The earlier foolish pattern
was relying on broad prose and partial success signals; this report rejects that
pattern by writing the failures plainly.

3. Was there another path?

Yes. I could have emphasized the strongest individual wins and minimized the
failed rows. That path would be misleading because it would hide the Set-A flat
result and the Barnes-Hut regression.

4. Can I now try a different path?

Yes. The different path is to stop all-app spending temporarily, fix correctness
and the shared Set-A runtime blockers, then rerun focused probes before another
all-app comparison.
