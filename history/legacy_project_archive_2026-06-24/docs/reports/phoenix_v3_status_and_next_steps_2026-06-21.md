# Phoenix V3 Status And Next Steps - 2026-06-21

> Current supersession: read
> `docs/reports/phoenix_v3_current_status_after_post_p1_consensus_2026-06-21.md`
> for the current Phoenix V3 state. The older sections below are historical
> progress log entries and may contain superseded eleven-row or installer-scope
> facts.

## Latest Phoenix Queue Update - 2026-06-21 18:47 ET

Current working state remains V3-only. V4, C ABI, embedding, and external
zero-copy interop are out of scope.

New full-scale Spatial overlay active-count evidence has been integrated as a
no-go, not as a win:

- No-go packet:
  `docs/rebuild/v3/phoenix_v3_spatial_overlay_active_count_full_scale_no_go_2026-06-21.md`
- Source evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_spatial_overlay_full_active_count_20260621/full_overlay_repeat1_m3_failclosed.json`
- Scale: `15,700 x 7,774 = 122,051,800` shape pairs.
- OptiX timed median: `0.01629706472158432 s`.
- Embree timed median: `20.57024759799242 s`.
- Timed-median ratio: `1262.205676x`, explicitly rejected for promotion.
- Correctness blocker: OptiX active count `19,277` versus Embree active count
  `21,228`, delta `-1,951`.
- Repeat blocker: repeat=1 on both backends.
- Gate result: `spatial_overlay_active_count_full_scale_no_go`, with
  `m7_promotion_authorized: false`, `release_authorized: false`, and
  `public_speedup_claim_authorized: false`.

The next-engine queue now records this under
`spatial_rayjoin_topology_stream_author_gap` as future research:

- Queue packet:
  `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`
- Queue status: `generic_engine_work_queue_closed_not_release`.
- Active queue: empty.
- Pending external-review candidate: Barnes-Hut fused Numba CUDA partner row
  only, still `m7_rows_added_now: 0`.
- Release surface gate:
  `surface_breadth_blocked_not_release`.
- Release readiness gate:
  `blocked_not_release`.

Claude status:

- Local Claude binary is verified at
  `C:\Users\Lestat\.local\bin\claude.exe`, version `2.1.170 (Claude Code)`.
- Retry before reset returned:
  `You've hit your session limit - resets 7pm (America/New_York)`.
- Retry blocked record:
  `docs/reviews/claude_blocked_retry_phoenix_v3_barnes_hut_fused_partner_m7_candidate_2026-06-21.md`.
- Prepared review request for Spatial no-go:
  `docs/reviews/call_for_review_phoenix_v3_spatial_overlay_active_count_full_scale_no_go_2026-06-21.md`.

Latest verification:

- `py -3 -m unittest tests.v3_phoenix_next_engine_work_queue_test`: 6 tests OK.
- `py -3 -m unittest tests.v3_phoenix_release_surface_breadth_gate_test tests.v3_phoenix_release_readiness_gate_test`: 6 tests OK.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: 96 modules / 462 tests OK.

Goal-level decision audit:

1. Was I foolish? No for the queue decision. The full-scale Spatial result is
   treated as a correctness failure despite the huge speed ratio.
2. If yes, what actions made the decision foolish? The foolish path would have
   been to mine `1262.205676x` as a user-facing performance claim while hiding
   the `19,277 != 21,228` count mismatch and repeat=1 blocker.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: keep the result as a no-go and require a fresh exact-count packet before
   any M7 reconsideration.
4. Can I now try a different path that actually solves the problem? Yes: retry
   Claude after reset for the Barnes-Hut aggregate candidate and the Spatial
   no-go review, then update gates only if external review changes the evidence
   classification.

## Goal

Phoenix V3 is still active. The goal is to turn reusable M0-M149 generic
performance work into a user-responsible V3 surface: easy to learn, honest, and
backed by RTX/OptiX-vs-Embree evidence on serious rows. V4, C ABI, embedding,
and external zero-copy interop are out of this goal.

## High-Level Status Answer

We are building V3, not merely polishing individual benchmark apps. The current
Phoenix rule is that a row only matters for V3 if it demonstrates a reusable
engine capability: prepared execution, device-column ray-batch preparation,
candidate streaming, graph/chunk reuse, same-contract continuation, or
row-scoped validation discipline. App-specific native engines and one-off
route tricks stay internal.

The strongest current technical optimization is the grouped-reduction
`cupy_device_columns` prepare path. It is a V3 engine optimization because it
changes the generic input path from host-packed ray materialization to deferred
device-column preparation while keeping the same grouped_sum contract and CPU
reference parity. On the RTX pod it produced material, non-1.01x evidence:
`3.599x` and `73.586x` host-packed OptiX/device-column OptiX cold-plus-loop
speedups at the two tested serious sizes, with `100.019x` and `174.645x`
Embree/device-column OptiX same-contract context ratios.

This does not yet make V3 complete. The current release surface has eleven
M7-qualified row-scoped results after AABB, RTNN, Triangle, RTDBSCAN,
Hausdorff, Robot Collision, AABB candidate stream, and grouped-reduction rows
passed their evidence and review gates. The generic-engine active queue is now
closed, but that is not release authorization. Phoenix V3 is neither "already
done with tiny polish left" nor "just app development": it is a partially built
V3 language-level performance surface whose remaining blockers are release
authorization, surface breadth, installer/reproducibility, secondary RT
performance confirmation, and external release-readiness consensus.

## Current Position

- Current classification packet:
  `docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.json`
- Current app boundary map:
  `docs/rebuild/v3/v3_benchmark_app_classification_2026-06-20.json`
- Packet status: `m7_classification_packet_not_release`
- Current packet count:
  - M7-qualified release rows: 11
  - Route-map M7-qualified rows: 5
  - Supplemental M7-qualified rows: 6
  - Blocked/internal rows: 14
  - Release authorized: false
- Broad V3-over-V2 speedup claim: not authorized.
- Full V3 release: not authorized.
- Aggregate release-readiness gate:
  `scripts/v3_phoenix_release_readiness_gate.py --pretty` returns
  `status: blocked_not_release`; `--strict-release` exits nonzero on the
  current eleven-row evidence surface.
- Secondary-platform gate:
  `scripts/v3_phoenix_secondary_platform_gate.py --pretty` returns
  `status: compatibility_confirmed_rt_performance_not_confirmed`. `lx1` /
  `192.168.1.20` is accepted as compatibility evidence only; its recorded
  `NVIDIA GeForce GTX 1070` is not RT-core performance confirmation.
- Install/reproducibility gate:
  `scripts/v3_phoenix_install_reproducibility_gate.py --pretty` returns
  `status: staged_pod_gate_present_general_release_installer_not_ready`.
  `scripts/v3_install_gpu_pod_env.sh` is accepted only as a staged pod gate
  requiring `--accept-experimental-pod-gate`; it is not a general release
  installer and does not authorize package-install wording. The installer
  blocker is closed only under `release_scope:
  source_tree_pod_gated_eleven_row`, with
  `installer_closes_release_blocker_scope:
  source_tree_pod_gated_eleven_row`.
- Next generic-engine work queue:
  `scripts/v3_phoenix_next_engine_work_queue.py --pretty` returns
  `status: generic_engine_work_queue_closed_not_release`,
  `existing_evidence_promotable_now: false`, and an empty active queue.
  Grouped-reduction prepare amortization is closed for two exact device-column
  rows, AABB native prepared-query-handle reuse is closed for two exact
  jittered-grid range-intersection rows, and RTNN prepared repeat50 is closed
  for one exact 1,048,576-point prepared-session row after Claude external
  review plus Codex consensus. Barnes-Hut/vector accumulation and Spatial
  RayJoin topology-stream author-basis work are both retained as future
  research, not current Phoenix P0 work.
- Current Spatial RayJoin topology-stream status:
  `docs/rebuild/v3/phoenix_v3_spatial_active_p0_closure_gate_2026-06-21.md`
  records `spatial_active_p0_closed_current_v3_future_research` after Claude
  external review and Codex consensus. The exact-f64 repair is real internal
  progress: the serious RTX 4000 Ada packet has stable row count `47,262`, full
  M3 phase accounting, and current RTDL prepared-query median `6.309319 ms`.
  It is still not an M7 row or public Spatial win because the same-dataset
  RayJoin author Query median is `1.865660 ms`, about `3.382x` faster than
  RTDL, and the author count was not printed in that packet. The device-filtered
  probe remains rejected (`47,570 != 47,262`) and the relation-status corrected
  no-go remains rejected (`47,259 != 47,262`). Reopen requires a fresh
  same-dataset `br_county.cdb` POD packet with RTDL prepared-query median
  below `1.865660 ms` with stable margin, stable exact `47,262`, full M3
  table, same-packet author timing/count, or external acceptance of weaker
  scope plus Codex consensus.
- Current grouped-reduction prepare-amortization candidate:
  `docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_ray_batch_pod_evidence_2026-06-21.md`.
  POD evidence plus provisional 2-AI reopen consensus is complete:
  `pod_evidence_2ai_reopen_authorized_not_m7`.
- Current grouped-reduction device-column final M7 review packet:
  `docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.md`.
  Status:
  `grouped_reduction_device_column_m7_qualified_row_scoped`.
  This packet promotes two supplemental M7 rows, does not replace the current
  host-packed/scalar-broadcast M7 row, and does not authorize release or public
  broad speedup wording.
- Grouped-reduction device-column exact rows now M7-qualified:
  `grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups`
  and
  `grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups`.
  Accepted POD facts include host-packed/device-column OptiX cold-plus-loop
  speedups of `3.599x` and `73.586x`, device-route
  `host_packed_ray_count: 0`, CPU-reference parity, source-manifest
  provenance, and explicit acknowledgement that the raw evidence JSONs lack a
  git HEAD because the POD directory was not a git checkout.
- Current external-review tool status:
  Windows local Claude is verified at `C:\Users\Lestat\.local\bin\claude.exe`
  with version `2.1.170 (Claude Code)`. Future Claude reviews in this Windows
  repo should use that hard path directly. Older grouped-reduction
  Claude/Gemini blocked files remain historical evidence for that pass, not the
  current tool status.
- Current Claude+Codex release-readiness consensus:
  the old six-row factual state is superseded by the eleven-row surface and
  closed generic-engine queue, but release remains blocked. Claude's current
  verdict is `not-release-ready-fix-p0`, and Codex records
  `claude_codex_consensus_current_eleven_row_not_release_ready_fix_p0`.
  `docs/reviews/claude_phoenix_v3_eleven_row_release_readiness_review_2026-06-21.md`
  and
  `docs/reviews/codex_phoenix_v3_eleven_row_release_readiness_2ai_consensus_2026-06-21.md`

## Quick Checkpoint After Context Refresh

As of the latest context refresh, Phoenix V3 is in the M7-row consolidation
phase, not the final release phase.

- Active goal: promote only reusable, evidence-backed generic engine
  capabilities into V3; keep V4/C ABI/embedding/zero-copy interop out.
- Current approved row-scoped M7 count: 11.
- Current public release status: not authorized.
- Current broad V3-vs-V2 speedup status: not authorized.
- Current active queue items: none. AABB prepared query-handle reuse is closed
  as two exact row-scoped M7 rows after Claude/Codex review, RTNN prepared
  repeat50 is closed as one exact row-scoped M7 row after Claude/Codex review,
  and Spatial RayJoin topology-stream author/wording is closed to future
  research after Claude/Codex review.
  Barnes-Hut vector accumulation is also recorded as a future-research
  record, not an active Phoenix P0 build target, after alignment with M129/M131/M142.
  The closed M7 rows are exact row-scoped claims, not broad V3 release authorization.
- Triangle prepared graph review hygiene is now closed by Claude external
  refresh review:
  `docs/reviews/claude_phoenix_v3_triangle_prepared_graph_80000_m7_refresh_review_2026-06-21.md`.

The currently counted M7 rows are row-scoped only. They do not authorize a broad
"V3 is faster than V2" claim, whole-app claims, paper-reproduction claims, or
claims outside the exact tested row contract.

## What Is Already Strong

- Grouped reduction has a Claude+Codex reviewed row-scoped M7 packet.
- AABB candidate stream has a Claude+Codex reviewed row-scoped M7 packet.
- RTDBSCAN component-signature continuation has repeat=5 RTX evidence plus
  Claude+Codex review, and is M7 row-scoped only.
- Hausdorff threshold_summary now has exactly one row-scoped M7 row:
  `hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped`.
  Claude closed the P0 stability/oracle blockers after a five-sample independent
  paired process rerun. The approved wording says phase-total includes scene
  preparation.
- Robot Collision collision_flag_stream now has exactly one row-scoped M7 row:
  `collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped`.
  Claude approved the no-probe paired packet with P1 amendments; the final
  wording says the 5.086x tail and 5.075x window metrics are prepared query
  execution phase metrics, while 1.171x wrapper is the conservative
  process-level bound excluding only the CPU probe-reference oracle.
- Triangle prepared graph is counted in the current packet after Claude
  external refresh review found no P0 blockers and required only review-status
  hygiene amendments, now applied.
- Spatial RayJoin, RTNN, Contact Manifold, and M10 boundary reviews are now
  closed as no-promotion/internal-note outcomes; none of them add an M7 row.
- The app-level benchmark classification has been refreshed to
  `phoenix_boundary_classification_not_release`; it no longer uses live
  release-like labels for current rows.
- The setup/rerun runbook now defines a `Current Phoenix Rerun Contract` and
  points users to the Phoenix M7 row authority, app boundary map, GPU partner
  gate, wording gate, secondary-platform gate, and aggregate release-readiness
  gate.

Last recorded local verification in this session:

- `scripts/v3_release_wording_gate.py --pretty`: passed.
- `py -3 -m unittest tests.v3_phoenix_m7_row_classification_packet_test tests.v3_release_wording_gate_test tests.v3_rebuild_tutorial_surface_test`: passed.
- `py -3 scripts/run_test_matrix.py --group v3_rebuild`: 47 modules / 218 tests passed.

Latest verification after Hausdorff promotion:

- `py -3 scripts\v3_release_wording_gate.py --pretty`: passed.
- `py -3 -m unittest tests.v3_phoenix_m7_row_classification_packet_test tests.v3_release_wording_gate_test tests.v3_rebuild_tutorial_surface_test`: 25 tests passed.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: 47 modules / 218 tests passed.

## New Evidence Copied Back

Pod evidence copied back locally:

`docs/rebuild/v3/evidence/phoenix_v3_hausdorff_threshold_summary_repeat5_20260621/`

This is the Hausdorff threshold-summary same-contract rerun requested by the
current M7 reopen queue. It used repeat=5, warmup=1, RTX OptiX with
`--require-rt-core`, same threshold-summary contract, and oracle checks.

Results:

| copies | points per side | query OptiX/Embree | phase-total OptiX/Embree | wrapper OptiX/Embree |
| ---: | ---: | ---: | ---: | ---: |
| 16,384 | 65,536 | 1.891x | 0.583x | 1.147x |
| 65,536 | 262,144 | 1.831x | 0.995x | 1.378x |
| 262,144 | 1,048,576 | 1.685x | 1.264x | 1.588x |

Interpretation now:

- The query kernel evidence is strong across the tested sizes.
- End-to-end phase-total evidence is mixed: small is slower, middle is parity,
  largest is faster.
- The large row is now row-scoped M7 after the P0 repair and Claude/Codex
  review. Smaller rows remain blocked.

## Latest Verification

- `py -3 -m unittest tests.v3_phoenix_m10_same_stream_accounting_interpretation_test tests.v3_phoenix_contact_manifold_broadphase_boundary_test tests.v3_phoenix_rtnn_ranked_summary_wall_time_boundary_test tests.v3_rebuild_tutorial_surface_test tests.v3_release_wording_gate_test`: 29 tests passed.
- `py -3 scripts\v3_release_wording_gate.py --pretty`: passed with no missing required strings and no violations.
- `py -3 scripts\v3_phoenix_m7_row_classification_packet.py`: regenerated the classification packet with `final_review_blocked_packets: 0`, `m7_qualified_release_rows: 8`, and `release_authorized: false`.
- `py -3 -m unittest tests.v3_phoenix_m7_row_classification_packet_test tests.v3_phoenix_contact_manifold_broadphase_boundary_test tests.v3_release_wording_gate_test`: 17 tests passed.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: 47 modules / 218 tests passed.
- `py -3 -m unittest tests.v3_gpu_python_env_gate_script_test tests.v3_rebuild_tutorial_surface_test tests.v3_release_wording_gate_test tests.v3_rebuild_evidence_classification_test tests.v3_public_docs_rebuild_surface_test`: 30 tests passed after the runbook/classification cleanup.
- `py -3 scripts\v3_release_wording_gate.py --pretty`: passed after adding `v3_benchmark_app_classification_2026-06-20.json` to the scanned current surface.
- Current user-facing docs no longer use the old internal rescue/pass labels or
  release-like machine labels in the scanned Phoenix V3 surface.
- Final verification for this cleanup pass:
  `py -3 scripts\v3_release_wording_gate.py --pretty` passed, and
  `py -3 scripts\run_test_matrix.py --group v3_rebuild` passed
  47 modules / 219 tests.
- Aggregate readiness gate added after that cleanup:
  `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty` returns
  `blocked_not_release`; `py -3 scripts\v3_phoenix_release_readiness_gate.py
  --strict-release` exits 1; `py -3 -m unittest
  tests.v3_phoenix_release_readiness_gate_test` passed 3 tests.
- Latest post-gate verification:
  `py -3 -m unittest tests.v3_phoenix_release_readiness_gate_test
  tests.v3_release_wording_gate_test` passed 5 tests, and
  `py -3 scripts\run_test_matrix.py --group v3_rebuild` passed
  48 modules / 222 tests.
- Secondary-platform strategy gate added after that verification:
  `py -3 scripts\v3_phoenix_secondary_platform_gate.py --pretty` returns
  `compatibility_confirmed_rt_performance_not_confirmed`; `py -3
  scripts\v3_phoenix_release_readiness_gate.py --pretty` now includes
  `secondary_rt_performance_confirmation_not_closed`; `py -3 -m unittest
  tests.v3_phoenix_secondary_platform_gate_test
  tests.v3_phoenix_release_readiness_gate_test tests.v3_release_wording_gate_test`
  passed 8 tests.
- Latest full Phoenix rebuild verification after secondary-platform gate:
  `py -3 scripts\run_test_matrix.py --group v3_rebuild` passed
  49 modules / 225 tests.
- Install/reproducibility strategy gate added after that verification:
  `py -3 scripts\v3_phoenix_install_reproducibility_gate.py --pretty`
  returns `staged_pod_gate_present_general_release_installer_not_ready`.
  The gate reports `staged_gpu_pod_gate_available: true`,
  `release_scope: source_tree_pod_gated_eleven_row`,
  `general_release_installer_ready: false`,
  `package_install_claim_authorized: false`, and
  `installer_closes_release_blocker: true` under
  `installer_closes_release_blocker_scope:
  source_tree_pod_gated_eleven_row`.
- Latest full Phoenix rebuild verification after install/reproducibility gate:
  `py -3 -m unittest tests.v3_phoenix_install_reproducibility_gate_test
  tests.v3_phoenix_secondary_platform_gate_test
  tests.v3_phoenix_release_readiness_gate_test tests.v3_release_wording_gate_test`
  passed, and the later full matrix has continued to pass after subsequent
  M7-row consolidation work.
- Latest full Phoenix rebuild verification after Spatial exact-executor intake:
  `py -3 -m unittest tests.v3_phoenix_spatial_rayjoin_exact_executor_intake_test
  tests.v3_phoenix_next_engine_work_queue_test tests.v3_release_wording_gate_test`
  passed 13 tests; `py -3 scripts\v3_release_wording_gate.py --pretty`
  passed; `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`
  returned `blocked_not_release` with `failed_checks: []`; and
  `py -3 scripts\run_test_matrix.py --group v3_rebuild` passed
  66 modules / 315 tests.
- Latest Spatial relation-status corrected executor probe:
  public-county POD smoke with
  `--count-mode relation_status_corrected_executor_validated` failed closed at
  `47259 != 47262`; the no-go packet generated successfully with all checks
  true and no M7/release/public-speedup authorization.
- Next generic-engine work queue added after that verification:
  `py -3 scripts\v3_phoenix_next_engine_work_queue.py --pretty` returns
  `active_generic_engine_work_queue_not_release`; the aggregate readiness gate
  now includes `generic_engine_work_queue_open`; `py -3 -m unittest
  tests.v3_phoenix_next_engine_work_queue_test
  tests.v3_phoenix_release_readiness_gate_test tests.v3_release_wording_gate_test`
  passed 11 tests, and `py -3 scripts\run_test_matrix.py --group v3_rebuild`
  passed 51 modules / 235 tests.
- Grouped-reduction device-column candidate added after that verification:
  `py -3 scripts\v3_phoenix_grouped_reduction_device_column_candidate.py
  --pretty` returns
  `grouped_reduction_device_column_ray_batch_candidate_pending_pod_not_m7`.
  `py -3 -m unittest
  tests.v3_phoenix_grouped_reduction_device_column_candidate_test
  tests.v3_phoenix_next_engine_work_queue_test tests.v3_release_wording_gate_test
  tests.v3_phoenix_release_readiness_gate_test

  tests.goal2727_raydb_prepared_grouped_reduction_opponent_test
  tests.goal4425_v3_0_m28_raydb_prepared_grouped_refresh_test
  tests.goal671_optix_prepared_anyhit_count_test` passed 45 tests with 5
  environment skips. `py -3 scripts\v3_release_wording_gate.py --pretty`
  passed, and `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`
  remains `blocked_not_release`. `py -3 scripts\run_test_matrix.py --group
  v3_rebuild` passed 52 modules / 239 tests.
- Grouped-reduction device-column POD evidence and provisional 2-AI reopen
  consensus added after that verification:
  `py -3 -m unittest
  tests.v3_phoenix_grouped_reduction_device_column_pod_evidence_test` passed
  8 tests. `py -3 -m unittest tests.v3_phoenix_next_engine_work_queue_test
  tests.v3_release_wording_gate_test tests.v3_phoenix_release_readiness_gate_test
  tests.v3_phoenix_grouped_reduction_device_column_pod_evidence_test` passed
  19 tests. `py -3 scripts\v3_release_wording_gate.py --pretty` passed with no
  violations. `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`
  remains `blocked_not_release` with no failed checks. `py -3
  scripts\run_test_matrix.py --group v3_rebuild` passed 53 modules / 247 tests.
- Grouped-reduction device-column final review closure added after that
  verification:
  `py -3 scripts\v3_phoenix_grouped_reduction_device_column_m7_final_review_packet.py --pretty`
  now returns `grouped_reduction_device_column_m7_qualified_row_scoped`.
  The subagent review approved both rows with required wording fixes, and
  Codex recorded the 2-AI consensus. The M7 classification packet now counts
  eight row-scoped M7 rows, and the next generic-engine queue now has four
  open items.

Earlier same-session verification:

- `py -3 -m unittest tests.v3_phoenix_triangle_prepared_graph_80000_m7_final_review_packet_test tests.v3_phoenix_m7_row_classification_packet_test tests.v3_release_wording_gate_test tests.v3_public_docs_rebuild_surface_test tests.v3_rebuild_tutorial_surface_test`: 34 tests passed.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: 47 modules / 218 tests passed.
- `py -3 scripts\v3_release_wording_gate.py --pretty`: passed.

## Major Steps Remaining

1. Execute the remaining generic-engine work queue. Grouped-reduction prepare
   amortization is closed for two exact `cupy_device_columns` rows; current
   evidence has no further rows that can be honestly promoted as-is. New M7
   rows require engine changes or new focused evidence for ranked-summary wall
   path, reusable AABB lifetime, topology-stream overhead, or vector
   accumulation.
2. Fix or package the installer/reproducibility story so users can reproduce
   the GPU gate without project-history knowledge. The current runbook now names
   the rerun contract, but the installer is still a staged pod gate rather than
   a general release installer.
3. Decide whether an eight-row exact-claim surface is sufficient for an interim V3
   candidate, or continue generic-engine work until more capabilities have
   serious row-scoped evidence.
4. Execute the second-machine RT performance strategy. The `lx1` decision is
   now closed as compatibility-only because it is GTX 1070 hardware; remaining
   choices are another RTX/RT-core host, or explicit waiver with
   hardware-scoped wording and 2-AI review.
5. Strengthen the wording scanner from first-pass gate to final release gate.
6. Make the V3 product-scope decision: release as runability-first with eight
   exact performance rows, or continue engine work before calling it a major
   version.
7. Keep the aggregate release-readiness gate as the single machine-readable
   release control surface until the blockers above close.

## Current No-Go Lines

- No V4 work in this Phoenix V3 goal.
- No C ABI, embedding, V4 packaging, or external zero-copy interop in V3.
- No broad V3-over-V2 speedup claim from current evidence.
- No "OptiX is faster" claim without same-contract baseline, oracle/parity,
  RTX evidence, and row-scoped wording.
- No paper-reproduction or whole-application claim unless the exact evidence
  proves that exact statement.

## Goal-Level Decision Self-Audit

Decision: pause promotion, preserve the current state, copy back pod evidence,
and record next steps before continuing.

1. Was I foolish?
   No. This decision avoids acting from memory after compaction and avoids
   promoting mixed Hausdorff evidence too early.
2. If yes, what actions made the decision foolish?
   Not applicable for this decision. The foolish alternative would have been to
   promote Hausdorff from the query-only speedup while ignoring phase-total
   regression/parity rows.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: continue the benchmark queue silently. That would preserve momentum but
   would leave the user without a clear state ledger. The safer path is this
   status lock plus artifact copy-back.
4. Can I now try a different path that actually solves the problem?
   Yes. The next path is evidence-packet first, external review second,
   classification/docs/tests third. That directly serves Phoenix V3 release
   readiness instead of broad, unsupported claims.

## Goal-Level Decision Self-Audit - Final Readiness Consensus

Decision: do not declare V3 release-ready; record the then-current state as a
bounded six-row exact-claim surface after Claude+Codex review.

1. Was I foolish?
   No. This follows the evidence and avoids converting exact row claims
   into a major-release claim.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be claiming broad V3-over-V2 speed
   from a 1.012x geomean or calling row-scoped evidence whole-app evidence.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: keep promoting more generic-engine rows. Claude and Codex agreed that
   the six-row surface was not a major release; the later device-column closure
   raises the count to eight but does not close release infrastructure,
   second-machine strategy, wording scanner, and product scope.
4. Can I now try a different path that actually solves the problem?
   Yes. The next path is installer/reproducibility, external review cleanup,
   second-machine decision, stronger scanner, and final V3 product positioning.

## Goal-Level Decision Self-Audit - Aggregate Readiness Gate

Decision: add `scripts/v3_phoenix_release_readiness_gate.py` as the single
machine-readable Phoenix V3 release-readiness control surface.

1. Was I foolish?
   No. This directly prevents the previous failure mode: treating scattered
   row evidence, passing tests, or polished wording as release authorization.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to let row-scoped M7 rows
   imply a V3 major release or broad V3-over-V2 speedup.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: continue engine tuning first. That is still necessary, but without a
   gate the next strong row could be overclaimed again.
4. Can I now try a different path that actually solves the problem?
   Yes. Keep this gate active, then either close release blockers or expand
   generic M7 coverage before changing `release_authorized`.

## Goal-Level Decision Self-Audit - Secondary Platform Strategy

Decision: classify `lx1` / GTX 1070 as compatibility confirmation only, not
secondary RT performance evidence.

1. Was I foolish?
   No. This prevents non-RT hardware from being misread as RT-core performance
   confirmation.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be treating `lx1` passing tests,
   wording, source-tree doctor, or CUDA partner smoke gates as proof of
   RTX/OptiX performance portability.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: run a calibrated subset on `lx1` and call it a second-machine
   performance pass. That would confuse CUDA compatibility with RT-core
   evidence.
4. Can I now try a different path that actually solves the problem?
   Yes. Keep `lx1` as compatibility evidence and require another RTX-class
   host, or an explicit release waiver, before closing the performance blocker.

## Goal-Level Decision Self-Audit - Install Reproducibility Strategy

Decision: classify `scripts/v3_install_gpu_pod_env.sh` as a staged pod gate,
not a general release installer.

1. Was I foolish?
   No. This prevents a dependency-gated pod script from being promoted into a
   user-facing install promise.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be claiming package-install
   readiness because an experimental pod setup script exists.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: ignore the installer blocker and continue performance work. That would
   keep momentum but would leave users unable to reproduce the GPU gate
   responsibly.
4. Can I now try a different path that actually solves the problem?
   Yes. Keep the staged pod gate explicit, then either build reviewed general
   install docs/package instructions or scope V3 as source-tree/pod-gated with
   2-AI release wording.

## Goal-Level Decision Self-Audit - Next Generic Engine Queue

Decision: reopen Phoenix V3 work only through generic engine optimization
candidates, not app-specific promotion from old evidence.

1. Was I foolish?
   No. This keeps the empty next-M7 evidence queue from being misread as either
   release readiness or permission to promote app-specific rows.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be mining the old P0 matrix for
   impressive ratios while ignoring current blockers, wall timing, author
   baselines, or V2.14 parity.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: keep polishing docs or tune individual apps. That can look productive
   but would not prove a V3 language-level performance breakthrough.
4. Can I now try a different path that actually solves the problem?
   Yes. Use the queue to make the next work engine-level: RTNN
   ranked-summary wall path, reusable AABB lifetime/review closure, and
   Spatial topology-stream author-basis/wording closure. Barnes-Hut/vector
   accumulation is no longer an active Phoenix P0; it remains future research
   unless a reviewed hierarchical traversal design reopens it.

## Latest Verification - Device-Column Final Review Packet Hygiene

- `py -3 scripts\v3_phoenix_grouped_reduction_device_column_m7_final_review_packet.py --pretty`:
  regenerated the approved final-review packet with explicit `packet_path` and
  `packet_json_path` provenance.
- `py -3 -m unittest tests.v3_phoenix_grouped_reduction_device_column_m7_final_review_packet_test`:
  6 tests passed.
- `py -3 scripts\v3_release_wording_gate.py --pretty`: passed with no missing
  required files, no missing required strings, and no violations.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`: returned
  `status: blocked_not_release`, `failed_checks: []`, and the expected blockers
  remain active.
- `py -3 -m unittest tests.v3_phoenix_grouped_reduction_device_column_m7_final_review_packet_test tests.v3_release_wording_gate_test tests.v3_phoenix_next_engine_work_queue_test tests.v3_phoenix_release_readiness_gate_test`:
  17 tests passed.

## Latest Final Verification - Eight-Row Phoenix Surface

- `py -3 scripts\v3_release_wording_gate.py --pretty`: passed with no missing
  required scanned files, no missing required strings, and no violations.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: passed 54 modules /
  253 tests.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`: returned
  `status: blocked_not_release`, `failed_checks: []`,
  `m7_qualified_release_rows: 8`, and the active blockers:
  release authorization false, eight-row surface still too narrow, broad
  V3-faster-than-V2 claim not authorized, general release installer not ready,
  secondary RT performance confirmation not closed, generic engine queue open,
  and prior external release-readiness consensus blocking major-release
  wording.
- `py -3 scripts\v3_phoenix_next_engine_work_queue.py --pretty`: returned
  `active_generic_engine_work_queue_not_release` with three active P0 items:
  ranked-summary wall path, reusable AABB lifetime, and topology-stream overhead.
  Barnes-Hut vector accumulation is retained as
  `future_research_not_current_p0`, not as an active Phoenix P0 build target.
- `py -3 scripts\v3_phoenix_m7_row_classification_packet.py`: regenerated the
  M7 packet with `m7_qualified_release_rows: 8`,
  `row_scoped_public_claim_rows: 8`, `public_claim_rows: 0`, and
  `release_authorized: false`.

## Latest Verification - RTNN M112 Reconciliation And Queue Refresh

- `py -3 scripts\v3_phoenix_rtnn_m112_reconciliation_packet.py`: generated
  `rtnn_m112_reconciled_no_m7_promotion`, with
  `m7_qualified_release_rows: 0` and
  `existing_evidence_promotable_now: false`.
- RTNN is now recorded as real `ranked_summary` engine progress but not an M7
  row: the old M104-M112 line shows a strong large aggregate route, while M104
  still has a tie-sensitive kth checksum mismatch, M106 is
  `float32`/`exact=false`, and author/RTDL output contracts differ.
- `py -3 scripts\v3_phoenix_next_engine_work_queue.py --pretty --json-out
  docs\rebuild\v3\phoenix_v3_next_generic_engine_work_queue_2026-06-21.json
  --md-out docs\rebuild\v3\phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`:
  regenerated the queue with RTNN refined to two honest next paths: exact
  tie-stable aggregate review/repair, or focused float32 same-contract rerun.
- `py -3 -m unittest tests.v3_phoenix_rtnn_m112_reconciliation_test
  tests.v3_phoenix_next_engine_work_queue_test
  tests.v3_release_wording_gate_test`: 13 tests passed.
- `py -3 scripts\v3_release_wording_gate.py --pretty`: passed with no missing
  required scanned files, no missing required strings, and no violations.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`: returned
  `blocked_not_release`, `failed_checks: []`, and kept the same blockers:
  release authorization false, eight-row surface too narrow, broad
  V3-faster-than-V2 claim not authorized, general release installer not ready,
  secondary RT performance confirmation not closed, generic engine queue open,
  and external release-readiness consensus blocking major-release wording.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: passed
  55 modules / 258 tests.

## Latest Verification - AABB Prepare-Reuse Contract

- Contact broadphase now emits generic `prepared_session_residency` metadata
  for `aabb_index_query_2d`, with `prepare_aabb_index_2d` as the cold phase,
  `emit_aabb_intersection_pair_rows_2d` as the hot phase, explicit
  `get_or_prepare_explicit_session` reuse helper, and public speedup/device
  interop/automatic partner/app-specific native logic claims false.
- `py -3 scripts\v3_phoenix_aabb_prepare_reuse_contract.py --pretty`:
  generated `aabb_prepare_reuse_contract_candidate_not_m7`, with
  `m7_qualified_release_rows_added: 0`, prepared-session primitive
  `aabb_index_query_2d`, and current contact wall OptiX/Embree still
  `0.8029757821318222`.
- Claude reviewed the packet as `approve_with_amendments` with no P0 blockers.
  The two P1 amendments are now applied: future M7 evidence has a serious
  scale floor of at least 32,768 indexed AABBs and 32,768 query AABBs or
  reviewer-approved equivalent scale, and the packet says the current local
  smoke records contract visibility rather than observed prepared execution or
  performance proof.
- Codex consensus is recorded as
  `claude_codex_consensus_complete_queue_advancement_not_m7` in
  `docs/reviews/codex_phoenix_v3_aabb_prepare_reuse_contract_2ai_consensus_2026-06-21.md`.
- `scripts/v3_phoenix_aabb_prepare_reuse_pod_runner.py` is now the checked-in
  serious evidence entrypoint for this queue item. Its default RTX command uses
  `jittered_grid`, 32,768 indexed AABBs, 32,768 query AABBs, warmup 3,
  repeat 50, Embree+OptiX, and `--require-rt-hardware`. The runner records
  prepare/query/collect/wall phases and still keeps `m7_promotion_authorized:
  false` until a fresh RTX run and 2-AI review close.
- External review for the runner is not closed:
  `docs/reviews/external_ai_blocked_phoenix_v3_aabb_prepare_reuse_pod_runner_2026-06-21.md`
  records a Claude timeout and Gemini authentication/product-tier failure. This
  does not satisfy 2-AI consensus.
- `py -3 scripts\v3_phoenix_next_engine_work_queue.py --pretty --json-out
  docs\rebuild\v3\phoenix_v3_next_generic_engine_work_queue_2026-06-21.json
  --md-out docs\rebuild\v3\phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`:
  refreshed the queue with `contact_aabb_prepare_reuse` pointing to
  `phoenix_v3_aabb_prepare_reuse_contract_2026-06-21.md` and the AABB POD
  runner, while keeping the item open for repeated-session RTX evidence.
- `py -3 -m unittest tests.v3_phoenix_aabb_prepare_reuse_contract_test
  tests.v3_phoenix_aabb_prepare_reuse_pod_runner_test
  tests.v3_phoenix_next_engine_work_queue_test
  tests.v3_phoenix_contact_manifold_broadphase_boundary_test
  tests.v3_release_wording_gate_test`: 22 tests passed.
- `py -3 scripts\v3_release_wording_gate.py --pretty`: passed with no missing
  required scanned files, no missing required strings, and no violations.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`: returned
  `blocked_not_release`, `failed_checks: []`, and kept the same release
  blockers active.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: passed
  57 modules / 267 tests.

## Goal-Level Decision Self-Audit - V3 Versus App Work

Decision: continue Phoenix as a V3 generic engine project, and count only
material, reusable, externally reviewed performance rows toward V3.

1. Was I foolish?
   No. This decision prevents both failure modes: treating app-specific tuning
   as V3, and treating existing eight-row evidence as a finished major release.
2. If yes, what actions made the decision foolish?
   Not applicable for this decision. The foolish actions would be claiming a
   broad V3-over-V2 breakthrough from tiny ratios, or publishing impressive
   per-route numbers without proving they are reusable engine capabilities.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: declare the current eight M7 rows enough, or keep optimizing apps one by
   one. Both paths are faster administratively, but neither gives users a
   trustworthy V3 language-level performance surface.
4. Can I now try a different path that actually solves the problem?
   Yes. The immediate path is now the remaining generic queue:
   RTNN ranked-summary wall path, reusable AABB lifetime/review closure, and
   Spatial topology-stream author-basis/wording closure. Barnes-Hut/vector
   accumulation is a future-research record, not an active queue item.

## Latest Verification - Spatial RayJoin Topology-Stream Contract

- Added generic topology-stream phase accounting in
  `src/rtdsl/v3_0_topology_stream_accounting.py` and the generated contract
  packet
  `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_topology_stream_contract_2026-06-21.md`.
- The packet status is
  `spatial_rayjoin_topology_stream_contract_candidate_not_m7`; it adds
  `m7_qualified_release_rows_added: 0` and explicitly keeps release, public
  speedup, whole-app, paper-reproduction, and RTDL-beats-RayJoin wording false.
- The useful finding is a reusable engine bottleneck, not an app win:
  RTDL OptiX PIP wall has about 32.6% visible non-traversal overhead, while the
  RayJoin author RT timer remains 5.728x faster than RTDL OptiX wall. The next
  valid path is a full M3 phase table plus generic topology-stream overhead
  reduction.
- `scripts/v3_release_wording_gate.py` now scans the new topology-stream
  contract and requires the `not_m7`, `topology_stream_phase_accounting_v1`,
  `M7 rows added by this packet: 0`, full-M3, and "Do not invert the 5.728x"
  guardrails.
- `py -3 scripts\v3_release_wording_gate.py --pretty`: passed with no missing
  required scanned files, no missing required strings, and no violations.
- `py -3 -m unittest tests.v3_release_wording_gate_test
  tests.v3_phoenix_spatial_rayjoin_topology_stream_contract_test
  tests.v3_phoenix_next_engine_work_queue_test`: 14 tests passed.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`: returned
  `blocked_not_release`, `failed_checks: []`, `m7_qualified_release_rows: 8`,
  and kept the broad V3-over-V2 claim unauthorized.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: passed 58 modules /
  273 tests.

## Latest Verification - Spatial RayJoin M3 Gap Analysis

- Added
  `scripts/v3_phoenix_spatial_rayjoin_m3_gap_analysis.py` and generated
  `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_m3_gap_analysis_2026-06-21.md`.
- The packet status is `spatial_rayjoin_m3_gap_analysis_not_m7`; it adds no M7
  rows and keeps release, public speedup, whole-app, paper, RTDL-beats-RayJoin,
  true-zero-copy, and V4/embedding claims false.
- The useful V3 engine target is now explicit: old large-PIP evidence shows
  that keeping query point columns resident inside RTDL's prepared topology
  route moves OptiX hot wall from 273.922ms to 120.060ms (2.282x), with counts
  matching and visible residual after native transfer falling from 140.988ms to
  1.373ms.
- This does not authorize a public Spatial RayJoin row. The next legitimate
  engineering work is a reusable topology-stream prepared handle/runner that
  emits all M3 phases in one fresh packet and does not use RayJoin-specific
  native logic.
- `scripts/v3_release_wording_gate.py` now scans the M3 gap packet and requires
  the not-M7, true-zero-copy-false, device-resident-delta, and resident
  topology-stream guardrails.

## Current Phoenix V3 Boundary Answer

1. Are we building V3 instead of developing individual apps?
   Yes, that is the required direction. App rows are only probes. A row counts
   toward V3 only when it proves a reusable engine capability, is row-scoped,
   has serious evidence, and does not depend on app-specific native logic.
2. Are we making real technical optimization beyond v2.x?
   Partly. The current qualified rows show real work in prepared execution,
   scalar-broadcast grouping, device-column grouping, AABB candidate streams,
   component-signature continuation, prepared graph chunks, threshold summaries,
   and collision flag streams. But the aggregate release gate still says the
   surface is too narrow for a responsible major release.
3. Are the gains material rather than 1.01x wording tricks?
   For promoted rows, yes: the gate excludes tiny, ambiguous, or broad claims.
   It also keeps low-ratio rows such as early RTDBSCAN same-contract evidence
   out until the exact row is defensible. For unpromoted rows like Spatial
   RayJoin, the report names the negative gap instead of selling it.
4. Does final V3 depend on current work, or was it already basically done?
   Final V3 still depends on current work. The earlier M0-M149 body contains
   the core ideas and many implementations, but Phoenix is the process that
   converts them into a user-responsible V3: narrowed contracts, serious RTX
   evidence, M7 row qualification, release wording gates, and rejection of
   misleading app-level claims.

## Goal-Level Decision Self-Audit - Spatial Topology-Stream

Decision: keep Spatial RayJoin as a topology-stream accounting and optimization
queue item, not an M7 success row.

1. Was I foolish?
   No. This avoids repeating the earlier mistake of turning impressive-looking
   partial numbers into a V3 claim.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to quote the 1.920x PIP wall win
   or 499x overlay active-count row without also reporting the 5.728x
   RayJoin-author-over-RTDL-OptiX gap and the missing full M3 phase table.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: tune Spatial RayJoin-specific code immediately. That might improve one
   app, but it would not build a reusable V3 topology-stream capability.
4. Can I now try a different path that actually solves the problem?
   Yes. The correct next path is generic overhead work: full M3 phase accounting
   for topology-stream phases, then reducing non-traversal overhead across any
   route that emits topology/continuation streams.

## Latest Verification - RTNN Full-Batch Float32 Same-Contract Runner

- Added
  `scripts/v3_phoenix_rtnn_full_batch_float32_same_contract_runner.py` as the
  checked-in runner for the M112-approved
  `rtnn_full_batch_float32_same_contract_m7_rerun` path.
- The runner compares generic RTDL OptiX
  `ranked-summary-aggregate-prepared-query-batch-float32` against a
  same-contract CuPy grid reference. It records point manifest, environment,
  phase/wall timing, summary-signature parity, and material speedup checks.
- Current status is only
  `rtnn_full_batch_float32_same_contract_runner_plan_not_m7` in the queue:
  there is no new pod evidence, no M7 row, and no public RTNN speedup wording.
- The queue now records `active_pod_runner:
  scripts/v3_phoenix_rtnn_full_batch_float32_same_contract_runner.py`,
  `active_pod_runner_status: runner_available_not_yet_rt_pod_evidence`, and
  `active_candidate_status:
  rtnn_full_batch_float32_same_contract_runner_plan_not_m7`.
- `py -3 -m unittest
  tests.v3_phoenix_rtnn_full_batch_float32_same_contract_runner_test`: 4 tests
  passed.
- `py -3 scripts\v3_phoenix_next_engine_work_queue.py --pretty --json-out
  docs\rebuild\v3\phoenix_v3_next_generic_engine_work_queue_2026-06-21.json
  --md-out docs\rebuild\v3\phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`:
  regenerated the queue with `rtnn_full_batch_float32_runner_exists: true`.
- `py -3 -m unittest
  tests.v3_phoenix_rtnn_full_batch_float32_same_contract_runner_test
  tests.v3_phoenix_next_engine_work_queue_test
  tests.v3_release_wording_gate_test`: 12 tests passed.
- `py -3 scripts\v3_phoenix_rtnn_full_batch_float32_same_contract_runner.py
  --dry-run --point-count 64 --routes optix,cupy_grid --output-dir <temp>`:
  returned `rtnn_full_batch_float32_same_contract_runner_plan_not_m7` and did
  not claim route completion.
- `py -3 scripts\v3_release_wording_gate.py --pretty`: passed with the RTNN
  runner/not-M7 strings present and release/public speedup authorization false.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`: returned
  `blocked_not_release`, `failed_checks: []`, and kept
  `m7_qualified_release_rows: 8`.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: passed 59 modules /
  277 tests.

## Goal-Level Decision Self-Audit - RTNN Runner Path

Decision: stage the RTNN float32 same-contract rerun path through a reusable
runner instead of promoting M106 directly or editing app-specific RTNN code.

1. Was I foolish?
   No. This turns the next RTNN work into a reproducible V3 engine evidence
   entrypoint while keeping all release and M7 flags false.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to quote the M106 787.53x
   vs-Embree or 2.26x vs-author numbers as a public RTNN win without
   same-contract reference parity and fresh review.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: repair the exact float64 tie policy first. That remains valid, but it is
   a semantic/parity review path rather than the fastest route to fresh
   full-batch evidence.
4. Can I now try a different path that actually solves the problem?
   Yes. The next RTNN step is a real RTX run of the checked-in runner with
   OptiX plus CuPy grid reference, followed by external AI review and Codex
   consensus before any M7 reopen decision.

## Latest Verification - Barnes-Hut Vector-Accumulation Contract

- Added
  `scripts/v3_phoenix_barnes_hut_vector_accumulation_contract.py` and generated
  `docs/rebuild/v3/phoenix_v3_barnes_hut_vector_accumulation_contract_2026-06-21.md`.
- Current status is
  `barnes_hut_vector_accumulation_contract_candidate_not_m7`: release,
  public-speedup, RT-core-speedup, whole-app, broad V3-over-V2, and M7
  promotion flags remain false.
- The packet records the serious M6 evidence honestly: fused Numba CUDA is
  fastest at 32,768 / 65,536 / 131,072 bodies, while prepared
  RTDL/OptiX+Numba is 7.328x, 5.120x, and 13.912x slower than the fastest route.
- The V3 engine target is not a Barnes-Hut app rewrite. It is the generic
  `generic_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_v1` primitive:
  fused aggregate-tree traversal plus weighted vector accumulation into
  source-id keyed device output columns, without aggregate-frontier row
  emission on the hot path.
- M7 rows added by this packet: 0. External review and Codex consensus are
  still required before any future M7 reopen decision.
- Supersession note: the current Phoenix queue now aligns this packet with
  M129/M131/M142. The Python wrapper exists, the naive all-node OptiX route is
  semantically blocked because it cannot prove subtree-skip/no-double-counting,
  and Goal4541 closed Barnes-Hut as current mixed-explicit route guidance.
  Therefore Barnes-Hut vector accumulation is a future-research record, not an
  active Phoenix V3 P0 release blocker.
- Review handoff was saved to
  `docs/reviews/call_for_review_phoenix_v3_barnes_hut_vector_accumulation_contract_2026-06-21.md`.
  A Claude CLI attempt was recorded as blocked in
  `docs/reviews/claude_blocked_phoenix_v3_barnes_hut_vector_accumulation_contract_2026-06-21.md`;
  this does not count as Claude approval or 2-AI consensus.
- Verification:
  `py -3 -m unittest tests.v3_phoenix_barnes_hut_vector_accumulation_contract_test tests.v3_phoenix_next_engine_work_queue_test tests.v3_release_wording_gate_test`
  passed 13 tests;
  `py -3 scripts\v3_release_wording_gate.py --pretty` passed;
  `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty` returned
  `blocked_not_release`; `py -3 scripts\run_test_matrix.py --group
  v3_rebuild` passed 60 modules / 282 tests.

## Goal-Level Decision Self-Audit - Barnes-Hut Vector Accumulation

Decision: turn Barnes-Hut/vector-accumulation into a generic V3 engine-gap
contract, not an app win.

1. Was I foolish?
   No. The evidence says the current prepared RTDL/OptiX frontier-emission route
   is slower than fused Numba CUDA, so the honest V3 move is to define the
   missing reusable primitive.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to sell route parity,
   contribution-row scale, or OptiX participation as Barnes-Hut RT-core
   acceleration while the fastest measured route is not RTDL/OptiX.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: tune Barnes-Hut-specific code or keep quoting old M101/M121 reports.
   That might improve a demo, but it would not establish a language-level V3
   capability.
4. Can I now try a different path that actually solves the problem?
   Yes. Keep the packet as the future RT-native vector-accumulation contract,
   but do not spend current Phoenix V3 release work on it until a reviewed
   hierarchical traversal design exists. Current active work should stay on
   RTNN, AABB, and Spatial RayJoin evidence/review blockers.

## Latest Verification - AABB Prepare-Reuse Serious RTX Evidence

- Ran the checked-in AABB prepare-reuse runner on the RTX pod:
  `root@213.173.108.14 -p 11592`, GPU `NVIDIA RTX 4000 Ada Generation`,
  driver `550.127.05`, compute capability `8.9`.
- Evidence directory:
  `docs/rebuild/v3/evidence/phoenix_v3_aabb_prepare_reuse_serious_20260621`.
- Packet:
  `docs/rebuild/v3/phoenix_v3_aabb_prepare_reuse_serious_rtx_evidence_2026-06-21.md`.
- Run shape: `jittered_grid`, 32,768 indexed AABBs, 32,768 query AABBs,
  warmup 3, repeat 50, backends `embree,optix`, RT hardware required.
- Correctness and scope checks passed: both backends ran, CPU-reference parity
  passed, complete candidate coverage passed, prepared-session reuse was
  observed, and prepare/query/collect/wall phases were recorded.
- Result: useful not-M7 evidence. OptiX/Embree cold-plus-collect wall speedup
  was 1.140x, below the predeclared 1.20 material-speedup floor; query-total
  speedup was 1.178x; OptiX prepare remained slower at 0.624x.
- M7 rows added by this packet: 0. No public AABB, contact, full-solver, or
  broad V3-over-V2 speedup claim is authorized.

## Goal-Level Decision Self-Audit - AABB Serious RTX Evidence

Decision: record the serious AABB prepare-reuse RTX run as useful not-M7
evidence.

1. Was I foolish?
   No. The run used serious scale, RTX hardware, both backends, parity, phase
   accounting, and the predeclared material-speedup floor.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to round 1.140x up into a V3 win,
   quote query-only numbers, or ignore that OptiX prepare remains slower.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: skip the run and keep the runner as a plan. That would preserve a clean
   story but would not answer whether prepare reuse materially fixes AABB.
4. Can I now try a different path that actually solves the problem?
   Yes. Use this low-margin evidence to drive engine-level overhead work or
   another reviewer-approved prepared-reuse shape before any M7 review.

## Latest RTNN Evidence Update

The RTNN full-batch float32 same-contract runner has now been executed on the
RTX 4000 Ada pod after installing CuPy in an isolated remote venv.

- Main packet:
  `docs/rebuild/v3/phoenix_v3_rtnn_full_batch_float32_same_contract_rtx_evidence_2026-06-21.md`
- Main raw summary:
  `docs/rebuild/v3/evidence/rtnn_full_batch_float32_same_contract_1048576_r5_20260621/summary.json`
- Review request:
  `docs/reviews/call_for_review_phoenix_v3_rtnn_full_batch_float32_same_contract_rtx_evidence_2026-06-21.md`
- External-review blocker:
  `docs/reviews/external_review_blocked_phoenix_v3_rtnn_full_batch_float32_same_contract_rtx_evidence_2026-06-21.md`

Current status:

`rtnn_full_batch_float32_hot_query_candidate_pending_2ai_wall_blocked_not_m7`

Key facts from the 1,048,576-point repeat5 run:

- Same-contract signature parity passed against the CuPy grid reference.
- Prepared OptiX hot-query median: `0.010823458433151245` seconds.
- CuPy grid hot-query median: `0.0843174010515213` seconds.
- Prepared-hot-query OptiX/CuPy speedup: `7.790x`.
- OptiX cold-plus-query wall: `5.28186272084713` seconds.
- CuPy cold-plus-query wall: `2.0769412517547607` seconds.
- Cold-plus-query OptiX/CuPy speedup: `0.393x`.
- Runner-wall OptiX/CuPy speedup: `0.627x`.

Interpretation:

This is real V3 generic ranked_summary progress for a prepared hot-query
contract, but it is not an RTNN whole-app win and not an end-to-end speedup row.
Load, pack, and OptiX preparation dominate wall time. No M7 promotion is
authorized because external review is unavailable and because wall/end-to-end
wording remains blocked.

Latest verification after the RTNN evidence update:

- `py -3 -m unittest tests.v3_phoenix_rtnn_full_batch_float32_pod_evidence_test tests.v3_phoenix_next_engine_work_queue_test tests.v3_release_wording_gate_test`: 14 tests passed.
- `py -3 scripts\v3_release_wording_gate.py --pretty`: passed with no missing required strings and no violations.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`: `blocked_not_release`.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: 62 modules / 293 tests passed.

## Goal-Level Decision Self-Audit - RTNN RTX Evidence

Decision: classify the fresh RTNN full-batch float32 same-contract RTX run as a
prepared-hot-query candidate, not an M7 or end-to-end win.

1. Was I foolish?
   No. The classification keeps the substantial hot-query improvement and the
   wall-time regression visible at the same time.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to market the 7.790x hot-query
   number while hiding the 0.393x cold-plus-query and 0.627x runner-wall
   regressions.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Reject RTNN entirely because wall time loses, or promote it entirely
   because hot time wins. Either path would erase important evidence.
4. Can I now try a different path that actually solves the problem?
   Yes. Keep the row as a narrow candidate, restore external review before M7,
   and direct engine work toward pack/prepare amortization or exact/tie-stable
   parity before promotion.

## Latest AABB Prepare-Reuse Scale Update

The AABB prepare-reuse runner was rerun at 65,536 indexed/query AABBs on the
same RTX 4000 Ada pod:

- Scale packet:
  `docs/rebuild/v3/phoenix_v3_aabb_prepare_reuse_scale_evidence_2026-06-21.md`
- 65k raw summary:
  `docs/rebuild/v3/evidence/phoenix_v3_aabb_prepare_reuse_65536_r50_20260621/summary.json`

Current status:

`aabb_prepare_reuse_scale_evidence_not_m7_scale_does_not_clear_floor`

Key facts:

- 32,768 AABBs, repeat50: OptiX/Embree cold-plus-collect wall speedup `1.140x`.
- 65,536 AABBs, repeat50: OptiX/Embree cold-plus-collect wall speedup `1.087x`.
- Both rows passed backend execution, CPU-reference parity, complete candidate
  coverage, reuse observation, and phase-table checks.
- Both rows are below the predeclared `1.20x` material wall-speedup floor.
- The larger scale got worse, so scale alone does not reopen AABB prepare-reuse
  for M7.

Interpretation:

This is a no-go scale result, not a failure of the whole V3 direction. It means
the AABB prepare-reuse path needs real generic overhead work: reduce OptiX
prepare cost, repeated query cost, or collect/compaction cost. It should not be
rescued by trying larger and larger scales until a number happens to cross the
floor.

## Goal-Level Decision Self-Audit - AABB Scale Evidence

Decision: record the 65,536-row AABB prepare-reuse rerun as scale evidence that
does not clear the M7 material floor.

1. Was I foolish?
   No. The rerun tested whether a serious larger scale amortizes the prepared
   AABB path enough to meet the predeclared floor.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to keep shopping scales or quote
   query-only wins after the 65,536-row wall result got worse.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Skip the scale rerun and assume 32,768 was representative. That would
   leave a plausible but untested scale question open.
4. Can I now try a different path that actually solves the problem?
   Yes. Use this no-go scale packet to drive actual generic overhead work
   instead of more app-specific or scale-only experiments.

## Latest Spatial RayJoin M3 Gap And Queue Update

This pass added the Spatial RayJoin M3 gap packet and refreshed the generic
engine work queue without promoting Spatial RayJoin to M7.

New evidence/control files:

- `scripts/v3_phoenix_spatial_rayjoin_m3_gap_analysis.py`
- `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_m3_gap_analysis_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_m3_gap_analysis_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.json`

Key facts:

- Spatial RayJoin remains `spatial_rayjoin_m3_gap_analysis_not_m7`.
- It does not authorize public Spatial RayJoin speedup wording, paper
  reproduction wording, RTDL-beats-RayJoin wording, true-zero-copy wording, or
  V4/embedding wording.
- The useful V3 signal is generic: old large-PIP evidence moves OptiX hot wall
  from `273.922ms` to `120.060ms` (`2.282x`) when the query point stream stays
  resident, and visible residual after native transfer falls from `140.988ms`
  to `1.373ms`.
- The next legitimate work is a generic reusable topology-stream prepared
  handle/runner that keeps query columns resident, emits a full M3 phase table,
  and avoids RayJoin-specific native shortcuts.

Latest verification after the M3 gap and queue refresh:

- `py -3 -m unittest tests.v3_phoenix_spatial_rayjoin_m3_gap_analysis_test tests.v3_phoenix_next_engine_work_queue_test tests.v3_release_wording_gate_test`: 14 tests passed.
- `py -3 scripts\v3_release_wording_gate.py --pretty`: passed with no missing
  required strings and no violations.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`: returned
  `blocked_not_release`, `failed_checks: []`, `m7_qualified_release_rows: 8`,
  and kept broad V3-over-V2 wording unauthorized.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: passed 64 modules /
  304 tests.

## Goal-Level Decision Self-Audit - V3 Engine Versus App Work

Decision: continue Phoenix as V3 language-level generic engine work, not as
per-app optimization or release polishing.

1. Was I foolish?
   No for this decision. It directly answers the current risk: V3 must prove
   reusable engine improvements, not collect app-specific wins.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to count a single app shortcut,
   a 1.01x-style marginal result, or a hot-only ratio as a V3 language
   breakthrough.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. The other path is to treat each benchmark app as a separate product.
   That may improve demos, but it does not solve the v2.x problem of lacking a
   trustworthy, repeatable, high-performance V3 language surface.
4. Can I now try a different path that actually solves the problem?
   Yes. The current path is to promote only reusable capabilities with material
   row-scoped evidence: grouped reduction device-column preparation is already
   a real non-1.01x win; RTNN, AABB prepare-reuse, and Spatial RayJoin stay in
   the open engine queue until their wall/phase evidence and review gates
   justify promotion. Barnes-Hut is retained as a future-research record after
   M129/M131/M142, not as a current Phoenix P0 build target.

## Latest Spatial RayJoin Topology-Stream Interface Update

This pass moved Spatial RayJoin from only a gap analysis toward a reusable V3
topology-stream interface, without closing the queue item or promoting a row.

Code/interface changes:

- `src/rtdsl/v3_0_topology_stream_accounting.py` now defines
  `topology_stream_m3_phase_table_v1` and
  `topology_stream_prepared_handle_v1`.
- The prepared OptiX Spatial RayJoin payload now emits
  `topology_stream_m3_phase_table` and `topology_stream_prepared_handle`.
- `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_topology_stream_contract_2026-06-21.md`
  now records those two contracts as local interface progress only.
- `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`
  still keeps Spatial RayJoin open and says the next step is a fresh POD packet.

Current interpretation:

- This is V3 generic engine progress, not RayJoin-specific native tuning.
- It does not add an M7 row.
- It does not authorize public Spatial RayJoin speedup, RTDL-beats-RayJoin,
  true-zero-copy, broad V3-over-V2, or V4/embedding wording.
- It gives the next POD run a concrete table/handle surface for full M3 phase
  evidence instead of scattered app fields.

Latest verification after the topology-stream interface update:

- `py -3 -m unittest tests.v3_phoenix_spatial_rayjoin_topology_stream_contract_test tests.v3_rebuild_spatial_rayjoin_route_test`: 9 tests passed.
- `py -3 -m unittest tests.v3_phoenix_spatial_rayjoin_topology_stream_contract_test tests.v3_rebuild_spatial_rayjoin_route_test tests.v3_phoenix_next_engine_work_queue_test tests.v3_release_wording_gate_test`: 17 tests passed.
- `py -3 scripts\v3_release_wording_gate.py --pretty`: passed with no missing required strings and no violations.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`: returned
  `blocked_not_release`, `failed_checks: []`, and kept
  `m7_qualified_release_rows: 8`.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: passed 64 modules /
  306 tests.

## Goal-Level Decision Self-Audit - Spatial Topology-Stream Interface

Decision: add generic M3 phase-table and prepared-handle metadata to the V3
topology-stream layer and Spatial RayJoin prepared OptiX payload, while keeping
Spatial RayJoin unpromoted.

1. Was I foolish?
   No. This makes the next performance run more measurable without turning a
   local interface improvement into a release claim.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to call the metadata itself a
   performance win or to treat it as true zero-copy.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. I could have tuned only the RayJoin app route or continued writing
   prose. The former would not be a V3 generic engine improvement; the latter
   would not prepare a stronger POD run.
4. Can I now try a different path that actually solves the problem?
   Yes. The next path is to run a fresh POD packet through the new
   `topology_stream_m3_phase_table_v1` / `topology_stream_prepared_handle_v1`
   surface, then judge it by wall/phase evidence and external review.

## Latest Spatial RayJoin M3 POD Runner Preparation

This pass added the checked-in runner for the next Spatial RayJoin POD packet:

`scripts/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py`

Runner purpose:

- Run the PIP prepared OptiX route through the new
  `topology_stream_m3_phase_table_v1` and `topology_stream_prepared_handle_v1`
  payload fields.
- Require full M3 phase-table presence by default.
- Reject samples that authorize public speedup, M7, release, or true-zero-copy
  wording.
- Emit `spatial_rayjoin_topology_stream_m3_pod_evidence_pending_review_not_m7`
  until fresh POD evidence and review justify anything stronger.

The generic work queue now records this runner as
`active_pod_runner` with status
`local_runner_added_pending_pod_evidence_not_m7`.

Latest verification after adding the runner:

- `py -3 -m unittest tests.v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner_test tests.v3_phoenix_next_engine_work_queue_test tests.v3_release_wording_gate_test`: 11 tests passed.
- `py -3 scripts\v3_release_wording_gate.py --pretty`: passed with no missing
  required strings and no violations.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`: returned
  `blocked_not_release`, `failed_checks: []`, and kept
  `m7_qualified_release_rows: 8`.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: passed 65 modules /
  309 tests.

## Goal-Level Decision Self-Audit - Spatial M3 POD Runner

Decision: add a focused Spatial RayJoin topology-stream M3 POD runner before
spending pod time on fresh performance evidence.

1. Was I foolish?
   No. This turns the next paid pod action into a repeatable evidence packet
   instead of another ad hoc benchmark.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to run the pod first and only
   afterwards discover missing M3 table, handle metadata, or claim flags.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Reuse the older Goal3244 RayJoin runner unchanged. It is useful for
   comparison, but it does not force the Phoenix M3 table/handle contract.
4. Can I now try a different path that actually solves the problem?
   Yes. The next path is to run the new runner locally under tests, then run it
   on the RTX pod and intake the resulting packet as not-M7 evidence unless it
   passes the full M7 and review bar.

## Spatial RayJoin Exact-Executor POD Evidence

This pass moved the Spatial RayJoin queue item from "runner pending" to fresh
POD evidence collected, while keeping it not-M7.

Code and runner changes:

- `src/rtdsl/v3_0_topology_stream_accounting.py` now treats exact
  prepared-points native `candidate_write_pass` as RT traversal/candidate
  emission when `candidate_count_pass` is zero. This fixes the misleading
  `rt_traversal_sec: 0.0` interpretation for the exact scalar-count route.
- `examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
  now supports `count_mode="exact_prepared_points_executor"`.
- `scripts/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py`
  defaults to the exact prepared-points executor route and leaves the
  device-filtered route as a diagnostic option only.

POD evidence copied back locally:

- Main packet:
  `docs/rebuild/v3/evidence/phoenix_v3_spatial_rayjoin_topology_m3_public_county_exact_executor_repeat50_20260621/summary.json`
- Human-readable note:
  `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_topology_stream_exact_executor_pod_evidence_2026-06-21.md`
- Rejected device-filtered probe:
  `docs/rebuild/v3/evidence/phoenix_v3_spatial_rayjoin_topology_m3_public_county_device_filtered_smoke_20260621/run.log`

Main result:

- Dataset: public `br_county.cdb`.
- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05.
- Repeat protocol: sample_repeat=5, query_repeat=50, warmup=5.
- Stable exact row count: 47,262.
- Failed checks: `[]`.
- M7 rows added: 0.
- Median prepared query: 0.023217812180519104 s.
- Median repeat=50 prepared query total: 1.1688360273838043 s.
- Median runner wall: 2.8939708545804024 s.
- Median M3 phases:
  - static scene prepare: 0.19943977892398834 s
  - query stream prepare: 0.05608516186475754 s
  - device transfer/residency: 0.0 s
  - RT traversal/candidate emission: 0.000437483 s
  - topology continuation/exact refine: 0.023139639 s
  - host return/scalar materialization: 0.000076802 s

Current interpretation:

- This is V3 generic-engine progress: prepared point columns plus a reusable
  exact scalar-count executor are exposed through the topology-stream M3 table.
- It is not a Spatial RayJoin M7 row. It still lacks author-timing-basis
  comparison, external release review, and a material public speedup claim.
- It is not a true-zero-copy claim. Query columns are device-resident after
  preparation, but exact authority still downloads candidates and refines
  membership on the host.
- The rejected device-filtered route is a correctness blocker, not a route to
  publish: it returned 47,570 versus the exact count 47,262.

Latest verification after this pass:

- `py -3 -m unittest tests.v3_phoenix_spatial_rayjoin_topology_stream_contract_test tests.v3_rebuild_spatial_rayjoin_route_test tests.v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner_test`: 13 tests passed.
- `py -3 scripts\v3_phoenix_next_engine_work_queue.py --pretty`: passed with
  `failed_checks: []`.

## Goal-Level Decision Self-Audit - Spatial Exact Executor Evidence

Decision: use the exact prepared-points executor as the Phoenix Spatial
topology-stream evidence route, and explicitly reject device-filtered counting
after the public county correctness mismatch.

1. Was I foolish?
   No. The fresh POD run first tested the tempting device-filtered route and
   caught a real exact-count mismatch, then moved to a correctness-preserving
   reusable executor route.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would have been to tune around or ignore
   `47,570 != 47,262`, or to publish device-filtered timing because it looked
   faster.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. I could have stayed with the older exact prepared-points scalar count
   without executor capacity accounting. That path is correct but weaker as a
   V3 engine surface because it hides reuse and M3 phase attribution.
4. Can I now try a different path that actually solves the problem?
   Yes. The next path is to reduce the generic topology-continuation/exact-refine
   bottleneck or build an author-basis comparison packet for external review.
   No public or M7 claim is justified yet.

## Latest Verification - Spatial Relation-Status No-Go

After the exact-executor evidence pass, I tested a more fused generic Spatial
candidate: `count_mode="relation_status_corrected_executor_validated"`.
This route was attractive because it reused prepared point probe columns and a
native relation-status scalar-count executor instead of materializing a row
stream. It failed the required exact public-county validation on the RTX pod:

- Command route:
  `scripts/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py --count-mode relation_status_corrected_executor_validated`.
- Dataset: public `br_county.cdb`.
- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05.
- Exact authority count: 47,262.
- Candidate relation-status count: 47,259.
- Candidate minus exact: -3.
- Failure class: `validated_candidate_exactness_mismatch`.
- No M7 row was added.
- No release, public speedup, paper reproduction, RTDL-beats-RayJoin,
  true-zero-copy, broad V3-over-V2, or V4/embedding wording is authorized.

Recorded evidence:

- No-go packet:
  `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_corrected_no_go_2026-06-21.md`.
- POD run log:
  `docs/rebuild/v3/evidence/phoenix_v3_spatial_rayjoin_relation_status_corrected_rejected_smoke_20260621/run.log`.
- Latest full rebuild matrix:
  `docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_relation_status_no_go_20260621.json`.

Verification after this no-go pass:

- `C:\Python311\python.exe -m unittest tests.v3_rebuild_spatial_rayjoin_route_test tests.v3_phoenix_spatial_rayjoin_topology_stream_contract_test tests.v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner_test tests.v3_phoenix_spatial_rayjoin_relation_status_corrected_no_go_test tests.v3_phoenix_next_engine_work_queue_test tests.v3_release_wording_gate_test`:
  27 focused tests passed.
- `C:\Python311\python.exe scripts\run_test_matrix.py --group v3_rebuild`:
  67 modules / 321 tests passed.
- `C:\Python311\python.exe scripts\v3_release_wording_gate.py --pretty`:
  passed with zero violations and zero missing required strings.
- `C:\Python311\python.exe scripts\v3_phoenix_release_readiness_gate.py --pretty`:
  returned `blocked_not_release`, `failed_checks: []`,
  `m7_qualified_release_rows: 8`, and `release_authorized: false`.

## Goal-Level Decision Self-Audit - Spatial Relation-Status No-Go

Decision: reject the relation-status corrected Spatial executor as a V3 release
or M7 route until its exactness is fixed on real POD data.

1. Was I foolish?
   No. Testing the route was a reasonable generic-engine attempt; the important
   part is that it failed closed instead of being promoted.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would have been to hide the `47,259 !=
   47,262` mismatch or describe the fused route as a speedup despite failing
   exactness.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. I could have stayed only with the slower exact executor and skipped the
   fused candidate. That would be safer but would not answer whether V3 has a
   stronger reusable topology-stream route.
4. Can I now try a different path that actually solves the problem?
   Yes. Either repair the generic relation-status boundary semantics and rerun
   exact validation, or move to another generic P0 optimization with stronger
   evidence potential instead of spending V3 budget on app-specific shortcuts.

## Latest Verification - Spatial Exact-F64 Native Scalar Count Intake

The relation-status no-go was repaired as a generic native scalar-count route,
not as a Spatial-only application shortcut. The OptiX any-hit continuation now
evaluates the full closed-shape predicate in double precision on the device for
each AABB candidate, then emits only the scalar count. The old no-go remains in
history and is still useful: it proves why float32 relation-status prefiltering
could not be promoted.

POD evidence:

- Build: `make build-optix OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0`
  succeeded on the RTX pod.
- Dataset: public `br_county.cdb`.
- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05.
- Repeat protocol: sample_repeat=5, query_repeat=50, warmup=5.
- Stable exact row count: 47,262.
- Failed checks: `[]`.
- M7 rows added: 0.
- Median prepared query: 0.0063093192875385284 s.
- Median repeat=50 prepared query total: 0.3156639263033867 s.
- Median runner wall: 1.974891372025013 s.
- Native counters: 155,555 raw AABB candidates, 47,550 boundary-status
  candidates, 108,293 exact-f64 rejects, 47,262 emitted exact hits.

Comparison against the earlier exact executor packet:

- Prepared-query median improved from 0.023217812180519104 s to
  0.0063093192875385284 s: 3.680x.
- Repeat=50 prepared-query total improved from 1.1688360273838043 s to
  0.3156639263033867 s: 3.703x.
- Runner wall improved from 2.8939708545804024 s to 1.974891372025013 s:
  1.465x.
- The old exact executor had topology continuation/exact refine median
  0.023139639 s. The repaired native scalar-count packet reports that phase as
  0.0 s because the exact predicate work moved into the native device route.

Recorded evidence:

- Intake packet:
  `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_intake_2026-06-21.md`.
- POD evidence directory:
  `docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_exact_f64_attempt_20260621`.
- Current work queue:
  `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`.

Current interpretation:

- This is real V3 generic-engine progress for the
  `point_location_topology_stream` / native scalar-count route.
- It is not a Spatial RayJoin app-specific speed hack.
- It is not a V3 release authorization, not M7, and not a broad
  V3-over-V2/RTDL-beats-RayJoin claim.
- Promotion still needs author-timing basis, adverse-subset parity, external
  review, and wording review.

Verification after this repair:

- `C:\Python311\python.exe -m unittest tests.goal3684_native_relation_status_corrected_scalar_count_test tests.v3_phoenix_spatial_rayjoin_relation_status_exact_f64_intake_test tests.v3_rebuild_spatial_rayjoin_route_test tests.v3_phoenix_spatial_rayjoin_relation_status_corrected_no_go_test tests.v3_release_wording_gate_test`:
  20 focused tests passed.
- `C:\Python311\python.exe -m unittest tests.v3_phoenix_next_engine_work_queue_test tests.v3_phoenix_spatial_rayjoin_relation_status_exact_f64_intake_test tests.v3_release_wording_gate_test`:
  14 queue/intake/wording tests passed.
- `C:\Python311\python.exe scripts\v3_phoenix_next_engine_work_queue.py --json-out docs\rebuild\v3\phoenix_v3_next_generic_engine_work_queue_2026-06-21.json --md-out docs\rebuild\v3\phoenix_v3_next_generic_engine_work_queue_2026-06-21.md --pretty`:
  passed with `failed_checks: []`.
- `C:\Python311\python.exe scripts\run_test_matrix.py --group v3_rebuild`:
  68 modules / 327 tests passed after the exact-f64 repair intake. The captured
  result is
  `docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_spatial_exact_f64_intake_20260621.json`.

## Goal-Level Decision Self-Audit - Spatial Exact-F64 Repair Intake

Decision: repair the generic relation-status scalar-count route by moving exact
closed-shape membership to device-side double precision, record the result as
intake only, and keep all release/M7 claims false.

1. Was I foolish?
   No. The foolish path would have been to discard the failed relation-status
   route as "just a bad app row" or to publish it despite the three-row
   correctness miss. Repairing the generic predicate route addressed the actual
   engine bottleneck while preserving the no-go record.
2. If yes, what actions made the decision foolish?
   Not applicable. The risky action I had to avoid was optimizing around a
   float32 prefilter that could lose true positives.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. I could have moved immediately to another benchmark app, but that would
   leave an important topology-stream bottleneck unresolved and would not answer
   whether V3 has reusable native scalar-count value.
4. Can I now try a different path that actually solves the problem?
   Yes. The next path is to seek review, run adverse subsets, and repeat this
   same strict intake process on the remaining P0 generic routes instead of
   calling V3 done from one repaired row.

## Latest Verification - Spatial Exact-F64 Review Gate

After the exact-f64 intake, I attempted external AI review for the Spatial
repair. This did not produce a valid external verdict:

- Claude was not available in the checked Windows shell, local Linux `lx1`, or
  RTX pod PATH.
- Gemini failed before review with `IneligibleTierError`.
- The failed Gemini output is preserved at
  `docs/reviews/gemini_phoenix_v3_spatial_relation_status_exact_f64_intake_review_2026-06-21.md`.
- The Claude-unavailable record is
  `docs/reviews/claude_unavailable_phoenix_v3_spatial_relation_status_exact_f64_intake_2026-06-21.md`.
- The combined external-blocker record is
  `docs/reviews/external_ai_blocked_phoenix_v3_spatial_relation_status_exact_f64_intake_2026-06-21.md`.

I therefore added a machine-readable review gate:

- `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_review_gate_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_review_gate_2026-06-21.json`

Gate status:

```text
spatial_rayjoin_relation_status_exact_f64_review_blocked_not_m7
```

The gate preserves the useful internal result, prepared-query `3.680x` and
runner-wall `1.465x` versus the prior RTDL exact executor, but blocks M7
reopening until all of these exist:

- external AI review with a real verdict;
- Codex consensus response to that review;
- same-dataset RayJoin author timing basis or a scope that does not cite author
  performance;
- adverse-subset parity;
- public wording review.

Verification after this gate:

- `C:\Python311\python.exe scripts\v3_phoenix_spatial_rayjoin_relation_status_exact_f64_review_gate.py`:
  passed with `failed_checks: []`.
- `C:\Python311\python.exe scripts\v3_phoenix_next_engine_work_queue.py --json-out docs\rebuild\v3\phoenix_v3_next_generic_engine_work_queue_2026-06-21.json --md-out docs\rebuild\v3\phoenix_v3_next_generic_engine_work_queue_2026-06-21.md --pretty`:
  passed with `failed_checks: []`.
- `C:\Python311\python.exe -m unittest tests.v3_phoenix_spatial_rayjoin_relation_status_exact_f64_review_gate_test tests.v3_phoenix_spatial_rayjoin_relation_status_exact_f64_intake_test tests.v3_phoenix_next_engine_work_queue_test tests.v3_release_wording_gate_test`:
  19 focused tests passed.
- `C:\Python311\python.exe scripts\run_test_matrix.py --group v3_rebuild`:
  69 modules / 332 tests passed after adding the review gate. The captured
  result is
  `docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_spatial_exact_f64_review_gate_20260621.json`.

## Goal-Level Decision Self-Audit - Spatial Exact-F64 Review Gate

Decision: keep the exact-f64 route as material intake evidence but add a review
gate that blocks M7 promotion while external review, author-basis, and adverse
subset gates are missing.

1. Was I foolish?
   No. The route is promising, but the responsible action is to prevent a
   strong internal comparison from becoming an unsupported public claim.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to treat Claude/Gemini tool
   failure as approval, or to replace external review with Codex self-approval.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. I could have kept tuning Spatial immediately. That risks single-route
   fixation and does not solve the release-discipline problem.
4. Can I now try a different path that actually solves the problem?
   Yes. Leave Spatial behind a review gate and continue Phoenix on the next
   generic engine route while retrying external review when a working channel is
   available.

## Latest Verification - RTNN Full-Batch Float32 Review Gate

The next queue item after Spatial was RTNN `ranked_summary`. The serious RTX
full-batch float32 packet is useful, but dangerous if read loosely:

- Point count: 1,048,576.
- Repeat: 5.
- Same-contract signature: matched.
- Prepared-hot-query OptiX/CuPy-grid speedup: 7.790x.
- Cold-plus-query wall speedup: 0.393x.
- Runner-wall speedup: 0.627x.

I added a Codex blocking review and a machine-readable review gate:

- `docs/reviews/codex_phoenix_v3_rtnn_full_batch_float32_same_contract_blocking_review_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_rtnn_full_batch_float32_review_gate_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_rtnn_full_batch_float32_review_gate_2026-06-21.json`

Gate status:

```text
rtnn_full_batch_float32_review_blocked_not_m7
```

The gate keeps the `7.790x` result as internal prepared-hot-query evidence only
and blocks M7 until:

- external AI review produces a real verdict;
- Codex consensus responds to that review;
- prepared-hot-query-only scope is accepted;
- pack/prepare amortization or exact/tie-stable repair is addressed;
- phase/wall timing and public wording keep whole-app, paper, universal
  nearest-neighbor, V3-over-V2, and end-to-end claims false.

Verification after this gate:

- `C:\Python311\python.exe scripts\v3_phoenix_rtnn_full_batch_float32_review_gate.py`:
  passed with `failed_checks: []`.
- `C:\Python311\python.exe scripts\v3_phoenix_next_engine_work_queue.py --json-out docs\rebuild\v3\phoenix_v3_next_generic_engine_work_queue_2026-06-21.json --md-out docs\rebuild\v3\phoenix_v3_next_generic_engine_work_queue_2026-06-21.md --pretty`:
  passed with `failed_checks: []`.
- `C:\Python311\python.exe -m unittest tests.v3_phoenix_rtnn_full_batch_float32_review_gate_test tests.v3_phoenix_rtnn_full_batch_float32_pod_evidence_test tests.v3_phoenix_next_engine_work_queue_test tests.v3_release_wording_gate_test`:
  19 focused tests passed.
- `C:\Python311\python.exe scripts\v3_release_wording_gate.py --pretty`:
  passed with zero violations.
- `C:\Python311\python.exe scripts\v3_phoenix_release_readiness_gate.py --pretty`:
  returned `blocked_not_release` with `failed_checks: []`.
- `C:\Python311\python.exe scripts\run_test_matrix.py --group v3_rebuild`:
  70 modules / 337 tests passed after adding the RTNN review gate. The captured
  result is
  `docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_rtnn_review_gate_20260621.json`.

## Goal-Level Decision Self-Audit - RTNN Full-Batch Float32 Review Gate

Decision: preserve RTNN's full-batch float32 prepared-hot-query signal but gate
it as review-blocked/not-M7 because wall timing regresses and external review is
missing.

1. Was I foolish?
   No. The row has a real reusable `ranked_summary` hot-query signal, but the
   wall results and review gap make promotion unsafe.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to promote `7.790x` while hiding
   `0.393x` cold-plus-query wall and `0.627x` runner wall.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. I could reject RTNN entirely because wall loses. That would avoid
   overclaim risk but would discard useful V3 engine evidence.
4. Can I now try a different path that actually solves the problem?
   Yes. Keep RTNN blocked and direct future engine work toward pack/prepare
   amortization or exact/tie-stable parity before any M7 review.

## Latest Verification - AABB Prepare-Reuse Overhead Gate

The next queue item after RTNN was AABB `aabb_candidate_stream`
prepare-reuse. The serious RTX rows are useful, but they are not material V3
performance wins:

- 32,768 indexed/query AABBs, repeat50: OptiX/Embree cold-plus-collect wall
  speedup `1.140x`.
- 65,536 indexed/query AABBs, repeat50: OptiX/Embree cold-plus-collect wall
  speedup `1.087x`.
- Material wall-speedup floor: `1.200x`.
- OptiX prepare is slower on both serious rows.
- Query-total speedup is positive but cannot be quoted as a public V3 win
  without wall clearance.
- Collect is neutral at 32,768 and slower at 65,536.

I added a machine-readable overhead gate:

- `docs/rebuild/v3/phoenix_v3_aabb_prepare_reuse_overhead_gate_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_aabb_prepare_reuse_overhead_gate_2026-06-21.json`

Gate status:

```text
aabb_prepare_reuse_overhead_gate_blocked_not_m7
```

The gate blocks AABB prepare-reuse from M7 until generic overhead work reduces
OptiX prepare cost, repeated query overhead, or collect/compaction overhead.
It also adds the overhead gate to the wording scan surface so this no-go cannot
drop out of current documentation hygiene.

Verification after this gate:

- `C:\Python311\python.exe scripts\v3_phoenix_aabb_prepare_reuse_overhead_gate.py --pretty`:
  passed with `failed_checks: []`.
- `C:\Python311\python.exe scripts\v3_phoenix_next_engine_work_queue.py --json-out docs\rebuild\v3\phoenix_v3_next_generic_engine_work_queue_2026-06-21.json --md-out docs\rebuild\v3\phoenix_v3_next_generic_engine_work_queue_2026-06-21.md --pretty`:
  passed with `failed_checks: []`.
- `C:\Python311\python.exe -m unittest tests.v3_phoenix_aabb_prepare_reuse_overhead_gate_test tests.v3_phoenix_aabb_prepare_reuse_scale_evidence_test tests.v3_phoenix_next_engine_work_queue_test tests.v3_release_wording_gate_test`:
  18 focused tests passed.
- `C:\Python311\python.exe scripts\v3_release_wording_gate.py --pretty`:
  passed with zero violations after adding the overhead gate files to the
  scanned surface.
- `C:\Python311\python.exe scripts\v3_phoenix_release_readiness_gate.py --pretty`:
  returned `blocked_not_release` with `failed_checks: []`.
- `C:\Python311\python.exe scripts\run_test_matrix.py --group v3_rebuild`:
  71 modules / 342 tests passed. The captured result is
  `docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_aabb_overhead_gate_20260621.json`.

## Goal-Level Decision Self-Audit - AABB Overhead Gate

Decision: add a hard overhead gate for AABB prepare-reuse instead of treating
sub-floor ratios as V3 progress.

1. Was I foolish?
   No. This gate prevents a low-margin `1.140x` row and a worse `1.087x`
   scale row from being mistaken for a major V3 optimization.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to promote query-only wins,
   keep increasing scale until a ratio looks good, or call this full contact or
   broad AABB acceleration.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. I could have moved straight to code tuning, but without this gate the
   current evidence would remain easy to misread.
4. Can I now try a different path that actually solves the problem?
   Yes. Use this gate as the work order for real generic overhead reduction:
   prepare, query, and collect/compaction must improve before AABB can reopen
   M7.

## Latest Verification - AABB Query-Cache Evidence

After the overhead gate, I implemented and tested a generic prepared
query-record cache for `OptixAabbIndex2D` and `EmbreeAabbIndex2D`. This is not
native result caching: each query still calls the native collector. The
optimization only avoids rebuilding the same normalized query records across a
prepared-session repeat window.

The POD query-cache evidence is:

- `docs/rebuild/v3/phoenix_v3_aabb_prepare_reuse_query_cache_evidence_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_aabb_prepare_reuse_query_cache_evidence_2026-06-21.json`
- `docs/rebuild/v3/evidence/phoenix_v3_aabb_prepare_reuse_query_cache_stats_32768_r50_20260621/`
- `docs/rebuild/v3/evidence/phoenix_v3_aabb_prepare_reuse_query_cache_stats_65536_r50_20260621/`

Result:

- Cache operation is real: both serious rows show one range-intersection cache
  entry, one miss, and 52 hits per backend.
- 32,768 indexed/query AABBs improved to `1.188x` OptiX/Embree
  cold-plus-collect wall speedup.
- 65,536 indexed/query AABBs reached only `1.135x`.
- Both rows remain below the `1.200x` material wall-speedup floor.
- Query-total speedup remains forbidden as public V3 success while wall speedup
  is below the floor.
- M7 rows added: 0.

Interpretation: this is a correct generic cleanup, not a Phoenix V3 performance
promotion. The next AABB work must go below Python query-record reuse: native
packed-query buffer reuse, OptiX prepare-cost reduction, and row-output
collect/compaction overhead.

Verification after this update:

- `C:\Python311\python.exe -m unittest tests.v3_phoenix_aabb_query_cache_evidence_test tests.v3_phoenix_aabb_prepared_query_cache_test tests.v3_phoenix_aabb_prepare_reuse_pod_runner_test`:
  12 tests passed.
- `C:\Python311\python.exe -m unittest tests.v3_phoenix_next_engine_work_queue_test tests.v3_phoenix_aabb_query_cache_evidence_test`:
  10 tests passed.
- `C:\Python311\python.exe -m unittest tests.v3_release_wording_gate_test tests.v3_phoenix_next_engine_work_queue_test tests.v3_phoenix_aabb_query_cache_evidence_test`:
  12 tests passed.
- `C:\Python311\python.exe scripts\run_test_matrix.py --group v3_rebuild`:
  73 modules / 350 tests passed. The captured result is
  `docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_aabb_query_cache_evidence_20260621.json`.

External AI review:

- Call-for-review packet:
  `docs/reviews/call_for_review_phoenix_v3_aabb_query_cache_evidence_2026-06-21.md`.
- External review is currently blocked, not complete:
  `docs/reviews/external_ai_blocked_phoenix_v3_aabb_query_cache_evidence_2026-06-21.md`.
- Therefore this AABB packet is a local engineering no-go/gate result, not a
  2-AI-closed promotion or release decision.

## Goal-Level Decision Self-Audit - AABB Query-Cache Evidence

Decision: record the AABB query-record cache as useful generic cleanup but not
as an M7 or release-performance breakthrough.

1. Was I foolish?
   No. The decision accepts the code improvement while refusing to promote
   sub-floor wall results.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to celebrate `1.188x` as close
   enough, or quote `1.238x` query-total speedup while hiding prepare and
   collect costs.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. I could keep increasing AABB scale, but the 65,536 row already got
   worse than 32,768, so that would be scale-shopping rather than solving the
   bottleneck.
4. Can I now try a different path that actually solves the problem?
   Yes. Move the AABB route to deeper generic overhead work: native packed
   query buffer reuse, prepare-cost reduction, and collect/compaction
   improvement.

## Latest Verification - AABB Native Query-Handle Evidence

I implemented the deeper generic AABB path identified above: OptiX
`range_intersection_rows` can now reuse a prepared native box-query handle
through
`rtdl_optix_collect_prepared_aabb_index_2d_range_intersection_rows_packed_queries`.
The high-level `OptixAabbIndex2D.intersection_rows` path caches that native
query handle for repeated prepared-session windows. This is still not result
caching: each repeat executes native row collection.

The POD evidence is:

- `docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_evidence_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_evidence_2026-06-21.json`
- `docs/rebuild/v3/evidence/phoenix_v3_aabb_native_query_handle_32768_r50_20260621/`
- `docs/rebuild/v3/evidence/phoenix_v3_aabb_native_query_handle_65536_r50_20260621/`

Result on the RTX 4000 Ada pod:

- 32,768 indexed/query AABBs, repeat50: `1.719x` OptiX/Embree
  cold-plus-collect wall speedup; query-total speedup `1.867x`.
- 65,536 indexed/query AABBs, repeat50: `1.637x` OptiX/Embree
  cold-plus-collect wall speedup; query-total speedup `1.743x`.
- Both rows show native query-handle cache evidence: one miss and 52 hits.
- CPU-reference parity and complete candidate coverage are true on both rows.
- This clears the predeclared `1.200x` material wall floor, so it is a real
  V3 generic-engine performance candidate.
- M7 rows added by this packet: 0. Promotion remains blocked until external
  review and Codex consensus close.

Verification after this update:

- POD `make build-optix OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0`:
  passed.
- POD focused tests:
  `python3 -m unittest tests.v3_phoenix_aabb_prepared_query_cache_test tests.goal2580_optix_aabb_index_native_symbol_test`:
  8 tests passed.
- POD OptiX row smoke:
  `python3 -m unittest tests.goal2623_optix_aabb_pair_rows_test.Goal2623OptixAabbPairRowsTest.test_optix_pair_rows_match_cpu_for_tiny_fixture tests.goal2623_optix_aabb_pair_rows_test.Goal2623OptixAabbPairRowsTest.test_optix_pair_rows_fail_closed_on_capacity_overflow`:
  2 tests passed.
- Local focused tests:
  `C:\Python311\python.exe -m unittest tests.v3_phoenix_aabb_prepared_query_cache_test tests.goal2580_optix_aabb_index_native_symbol_test tests.v3_phoenix_aabb_query_cache_evidence_test`:
  12 tests passed.
- Local queue/evidence tests:
  `C:\Python311\python.exe -m unittest tests.v3_phoenix_next_engine_work_queue_test tests.v3_phoenix_aabb_native_query_handle_evidence_test tests.v3_phoenix_aabb_prepared_query_cache_test`:
  13 tests passed.
- Wording/readiness guard:
  `C:\Python311\python.exe -m unittest tests.v3_release_wording_gate_test tests.v3_phoenix_aabb_native_query_handle_evidence_test tests.v3_phoenix_next_engine_work_queue_test`:
  10 tests passed.
- `C:\Python311\python.exe scripts\v3_release_wording_gate.py --pretty`:
  pass, with the new native-query-handle packet included in the scanned set.
- `C:\Python311\python.exe scripts\v3_phoenix_release_readiness_gate.py --pretty`:
  still returns `blocked_not_release`, with `m7_qualified_release_rows: 8`.
- `C:\Python311\python.exe scripts\run_test_matrix.py --group v3_rebuild`:
  74 modules / 353 tests passed. The captured result is
  `docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_aabb_native_query_handle_20260621.json`.

External AI review:

- Call-for-review packet:
  `docs/reviews/call_for_review_phoenix_v3_aabb_native_query_handle_evidence_2026-06-21.md`.
- Gemini attempt failed with unsupported-client authentication:
  `docs/reviews/gemini_phoenix_v3_aabb_native_query_handle_evidence_review_2026-06-21.stderr.txt`.
- Local Linux `192.168.1.20` was reachable as `lx1`, but no `claude` or
  `gemini` executable was found in the checked PATH.
- Blocked review note:
  `docs/reviews/external_ai_blocked_phoenix_v3_aabb_native_query_handle_evidence_2026-06-21.md`.

## Goal-Level Decision Self-Audit - AABB Native Query-Handle Evidence

Decision: record native prepared-query handle reuse as a real M7 candidate
pending external review, not as an already promoted V3 row.

1. Was I foolish?
   No. The work addressed the measured generic bottleneck and cleared the
   predeclared material wall floor on two serious rows.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to promote it immediately
   without external review, or to call it Contact Manifold/full-solver/broad
   V3-over-V2 proof.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. I could have abandoned AABB after the query-cache no-go, but the
   evidence pointed directly at native query lifetime; fixing that produced the
   material change.
4. Can I now try a different path that actually solves the problem?
   Yes. Keep this packet behind external review, and apply the same generic
   engine discipline to RTNN wall path and Spatial topology-stream
   author-basis/wording closure instead of tuning apps one by one. Barnes-Hut
   vector accumulation remains future research unless a reviewed hierarchical
   traversal design reopens it.

## Latest RTNN Generic OptiX CUBIN Cache Update

After the AABB native query-handle pass, the RTNN `ranked_summary` wall-path
blocker was checked on the same RTX 4000 Ada POD. The important diagnosis was
generic, not RTNN-specific: the first new process paid a large OptiX CUBIN
compile/module preparation cost. The implementation now adds a content-addressed
OptiX CUBIN disk cache in the generic OptiX backend, controlled by
`RTDL_OPTIX_CUBIN_CACHE_DIR` and `RTDL_OPTIX_DISABLE_CUBIN_CACHE`.

Evidence:

- Packet:
  `docs/rebuild/v3/phoenix_v3_rtnn_optix_cubin_cache_evidence_2026-06-21.md`
- Raw POD evidence:
  `docs/rebuild/v3/evidence/rtnn_cubin_cache_20260621/`
- Cache artifact:
  `docs/rebuild/v3/evidence/rtnn_cubin_cache_20260621/cache/frn3d_grid_kernel.cu.sm_89.7dc0d93402fa3efd.cubin`

Result on the serious 1,048,576-point repeat5 RTNN evidence harness:

- Cold OptiX execution prepare: `3.337s`.
- Warm-cache OptiX execution prepare: `0.564s`.
- Prepare reduction: `5.914x`.
- Cold-plus-query reduction versus cold OptiX: `2.056x`.
- Runner-wall reduction versus cold OptiX: `1.785x`.
- Warm OptiX/CuPy hot-query speedup: `7.740x`.
- Warm OptiX/CuPy cold-plus-query speedup: `0.794x`.
- Warm OptiX/CuPy runner-wall speedup: `1.098x`.

Interpretation:

- This is real V3 engine progress: a reusable OptiX backend cost was reduced.
- This is not an M7 row and not a public RTNN speedup claim. The warm-cache
  runner-wall ratio is only `1.098x`, below the `2.0x` material floor, and
  cold-plus-query still loses to CuPy at `0.794x`.
- The next legitimate RTNN work is still generic: input-pack/device-column
  reuse or persistent prepared-session amortization. Do not tune RTNN-specific
  logic to manufacture a benchmark win.

Verification after this update:

- POD `make -C /root/phoenix_v3_work/current_aabb_20260621 build-optix
  OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0`: passed.
- POD cold-cache OptiX-only run populated the CUBIN cache and recorded
  `execution_prepare_sec: 3.3368102610111237`.
- POD warm-cache same-contract OptiX/CuPy run completed with parity and recorded
  `rtdl_optix_over_cupy_grid_runner_wall_speedup: 1.0982908717463347`.
- `py -3 -m unittest tests.v3_phoenix_optix_cubin_cache_test
  tests.v3_phoenix_rtnn_cubin_cache_evidence_test
  tests.v3_phoenix_next_engine_work_queue_test
  tests.v3_phoenix_release_readiness_gate_test`: 18 tests passed.
- `py -3 scripts\v3_phoenix_next_engine_work_queue.py --pretty`: passed with
  `rtnn_cubin_cache_evidence_not_m7: true`.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`: still returns
  `blocked_not_release`.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: 76 modules / 362
  tests passed after adding the CUBIN cache evidence tests.

## Goal-Level Decision Self-Audit - RTNN OptiX CUBIN Cache

Decision: record the generic OptiX CUBIN cache as real blocker reduction, but
keep RTNN `ranked_summary` out of M7 because material wall speed is still
missing.

1. Was I foolish?
   No. The decision separates a reusable backend improvement from a release
   claim.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to treat the `7.740x` hot-query
   result or `1.098x` runner-wall result as a V3 win while cold-plus-query still
   loses.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. I could have tuned RTNN-specific code or polished docs, but that would
   not have attacked the measured generic OptiX startup blocker.
4. Can I now try a different path that actually solves the problem?
   Yes. Use the cache result as a stepping stone and work on reusable input-pack
   or prepared-session amortization before asking for M7 review.

## Latest Verification - RTNN Self-Query Graph And Current Phoenix Answer

The newest RTNN work added a generic prepared self-query CUDA graph replay route
for fixed-radius ranked-summary aggregation and removed the stale native graph
query cap of 65,536 rows. This is V3 engine work, not RTNN app tuning: the route
lets a prepared search handle serve as its own query source and records
`prepared_search_as_query_points` metadata.

Evidence:

- Evidence packet:
  `docs/rebuild/v3/phoenix_v3_rtnn_self_query_graph_evidence_2026-06-21.md`
- Raw POD evidence:
  `docs/rebuild/v3/evidence/rtnn_self_query_graph_20260621/`
- Queue packet:
  `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`

Result on the serious 1,048,576-point same-contract RTNN harness:

- Direct self-query batch cold-plus-query: about `0.5516s`.
- Self-query graph cold-plus-query: about `0.5446s`.
- Graph/direct cold-plus-query ratio: about `1.013x`.
- Same-contract parity: passed.
- Prepared-search-as-query residency: recorded.
- M7 rows added: `0`.

Interpretation:

- This is a valid generic V3 engine surface: the old 65,536 graph cap is gone
  and the route works at million-row scale with parity.
- This is not a meaningful performance breakthrough. `1.013x` is exactly the
  kind of small result that Phoenix must not dress up as a V3 win.
- The remaining RTNN performance blocker is still generic: file/column
  ingestion, input-pack cost, or prepared-session amortization. Do not tune
  RTNN-specific logic just to manufacture an app win.

Current direct answer to the V3 status question:

- We are building V3, not individual apps. The apps are evidence harnesses.
- There is real V3 technical progress versus v2.x, but not enough yet for a
  broad "V3 is faster than V2" claim.
- The strongest accepted non-1.01x progress is still row-scoped and generic:
  grouped-reduction device-column preparation, AABB candidate-stream rows,
  RTDBSCAN component-signature rows, Triangle prepared graph, Hausdorff
  threshold-summary, and Robot Collision collision-flag stream.
- The current RTNN graph result is not a performance win; it is a functional
  engine capability and a guardrail against overclaiming.
- Phoenix V3 still depends on the current work. It is not merely micro polish
  over an already complete release, because the aggregate release gate remains
  blocked and the generic-engine queue is still open.

Latest verification after this update:

- `py -3 -m unittest tests.v3_phoenix_next_engine_work_queue_test
  tests.v3_phoenix_rtnn_self_query_graph_evidence_test
  tests.v3_phoenix_rtnn_self_query_aggregate_test`: 13 tests passed.
- `$env:PYTHONPATH='src;.'; py -3 -m unittest
  tests.goal2825_rtnn_cuda_graph_replay_prepared_batch_test
  tests.goal4504_v3_0_m108_execution_path_policy_refresh_test`: 9 tests
  passed.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: 84 modules / 397
  tests passed.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`: returned
  `blocked_not_release`, `failed_checks: []`, `m7_qualified_release_rows: 8`,
  and kept `broad_v3_faster_than_v2_claim_authorized: false`.

Major remaining steps:

1. Close or reject the AABB native prepared-query handle candidate with
   external/2-AI review and stable row wording.
2. Continue RTNN only on reusable wall-path blockers: input-pack/device-column
   residency or prepared-session amortization.
3. Keep Spatial RayJoin exact-f64 scalar-count behind review/adverse-subset and
   author-baseline gates.
4. Keep Barnes-Hut/vector-accumulation as a future-research record unless a
   reviewed hierarchical traversal design is available; do not promote
   Barnes-Hut app-specific or naive all-node OptiX evidence.
5. Close release infrastructure blockers: general install story, secondary
   RT-core performance confirmation, and release-readiness consensus.

## Goal-Level Decision Self-Audit - RTNN Self-Query Graph

Decision: record the million-row RTNN self-query graph route as functional
generic engine progress and explicitly block M7/performance wording because the
material speedup floor is not met.

1. Was I foolish?
   No. The work removed a stale graph cap and proved same-contract million-row
   graph execution, while refusing to call `1.013x` a V3 win.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to publish the graph/direct
   `1.013x` ratio as a breakthrough or hide it inside broad RTNN/V3 wording.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. I could have skipped graph replay and moved directly to input-pack
   residency, but removing the cap clarified that graph replay alone is not the
   RTNN wall-time answer.
4. Can I now try a different path that actually solves the problem?
   Yes. The next RTNN work should target reusable input/column residency or
   persistent prepared-session amortization, and the broader Phoenix queue
   should prioritize candidates that can clear material wall-time floors.

## Latest Verification - AABB Native Query-Handle Stable Row Preparation

After the RTNN graph check, the next closest Phoenix V3 M7 candidate remains
AABB `aabb_candidate_stream` native prepared-query-handle reuse. The material
candidate evidence is unchanged:

- 32,768 AABBs, jittered_grid, repeat50:
  `1.719x` OptiX/Embree cold-plus-collect wall speedup.
- 65,536 AABBs, jittered_grid, repeat50:
  `1.637x` OptiX/Embree cold-plus-collect wall speedup.
- Raw AABB oracle, source-manifest provenance, fail-closed overflow, and
  fresh-run stability are already recorded.

New local closure:

- Packet:
  `docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_row_wording_gate_2026-06-21.md`
- Stable candidate row IDs now exist:
  `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50`
  and
  `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50`.
- The wording in this packet is draft-only and explicitly not publishable
  before external review.
- M7 rows added: `0`.
- Public speedup, broad AABB, Contact Manifold solver, release, and V3-over-V2
  wording remain unauthorized.

External review status:

- A fresh Gemini final-review attempt was made and captured here:
  `docs/reviews/gemini_phoenix_v3_aabb_native_query_handle_final_review_2026-06-21.md`.
- It failed with `IneligibleTierError` / `UNSUPPORTED_CLIENT`, so it is not an
  external review verdict.
- Blocked note:
  `docs/reviews/external_ai_blocked_phoenix_v3_aabb_native_query_handle_final_review_2026-06-21.md`.
- Local Linux `192.168.1.20` was reachable, but no `claude` or `gemini`
  executable was found in PATH during this check.

Updated gate interpretation:

- `docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_review_gate_2026-06-21.md`
  still returns `aabb_native_query_handle_review_blocked_not_m7`.
- The stable-row-id blocker is locally closed.
- Remaining blockers are:
  `external_ai_review_missing`,
  `codex_consensus_response_missing_after_external_review`, and
  `external_public_wording_review_missing`.

Latest verification after this update:

- `py -3 -m unittest tests.v3_phoenix_aabb_native_query_handle_row_wording_gate_test
  tests.v3_phoenix_aabb_native_query_handle_review_gate_test`: 11 tests passed.
- `py -3 -m unittest tests.v3_phoenix_next_engine_work_queue_test
  tests.v3_phoenix_aabb_native_query_handle_row_wording_gate_test
  tests.v3_phoenix_aabb_native_query_handle_review_gate_test`: 17 tests passed.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: 85 modules / 402
  tests passed.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`: returned
  `blocked_not_release`, `failed_checks: []`, `m7_qualified_release_rows: 8`,
  and `broad_v3_faster_than_v2_claim_authorized: false`.

## Goal-Level Decision Self-Audit - AABB Stable Row Preparation

Decision: close only the AABB native-query-handle stable-row-id preparation gap
while keeping M7 promotion blocked on true external review.

1. Was I foolish?
   No. This turns an avoidable local blocker into machine-checked candidate row
   identities without pretending release review exists.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish actions would be counting Gemini's auth failure
   as a review, using Codex subagent output as the external AI, or publishing
   the draft row wording.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. I could have moved directly to RTNN input residency or Spatial
   adverse-subset review, but AABB had a near-M7 local blocker that could be
   closed safely.
4. Can I now try a different path that actually solves the problem?
   Yes. Keep AABB blocked on true external AI review, and continue the
   generic-engine queue without broad release claims.

## Latest Verification - Spatial Exact-F64 Adverse-Subset Closure

Phoenix now records a focused Spatial RayJoin adverse-subset parity closure for
the exact-f64 relation-status scalar-count route.

New evidence and packets:

- POD raw evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_exact_f64_adverse_subset_20260621/br_county_subset_relation_status_exact_f64_r20_s5.json`
- Intake packet:
  `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_adverse_subset_2026-06-21.md`
- Updated review gate:
  `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_review_gate_2026-06-21.md`
- Updated queue:
  `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`

Result:

- Dataset: `tests/fixtures/rayjoin/br_county_subset.cdb`.
- Count mode: `relation_status_corrected_executor_validated`.
- Query repeat: `20`; sample repeat: `5`.
- Row count: `6`; row count remained consistent.
- Full M3 table was present.
- Query stream residency remained
  `device_resident_prepared_point_probe_columns_with_reusable_relation_status_corrected_executor`.
- M7 rows added: `0`.
- Release, public speedup, broad V3-over-V2, RayJoin-author, paper, and true
  zero-copy claims remain unauthorized.

Updated gate interpretation:

- `adverse_subset_parity_missing` is no longer a Spatial exact-f64 blocker.
- The route remains `spatial_rayjoin_relation_status_exact_f64_review_blocked_not_m7`.
- Remaining blockers are:
  `external_ai_review_missing`,
  `codex_consensus_response_missing_after_external_review`,
  `same_dataset_rayjoin_author_timing_basis_missing`,
  `route_name_semantically_stale_relation_status_corrected`, and
  `public_wording_review_missing`.

Latest verification after this update:

- `py -3 -m unittest tests.v3_phoenix_spatial_rayjoin_relation_status_exact_f64_adverse_subset_test tests.v3_phoenix_spatial_rayjoin_relation_status_exact_f64_review_gate_test tests.v3_phoenix_next_engine_work_queue_test`:
  15 tests passed.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: 86 modules / 406
  tests passed.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`: returned
  `blocked_not_release`, `failed_checks: []`, `m7_qualified_release_rows: 8`,
  and `broad_v3_faster_than_v2_claim_authorized: false`.

## Current Phoenix V3 High-Level Answer

We are building V3, not individual apps. The benchmark apps are evidence
harnesses for reusable engine capabilities.

Current truth:

- V3 is not release-ready and cannot honestly claim broad V3-over-V2 speedup.
- The current work is not cosmetic polish. It is converting old route
  experiments into reusable engine capabilities with gates, evidence, and
  anti-overclaim wording.
- The material candidates are real but narrow:
  grouped reduction has two supplemental M7 rows; AABB native query handle has
  1.6x-1.7x candidate evidence but still lacks external review; Spatial
  exact-f64 has a 3.680x internal executor improvement and now passes the
  adverse subset, but still lacks author-basis and external review; RTNN has
  strong hot-path evidence but wall-time gates still block promotion.
- A 1.01x-style result does not qualify as a Phoenix V3 performance win.

## Goal-Level Decision Self-Audit - Spatial Adverse-Subset Closure

Decision: close only the Spatial exact-f64 adverse-subset parity blocker while
keeping M7 promotion and release blocked.

1. Was I foolish?
   No. The decision adds correctness evidence to a generic point-location route
   without promoting it.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish actions would be treating the tiny subset as a
   speed claim, calling it a RayJoin comparison, or counting it as release
   readiness.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. I could have moved directly to RTNN ingestion or AABB external review,
   but Spatial had a clear local blocker that could be closed safely.
4. Can I now try a different path that actually solves the problem?
   Yes. Keep Spatial behind external-review, author-basis, and wording gates;
   continue Phoenix on the generic-engine queue instead of app-specific tuning.

## Latest Verification - AABB Final External Review Request Prepared

Phoenix now has a concise final external-review request for the AABB native
query-handle candidate:

- `docs/reviews/call_for_review_phoenix_v3_aabb_native_query_handle_final_m7_review_2026-06-21.md`

It asks an external Claude/Gemini reviewer to decide whether exactly two stable
row-scoped IDs may be promoted:

- `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50`
- `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50`

The review packet includes the current evidence:

- 32,768 row: `1.719x` OptiX/Embree cold-plus-collect wall speedup and
  `1.867x` query_total speedup.
- 65,536 row: `1.637x` OptiX/Embree cold-plus-collect wall speedup and
  `1.743x` query_total speedup.
- Six fresh POD runs preserve the material floor; weakest fresh
  cold-plus-collect wall speedup is `1.644x`.
- Raw Embree/OptiX AABB rows match an independent closed-boundary CPU oracle.
- OptiX low-capacity overflow is fail-closed.
- Source-manifest provenance is recorded with SHA-256
  `f7d8a0ae6e39c691bf7c949b23741181abcc24fc3e3ef405f73c7a113d1e4422`.

External review attempt status:

- `docs/reviews/external_ai_blocked_phoenix_v3_aabb_native_query_handle_final_m7_review_2026-06-21.md`
  records the latest tool blockage.
- Windows PATH has Gemini but no `claude`.
- Windows Gemini remains blocked by `IneligibleTierError` /
  `UNSUPPORTED_CLIENT`.
- `npx -y @anthropic-ai/claude-code --version` found package version
  `2.1.185`, but the downloaded Windows `claude.exe` is incompatible with this
  Windows version.
- `ssh 192.168.1.20` reaches `lx1`, but `claude`, `gemini`, `node`, `npm`,
  and `npx` are not in PATH there.
- Chrome/Claude GUI automation is blocked because Chrome is not running and the
  selected Chrome `Default` profile does not have the Codex Chrome Extension
  installed/enabled. The native host manifest is correct. Per plugin rules, no
  Chrome launch or extension repair was attempted without explicit permission.

Current gate interpretation:

- `docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_review_gate_2026-06-21.md`
  still returns `aabb_native_query_handle_review_blocked_not_m7`.
- `m7_promotion_authorized` remains `false`.
- `m7_qualified_release_rows_added` remains `0`.
- `release_authorized` remains `false`.
- The only remaining AABB blockers are still true external review, Codex
  consensus after that review, and external public wording review.

Latest local verification for this update:

- `py -3 -m unittest tests.v3_phoenix_aabb_native_query_handle_review_gate_test
  tests.v3_phoenix_next_engine_work_queue_test`: 12 tests passed.

## Goal-Level Decision Self-Audit - AABB External Review Blockage

Decision: record the final AABB external-review request and tool blockage
instead of treating failed Claude/Gemini/Chrome routes as review.

1. Was I foolish?
   No. AABB remains the closest material reusable M7 candidate, and the final
   review packet is now ready for a real external reviewer.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to count missing CLIs,
   unsupported Gemini, incompatible Claude Code, or unavailable Chrome
   extension as an approval.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. Continue RTNN ingestion or Spatial author/wording-gate work while AABB
   waits for external review; Barnes-Hut vector accumulation is no longer a
   current Phoenix P0 switch target.
4. Can I now try a different path that actually solves the problem?
   Yes. Keep AABB blocked/not-M7, preserve the final review request, and
   continue local generic-engine work without weakening the 2-AI rule.

## Latest Verification - RTNN Column-Source Runner Repair

Phoenix RTNN wall-path work is now a real runner surface, not just prose:

- `scripts/goal2348_rtnn_v2_2_external_runner.py` now reads
  `point_column_source=csv|numpy_csv|npz` for both RTDL OptiX and CuPy grid
  reference routes.
- The CuPy references now build point arrays through vectorized NumPy column
  stacking instead of `list(zip(...))`, so the reference is not polluted by
  Python object conversion.
- `scripts/v3_phoenix_rtnn_full_batch_float32_same_contract_runner.py` now
  passes the point manifest into the real `run_route` function. Before this
  repair, a non-dry-run POD execution with `point_column_file` would have hit a
  `NameError`.
- `docs/rebuild/v3/phoenix_v3_rtnn_column_source_residency_gap_2026-06-21.md`
  now records the stricter gate: the NPZ route is implemented and locally
  tested, but it is still not M7 and not a public speedup claim until a fresh
  same-hardware POD rerun clears parity plus cold/runner material floors.
- `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`
  was regenerated with the RTNN column-source gate.

Current RTNN truth remains unchanged and deliberately conservative:

- Existing prepared self-query hot-query speedup over CuPy grid: `19.437x`.
- Existing cold-plus-query speedup: `1.214x`.
- Existing runner-wall speedup: `1.030x`.
- Input load is `72.814%` of the runner wall.
- This is a blocker, not a V3 success claim.

Latest local verification:

- `py -3 -m unittest tests.v3_phoenix_rtnn_full_batch_float32_same_contract_runner_test tests.v3_phoenix_rtnn_column_source_residency_gap_test tests.v3_phoenix_next_engine_work_queue_test`:
  16 tests passed.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: 87 modules / 412
  tests passed.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`: returned
  `blocked_not_release`, `failed_checks: []`, `m7_qualified_release_rows: 8`,
  and `broad_v3_faster_than_v2_claim_authorized: false`.

Historical readiness blockers active at that point:

- `eight_row_surface_still_too_narrow_for_major_release`
- `broad_v3_faster_than_v2_claim_not_authorized`
- `general_release_installer_not_ready`
- `secondary_rt_performance_confirmation_not_closed`
- `generic_engine_work_queue_open`
- `external_release_readiness_consensus_blocks_major_release_wording`

Current superseding blocker name after the eleven-row Claude+Codex review:

- `current_eleven_row_release_readiness_consensus_blocks_release`

Next hardware action:

Run the serious same-contract RTNN runner on the RTX POD with
`--point-column-source npz`, save OptiX/CuPy payloads plus `summary.json`,
`environment.json`, and `point_manifest.json`, then intake the result without
promoting it unless cold-plus-query and runner-wall speedups clear the material
floor and review gates.

## Goal-Level Decision Self-Audit - RTNN Runner Repair Before POD

Decision: repair and locally gate the RTNN NPZ column-source runner before
spending POD time on the rerun.

1. Was I foolish?
   No. The real runner path had an untested `point_manifest` dependency and the
   CuPy reference had stale CSV/list conversion paths, so running POD first
   would have produced either a failure or weak evidence.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would have been to treat dry-run success
   as proof that the serious route could execute.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. I could have switched to AABB external review or Spatial author-basis
   work, but that would not close the RTNN wall-path blocker that is locally
   actionable.
4. Can I now try a different path that actually solves the problem?
   Yes. The route is now ready for the same-hardware POD rerun; if NPZ input
   still leaves runner-wall speed near neutral, the next path is deeper
   prepared-search/input residency or a different P0 generic engine item, not
   public RTNN wording.

## Latest POD Evidence - RTNN NPZ + CUBIN Cache

The same-hardware RTX POD rerun is now complete and recorded locally:

- Evidence root:
  `docs/rebuild/v3/evidence/phoenix_v3_rtnn_npz_cubin_cache_1048576_r5_20260621/`
- Intake packet:
  `docs/rebuild/v3/phoenix_v3_rtnn_npz_cubin_cache_evidence_2026-06-21.md`
- Work queue:
  `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`

What improved:

- NPZ column-source input is real on both RTDL OptiX and CuPy grid routes.
- Same-contract parity holds:
  row count, bounded-neighbor count, nearest checksum, and kth checksum match;
  sum-distance relative error is `1.207e-10`.
- Without CUBIN cache, NPZ alone removed the input-load blocker but OptiX still
  lost full runner wall at `0.312x` because execution prepare was about
  `3.007s`.
- With NPZ plus the generic OptiX CUBIN cache, execution prepare dropped to
  `0.226764s`.
- The warm route reached:
  `7.784x` hot-query speedup, `1.247x` cold-plus-query speedup, and `1.328x`
  runner-wall speedup versus the same-contract CuPy grid reference.

Interpretation:

- This is real V3 engine progress: input-column ingestion plus CUBIN cache turn
  RTNN from wall-time regression into a positive full-run result.
- It is still not M7 and not release/public wording: `1.328x` runner wall and
  `1.247x` cold-plus-query are below the `2.0x` Phoenix material floor.
- Remaining blocker: warm OptiX non-hot time is still `0.459455s`, about
  `42.420x` the hot query. The next reusable work is prepared-session
  amortization or device-column pack reuse, not RTNN-specific app tuning.

Latest local verification:

- `py -3 -m unittest tests.v3_phoenix_rtnn_npz_cubin_cache_evidence_test`:
  5 tests passed.
- `py -3 -m unittest tests.v3_phoenix_next_engine_work_queue_test
  tests.v3_phoenix_rtnn_npz_cubin_cache_evidence_test`: 11 tests passed.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: 88 modules / 417
  tests passed.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`: still
  returned `blocked_not_release`, `failed_checks: []`,
  `m7_qualified_release_rows: 8`, and
  `broad_v3_faster_than_v2_claim_authorized: false`.

## Goal-Level Decision Self-Audit - RTNN NPZ+CUBIN Result

Decision: record NPZ+CUBIN as a real generic V3 blocker reduction, but keep
RTNN out of M7 and keep V3 release blocked.

1. Was I foolish?
   No. The POD result is positive but below the material floor, so the correct
   action is to record progress without promotion.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be claiming `1.328x` runner wall or
   `7.784x` hot-query as a release-grade RTNN win.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. I could switch to AABB external review or Spatial author-basis work,
   but this run was the right closure for the RTNN NPZ rerun gate.
4. Can I now try a different path that actually solves the problem?
   Yes. Either continue RTNN only through reusable prepared-session/input-pack
   amortization, or move to another P0 generic engine item if RTNN remains below
   floor after this blocker reduction.

## Latest POD Evidence - RTNN Prepared Repeat50 Amortization

Phoenix now has a scoped RTNN prepared-session candidate, still not promoted:

- Intake packet:
  `docs/rebuild/v3/phoenix_v3_rtnn_prepared_repeat50_amortization_evidence_2026-06-21.md`
- Evidence root:
  `docs/rebuild/v3/evidence/phoenix_v3_rtnn_npz_cubin_repeat50_1048576_20260621/`
- Review request:
  `docs/reviews/call_for_review_phoenix_v3_rtnn_prepared_repeat50_amortization_2026-06-21.md`
- External review blocked record:
  `docs/reviews/external_review_blocked_phoenix_v3_rtnn_prepared_repeat50_amortization_2026-06-21.md`

Candidate row:

- `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02`

Observed POD facts:

- Same hardware: RTX 4000 Ada.
- Point count: `1,048,576`.
- Repeat count: `50`.
- Point source: `npz` on both RTDL OptiX and CuPy grid.
- Same-contract parity holds; sum-distance relative error is `1.207e-10`.
- RTDL OptiX/CuPy grid hot-query speedup: `7.889x`.
- RTDL OptiX/CuPy grid cold-plus-query speedup: `1.315x`.
- RTDL OptiX/CuPy grid runner-wall speedup: `3.761x`.

Interpretation:

- This is the first current RTNN evidence row that clears the Phoenix `2.0x`
  runner-wall material floor.
- It is scoped to prepared repeated-session amortization only.
- It is not a one-shot RTNN speedup, not whole-RTNN, not paper-equivalent, not
  V3 release authorization, and not broad V3-over-V2 wording.
- `m7_reopen_candidate_pending_2ai_review` is `true`, but
  `m7_promotion_authorized` remains `false` and M7 rows added remains `0`.

External review status:

- Windows Gemini retry failed with `IneligibleTierError` /
  `UNSUPPORTED_CLIENT`.
- No Claude/Gemini verdict exists yet.
- No 2-AI consensus exists yet.

Latest local verification:

- `py -3 -m unittest tests.v3_phoenix_rtnn_prepared_repeat50_amortization_evidence_test`:
  5 tests passed.
- `py -3 -m unittest tests.v3_phoenix_rtnn_prepared_repeat50_amortization_evidence_test
  tests.v3_phoenix_next_engine_work_queue_test`: 11 tests passed.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: 89 modules / 423
  tests passed.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`: still
  returned `blocked_not_release`, `failed_checks: []`,
  `m7_qualified_release_rows: 8`, and
  `broad_v3_faster_than_v2_claim_authorized: false`.

## Goal-Level Decision Self-Audit - RTNN Repeat50 Candidate

Decision: record RTNN repeat50 prepared-session amortization as a material M7
candidate pending external review, not as promotion.

1. Was I foolish?
   No. The result matches the V3 prepared-execution thesis and clears runner
   wall materially, while preserving the one-shot/cold-start boundary.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be calling it a whole RTNN or
   release-grade win before external review.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. I could have waited on AABB review or continued RTNN one-shot overhead,
   but repeat50 directly tests V3's reusable prepared-session value.
4. Can I now try a different path that actually solves the problem?
   Yes. Send the exact row for external review when a real Claude/Gemini route
   is available; meanwhile keep it pending and continue other P0 generic-engine
   blockers without weakening the review rule.

## Latest Verification - Queue/M7 Packet Reconciliation And Spatial Author Basis

This pass corrected a stale Phoenix state conflict and hardened the Spatial
RayJoin author-basis blocker. A later same-dataset author run changed the
Spatial blocker from "author basis missing" to "author basis present but
unfavorable/not-M7."

Changes recorded:

- `scripts/v3_phoenix_m7_row_classification_packet.py` now records the current
  next-engine queue explicitly: active P0 items are RTNN ranked-summary wall
  path, AABB prepared-query-handle review closure, and Spatial topology-stream
  author-basis/wording closure.
- The M7 classification packet now records Barnes-Hut/vector accumulation as
  `covered_by_m6_focused_evidence_future_research_not_current_p0`, not active
  Phoenix P0 work.
- `scripts/v3_phoenix_spatial_rayjoin_author_basis_same_county.py` records a
  same-dataset RayJoin author timing packet for
  `br_county.cdb`/`br_county.cdb`, repeat=50/warmup=5.
- The RayJoin author `query_exec` run reports `Query: 1.865660 ms` over
  OptiX launch width `342738`; the current RTDL exact-f64 prepared-query median
  is `6.309319 ms`, so the author Query timer is about `3.383x` faster than
  the RTDL candidate on this scoped comparison.
- The author binary did not print an author result count in this run, so
  author count parity is not verified.
- `scripts/v3_phoenix_spatial_rayjoin_relation_status_exact_f64_review_gate.py`
  now records `author_timing_basis.status:
  present_but_not_m7_author_query_faster_count_not_printed`.
- `scripts/v3_phoenix_next_engine_work_queue.py` now checks
  `spatial_relation_status_exact_f64_author_basis_present_not_m7`, so the
  global queue fails if this unfavorable evidence is accidentally turned into
  an unsupported Spatial/RayJoin speedup claim.

Latest verification:

- `py -3 scripts\v3_phoenix_spatial_rayjoin_author_basis_same_county.py`:
  `spatial_rayjoin_same_county_author_timing_present_not_m7`,
  `failed_checks: []`.
- `py -3 scripts\v3_phoenix_spatial_rayjoin_relation_status_exact_f64_review_gate.py`:
  `spatial_rayjoin_relation_status_exact_f64_review_blocked_not_m7`,
  `failed_checks: []`.
- `py -3 scripts\v3_phoenix_next_engine_work_queue.py --json-out
  docs\rebuild\v3\phoenix_v3_next_generic_engine_work_queue_2026-06-21.json
  --md-out
  docs\rebuild\v3\phoenix_v3_next_generic_engine_work_queue_2026-06-21.md
  --pretty`: `active_generic_engine_work_queue_not_release`,
  `failed_checks: []`.
- `py -3 -m unittest tests.v3_phoenix_spatial_rayjoin_author_basis_same_county_test
  tests.v3_phoenix_spatial_rayjoin_relation_status_exact_f64_review_gate_test
  tests.v3_phoenix_next_engine_work_queue_test
  tests.v3_release_wording_gate_test`: 19 tests passed.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`: still returns
  `blocked_not_release`, `failed_checks: []`,
  `m7_qualified_release_rows: 8`, and
  `broad_v3_faster_than_v2_claim_authorized: false`.

## Goal-Level Decision Self-Audit - Spatial Author-Basis Gate

Decision: make the Spatial exact-f64 same-dataset author comparison
machine-checkable and keep it blocked because the author Query timer is faster
than the current RTDL exact-f64 candidate and author result-count parity is not
printed.

1. Was I foolish?
   No. This prevents a correctness repair and internal RTDL-vs-RTDL speedup
   from being mistaken for a user-facing Spatial/RayJoin win.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to hide the unfavorable
   same-dataset author timing or call the current exact-f64 repair an M7
   performance row anyway.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. I could have skipped the author binary comparison and continued RTDL
   tuning, but that would leave the project vulnerable to another unsupported
   Spatial promotion.
4. Can I now try a different path that actually solves the problem?
   Yes. Keep Spatial blocked until a reviewed route can beat the relevant
   author baseline with count parity, external review, and public wording
   review; continue Phoenix through RTNN/AABB generic-engine candidates without
   broad V3-over-V2 or app-specific claims.

## Current User-Level Status Question - V3 Or App Work

Answer: Phoenix is building a V3 engine surface, not developing unrelated
apps. The benchmark apps are evidence harnesses. A result counts only if it
demonstrates a reusable engine capability such as prepared execution,
device-column input preparation, reusable native query handles, candidate
streaming, graph/chunk reuse, same-stream accounting, or same-contract
continuation.

What is real V3 technical progress over V2.x:

- `grouped_reduction` device-column preparation is a real generic input-path
  optimization: the engine can prepare ray batches from CuPy device columns
  instead of host-packed ray materialization, while preserving the grouped_sum
  contract and CPU parity. The accepted scoped rows show `3.599x` and
  `73.586x` host-packed/device-column OptiX cold-plus-loop speedups.
- AABB native query-handle reuse is now a real generic prepared-handle M7
  closure: Claude external review plus Codex consensus accepted exactly two
  row-scoped jittered-grid range-intersection rows with `1.719x` and `1.637x`
  cold-plus-collect wall speedups. OptiX prepare alone remains slower than
  Embree, so no prepare-only, Contact Manifold, broad AABB, or V3-over-V2
  claim is allowed.
- RTNN prepared repeated-session amortization is a real generic prepared-session
  candidate: repeat=50 shows `3.761x` runner-wall speedup versus CuPy grid, but
  it is still not M7 until review and scope wording close.
- Spatial RayJoin exact-f64 repair is real correctness/engine accounting work,
  not a performance win: same-dataset RayJoin author Query is about `3.383x`
  faster than the current RTDL exact-f64 prepared-query median, so Spatial
  remains blocked.

What is not yet true:

- No broad V3-over-V2 speedup claim is authorized.
- No whole-app speedup claim is authorized.
- No release claim is authorized from green tests alone.
- No 1.01x-style improvement can qualify as a Phoenix performance win.

Therefore the current work is not tiny polish. The already accepted eleven M7
rows are the foundation, and the active generic-engine queue is now closed, but
Phoenix V3 still depends on current work to turn a narrow row-scoped surface
into a responsible major-version performance surface. The next release-relevant
work is release authorization, broader surface judgment, installer and
reproducibility closure, secondary RT performance confirmation, and external
release-readiness consensus. Spatial remains future research unless it beats
the author baseline with verified parity.

Latest verification:

- `py -3 -m unittest tests.v3_phoenix_spatial_rayjoin_author_basis_same_county_test
  tests.v3_phoenix_spatial_rayjoin_relation_status_exact_f64_review_gate_test
  tests.v3_phoenix_next_engine_work_queue_test
  tests.v3_release_wording_gate_test`: 19 tests passed.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: 90 modules / 430
  tests passed.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`:
  `blocked_not_release`, `failed_checks: []`, `m7_qualified_release_rows: 11`,
  `release_authorized: false`, and
  `broad_v3_faster_than_v2_claim_authorized: false`.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: 90 modules / 430
  tests passed.

## Latest Verification - AABB Native Query-Handle, RTNN Repeat50 Closure, And 11-Row Sync

AABB native prepared-query-handle reuse is now closed as row-scoped M7 evidence,
not an active P0 queue item:

- External review:
  `docs/reviews/claude_phoenix_v3_aabb_native_query_handle_final_m7_review_2026-06-21.md`
- Codex consensus:
  `docs/reviews/codex_phoenix_v3_aabb_native_query_handle_final_m7_review_2ai_consensus_2026-06-21.md`
- Review gate:
  `docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_review_gate_2026-06-21.md`
- M7 rows added: `2`
- Current total M7 row-scoped count after later RTNN and Spatial closure sync:
  `11`
- Active generic-engine queue after later Spatial closure sync: none.
  Barnes-Hut/vector accumulation and Spatial RayJoin topology-stream author-gap
  are future research records, not active Phoenix P0 work.
- Release status: `blocked_not_release`
- Broad V3-over-V2 speedup status: not authorized

Latest local verification:

- `py -3 -m unittest tests.v3_phoenix_aabb_native_query_handle_review_gate_test tests.v3_phoenix_m7_row_classification_packet_test tests.v3_phoenix_next_engine_work_queue_test`:
  23 tests passed.
- `py -3 -m unittest tests.v3_phoenix_release_readiness_gate_test tests.v3_release_wording_gate_test`:
  5 tests passed.
- `py -3 scripts\v3_release_wording_gate.py --pretty`: passed with no missing
  required strings and no violations.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`:
  `blocked_not_release`, `failed_checks: []`, `m7_qualified_release_rows: 11`,
  `release_authorized: false`, and
  `broad_v3_faster_than_v2_claim_authorized: false`.

## Goal-Level Decision Self-Audit - 11-Row Sync

Decision: accept the AABB native query-handle and RTNN prepared repeat50
closures into the global Phoenix surface and synchronize wording/readiness docs
to 11 rows while keeping release blocked.

1. Was I foolish?
   No. The change follows real Claude external review plus Codex consensus and
   keeps the exact-row, slower-prepare, and no-broad-claim limits visible.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to count the rows without
   updating public tutorials, or to treat 11 rows as release authorization.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. I could have left AABB or RTNN pending and moved to Spatial, but that
   would preserve stale blockers after review closure.
4. Can I now try a different path that actually solves the problem?
   Yes. Continue Phoenix through release-readiness blockers now that the active
   generic-engine queue is closed, while keeping Spatial future research until
   author-baseline parity/performance and wording gates close.

## Latest Supersession - Claude Path, Spatial Closure, Queue Closed

This section supersedes earlier same-day report text that said the generic
engine queue was open or that Spatial RayJoin was an active P0 item.

Current facts:

- Windows local Claude is verified and recorded in
  `docs/handoff/REFRESH_LOCAL_2026-04-13.md`:
  `C:\Users\Lestat\.local\bin\claude.exe`, version `2.1.170 (Claude Code)`.
  Future Windows Claude calls should use this hard path directly, not `npx`.
- Spatial RayJoin active P0 is closed to future research after Claude external
  review and Codex consensus:
  `docs/rebuild/v3/phoenix_v3_spatial_active_p0_closure_gate_2026-06-21.md`,
  `docs/reviews/claude_phoenix_v3_spatial_active_p0_closure_review_2026-06-21.md`,
  and
  `docs/reviews/codex_phoenix_v3_spatial_active_p0_closure_2ai_consensus_2026-06-21.md`.
- The generic-engine active queue is empty:
  `scripts/v3_phoenix_next_engine_work_queue.py --pretty` returns
  `generic_engine_work_queue_closed_not_release`.
- This closure does not authorize release, M7 promotion, a broad V3-over-V2
  speedup claim, a whole-app Spatial claim, or RTDL-beats-RayJoin wording.
- Release readiness remains blocked with `failed_checks: []` and these active
  blockers: release authorization false, eleven-row surface still too narrow
  for a major release, broad V3-faster-than-V2 claim not authorized, general
  release installer not ready, secondary RT performance confirmation not
  closed, and external release-readiness consensus still blocking
  major-release wording.

Latest verification:

- `& 'C:\Users\Lestat\.local\bin\claude.exe' --print --dangerously-skip-permissions 'Return exactly: CLAUDE_OK'`:
  `CLAUDE_OK`.
- `py -3 scripts\v3_release_wording_gate.py --pretty`: passed with no missing
  required strings and no violations.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`: returned
  `blocked_not_release`, `failed_checks: []`, `m7_qualified_release_rows: 11`,
  and `broad_v3_faster_than_v2_claim_authorized: false`.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: passed 91 modules /
  436 tests.

## Goal-Level Decision Self-Audit - Record Claude Path And Close Queue Supersession

Decision: record the verified Windows Claude path in refresh memory and
supersede stale queue-open status text with the current Spatial-closed,
queue-empty, release-blocked state.

1. Was I foolish?
   No. The action fixes a repeated setup failure mode by making the working
   Claude path durable and checked.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to keep relying on transient
   memory, PATH discovery, or `npx` after the repo had already observed the
   working hard path and the incompatible `npx` route.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. I could have used Gemini-only review whenever Claude was not found, but
   that would dodge the local Claude availability problem instead of solving it.
4. Can I now try a different path that actually solves the problem?
   Yes. Future external review calls on this Windows machine can directly use
   `C:\Users\Lestat\.local\bin\claude.exe`, while Phoenix work proceeds from
   the verified current state: active generic-engine queue closed, release still
   blocked.

## Latest Supersession - Eleven-Row Release-Readiness Review

Claude has now reviewed the current eleven-row, queue-closed Phoenix V3 state:

- Review request:
  `docs/reviews/call_for_review_phoenix_v3_eleven_row_release_readiness_2026-06-21.md`
- Claude review:
  `docs/reviews/claude_phoenix_v3_eleven_row_release_readiness_review_2026-06-21.md`
- Codex consensus:
  `docs/reviews/codex_phoenix_v3_eleven_row_release_readiness_2ai_consensus_2026-06-21.md`

Verdict:

```text
not-release-ready-fix-p0
```

What changed:

- The old six-row factual state is superseded.
- The current facts are eleven exact row-scoped M7 rows, active generic-engine
  queue empty, and Spatial RayJoin future research.
- Claude and Codex agree no generic-engine work remains on the critical path
  for a scoped release review.

What did not change:

- Release remains unauthorized.
- Broad V3-over-V2 speedup remains unauthorized.
- Package-install wording remains unauthorized.
- Secondary RT-core performance confirmation remains unclosed.

Current aggregate gate blocker names:

```text
release_authorization_false
eleven_row_surface_still_too_narrow_for_major_release
broad_v3_faster_than_v2_claim_not_authorized
secondary_rt_performance_confirmation_not_closed
current_eleven_row_release_readiness_consensus_blocks_release
```

Latest verification:

- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`:
  `blocked_not_release`, `failed_checks: []`,
  `eleven_row_claude_review_verdict: not-release-ready-fix-p0`, and
  `eleven_row_consensus_status:
  claude_codex_consensus_current_eleven_row_not_release_ready_fix_p0`.
- `py -3 -m unittest tests.v3_phoenix_release_readiness_gate_test`: 3 tests
  passed.
- `py -3 scripts\v3_release_wording_gate.py --pretty`: passed.

## Goal-Level Decision Self-Audit - Eleven-Row Review Intake

Decision: Intake Claude's eleven-row release-readiness review and Codex
consensus as the current blocking release-readiness authority.

1. Was I foolish?
   No. This replaces stale six-row framing with the current eleven-row,
   queue-closed state while preserving the release block.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to treat the new review as
   approval because it praises row quality and queue closure.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. I could keep optimizing benchmark rows, but the current review says
   engine work is not on the critical path.
4. Can I now try a different path that actually solves the problem?
   Yes. The installer blocker is now scoped-closed; the next path is second
   RT-core evidence or hardware-scoped waiver, then a new aggregate
   release-readiness review.

## Latest Progress - Source-Tree / Pod-Gated Reproducibility Candidate

The installer/reproducibility blocker now has a concrete candidate artifact:

```text
docs/rebuild/v3/v3_source_tree_pod_gated_reproducibility_candidate_2026-06-21.md
```

This candidate is intentionally not a release installer. Claude reviewed it as
`approve-with-amendments-not-release`; Codex accepted that review after adding
the required Numba CUDA compiler-path exports. Its status is now:

```text
source_tree_pod_gated_candidate_reviewed_not_release
```

Gate behavior after this intake:

- `source_tree_pod_gated_candidate_present: true`
- `source_tree_pod_gated_candidate_reviewed: true`
- `source_tree_pod_gated_scoped_release_wording_reviewed: true`
- `release_scope: source_tree_pod_gated_eleven_row`
- `general_release_installer_ready: false`
- `package_install_claim_authorized: false`
- `installer_closes_release_blocker: true`
- `installer_closes_release_blocker_scope: source_tree_pod_gated_eleven_row`

This closes the installer/reproducibility blocker only under the reviewed
source-tree/pod-gated eleven-row scope. It still does not authorize release,
package-install wording, or a general installer.

Latest verification:

- `py -3 scripts\v3_phoenix_install_reproducibility_gate.py --pretty`:
  `staged_pod_gate_present_general_release_installer_not_ready`,
  `source_tree_pod_gated_candidate_present: true`,
  `source_tree_pod_gated_candidate_reviewed: true`,
  `installer_closes_release_blocker: true`.
- `py -3 scripts\v3_release_wording_gate.py --pretty`: passed after adding the
  candidate to the scanned current surface.
- `py -3 scripts\v3_phoenix_release_readiness_gate.py --pretty`:
  `blocked_not_release`, `failed_checks: []`.
- `py -3 scripts\run_test_matrix.py --group v3_rebuild`: passed 91 modules /
  437 tests.

## Goal-Level Decision Self-Audit - Reproducibility Candidate

Decision: apply Claude's P0 Numba export amendment, accept the source-tree /
pod-gated reproducibility candidate as reviewed, and keep the installer blocker
open.

1. Was I foolish?
   No. This records only the reviewed-candidate field and still refuses to call
   the staged pod gate a general installer.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to set
   `installer_closes_release_blocker: true`, `general_release_installer_ready:
   true`, or `release_authorized: true` because a candidate was reviewed.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. I could attempt a full package installer first, but the current evidence
   already supports a narrower source-tree/pod-gated candidate path that has now
   been reviewed.
4. Can I now try a different path that actually solves the problem?
   Yes. Next is a scoped release-wording review or general installer work for
   the remaining install P0, plus second RTX/RT-core evidence or a
   hardware-scoped waiver for the remaining hardware P0.
