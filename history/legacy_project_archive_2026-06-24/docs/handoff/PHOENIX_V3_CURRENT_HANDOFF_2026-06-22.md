# Phoenix V3 Current Handoff

Date: 2026-06-22
Status: `redo_required`

## Latest Update - 2026-06-24 Midterm Review Amendments

Current Phoenix V3 work remains `redo_required`, not release-authorized.

Claude reviewed the midterm report and returned verdict
`accept_with_required_amendments`. The amended next-work plan replaces the
old M72 direction.

Latest files:

- Midterm packet, amended §7:
  `docs/reviews/call_for_review_phoenix_v3_midterm_report_and_next_plan_2026-06-24.md`
- Claude review:
  `docs/reviews/claude_phoenix_v3_midterm_external_review_2026-06-24.md`
- Revised M72 plan:
  `docs/reviews/phoenix_v3_revised_m72_plan_target_the_blocker_2026-06-24.md`

New controlling direction:

- Do not re-prove the runner on a non-blocker family.
- M72 must target the scorecard blocker:
  Barnes-Hut / aggregate-tree-fused-vector-sum, current Set-A geomean around
  `0.844x`.
- Reuse the existing M43 grouped-reduction / CuPy prepared-session runner
  evidence where applicable.
- Every trunk evidence packet must record `win_source` as one of
  `{residency_wall, partner_continuation, kernel}`.
- Every new trunk family must be bound to a named scorecard-controlling row
  before implementation; a family that moves no blocker is capability evidence
  only and leaves the release path.
- `barnes_hut` and `librts_spatial_index` regressions must be explicitly owned
  as either `trunk_fix` or `severe_regression_repair`.

Non-authorization remains unchanged: no V3 release, no all-app run, no POD
spend, no runbook execution, no public speedup wording, no broad V3-over-V2
claim, no V4, no embedding, no C ABI, and no true-zero-copy claim.

Decision audit:

1. Was I foolish? Yes, partially: the previous M72 plan was runtime-driven but
   blocker-blind.
2. If yes, what actions made it foolish? It targeted a clean family instead of
   the scorecard blocker that actually prevents V3 release.
3. Was there another path? Yes: target the Barnes-Hut / aggregate-tree blocker
   using the existing M43 grouped-reduction runner evidence.
4. Can I now try a different path? Yes: adopt the revised M72 blocker-targeted
   plan before further engineering.

## Latest Update - 2026-06-24 M70/M71 3AI Complete

Current Phoenix V3 work remains `redo_required`, not release-authorized.

M70 and M71 are now goal-complete only for their bounded no-execution scopes:
M70 is the RTNN focused protocol draft, and M71 is the RTNN local harness
dry-run gate. Claude backfilled the required reviews after reset, post-Claude
validation passed, and final 3AI consensus is recorded.

Completion state:

- Status:
  `m70_m71_3ai_accept_goal_complete_no_execution_no_pod_no_release`.
- Final 3AI consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m70_m71_final_3ai_consensus_2026-06-24.md`.
- Goal-completion audit:
  `docs/reports/phoenix_v3_m70_m71_goal_completion_3ai_audit_2026-06-24.md`.
- Claude M70 output:
  `docs/reviews/claude_phoenix_v3_m70_rtnn_focused_protocol_recorded_review_2026-06-23.md`.
- Claude M71 output:
  `docs/reviews/claude_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_recorded_review_2026-06-23.md`.
- Combined Claude summary:
  `docs/reviews/claude_phoenix_v3_m70_m71_backfill_recorded_review_2026-06-24.md`.

Files:

- Backfill call for review:
  `docs/reviews/call_for_review_phoenix_v3_m70_m71_claude_backfill_2026-06-24.md`
- Claude prompt:
  `scratch/claude_prompt_phoenix_v3_m70_m71_backfill_2026-06-24.txt`
- Claude helper:
  `scripts/run_claude_phoenix_v3_m70_m71_backfill_2026_06_24.ps1`
- Backfill gate:
  `tests/v3_phoenix_m70_m71_claude_backfill_packet_gate_test.py`
- Backfill intake validator:
  `scripts/v3_phoenix_m70_m71_claude_backfill_intake.py`
- Backfill intake gate:
  `tests/v3_phoenix_m70_m71_claude_backfill_intake_test.py`
- Pending intake snapshot:
  `docs/rebuild/v3/phoenix_v3_m70_m71_claude_backfill_intake_pending_2026-06-24.json`
  and
  `docs/reports/phoenix_v3_m70_m71_claude_backfill_intake_pending_2026-06-24.md`
- Goal-completion audit builder:
  `scripts/v3_phoenix_m70_m71_goal_completion_audit.py`
- Goal-completion audit gate:
  `tests/v3_phoenix_m70_m71_goal_completion_audit_test.py`
- Pending goal-completion audit snapshot:
  `docs/rebuild/v3/phoenix_v3_m70_m71_goal_completion_audit_pending_2026-06-24.json`
  and
  `docs/reports/phoenix_v3_m70_m71_goal_completion_audit_pending_2026-06-24.md`
- Post-Claude local validation helper:
  `scripts/run_phoenix_v3_m70_m71_post_claude_local_validation_2026_06_24.ps1`
- Final 3AI consensus builder:
  `scripts/v3_phoenix_m70_m71_final_3ai_consensus.py`
- Final 3AI consensus gate:
  `tests/v3_phoenix_m70_m71_final_3ai_consensus_test.py`
- Pending final 3AI consensus snapshot:
  `docs/rebuild/v3/phoenix_v3_m70_m71_final_3ai_consensus_pending_2026-06-24.json`
  and
  `docs/reports/phoenix_v3_m70_m71_final_3ai_consensus_pending_2026-06-24.md`
- After-Claude intake/audit/consensus snapshots:
  `docs/rebuild/v3/phoenix_v3_m70_m71_claude_backfill_intake_after_claude_2026-06-24.json`,
  `docs/rebuild/v3/phoenix_v3_m70_m71_goal_completion_audit_after_claude_2026-06-24.json`,
  and
  `docs/rebuild/v3/phoenix_v3_m70_m71_final_3ai_consensus_after_claude_2026-06-24.json`
- Supplemental Antigravity backfill/intake review:
  `docs/reviews/antigravity_phoenix_v3_m70_m71_backfill_packet_intake_review_2026-06-24.md`
  with verdict
  `accept_m70_m71_backfill_packet_intake_continue_wait_for_claude`.
- Antigravity P1-B action:
  `scripts/v3_phoenix_m70_m71_claude_backfill_intake.py` now fails closed by
  default for pending/blocked intake statuses; pending snapshot generation must
  use explicit `--allow-non-accepted`.
- Claude review debt register:
  `docs/reviews/phoenix_v3_claude_review_debt_register_2026-06-23.md`
- Latest rebuild:
  `docs/reports/phoenix_v3_m70_m71_final_goal_completion_v3_rebuild_2026-06-24.json`
  with `module_count=148`, `Ran 752 tests`, `OK`.

Decision audit:

1. Was I foolish? No, this step closes review debt without expanding scope.
2. If yes, what actions made it foolish? Not applicable.
3. Was there another path? Yes: leave M70/M71 pending despite accepted Claude
   reviews, but that would block clean next-step planning.
4. Can I now try a different path? Yes: treat M70/M71 as closed process
   milestones and require a separate 3AI-reviewed protocol before any execution
   proposal.

Next allowed action:

1. Plan the next Phoenix V3 protocol separately.
2. Do not treat M70/M71 completion as execution, POD, release, or performance
   authorization.
3. Do not run live benchmarks, spend POD, run all-app, run a runbook, make
   public speedup wording, claim broad V3-over-V2 performance, claim RT-core
   speedup, claim whole-app or paper results, claim automatic partner selection,
   do route-specific RTNN app tuning, claim external device-buffer interop,
   start host-integration or low-level host-interface work, or close watch rows.

## Latest Update - 2026-06-23 M71

Current Phoenix V3 work remains `redo_required`, not release-authorized.

M71 built the RTNN local harness dry-run gate allowed by the provisional M70
2AI consensus. It is dry-run only: no benchmark execution, no runbook, no POD,
no all-app, no release, and no public performance claim.

M71 result:

- Status:
  `m71_rtnn_local_harness_dry_run_gate_ready_no_execution_no_pod`.
- Shape groups covered: `7`.
- Rows covered: `14`.
- Telemetry contract ready: `true`.
- The RTNN productized app path now exposes separated telemetry fields:
  `input_load`, `input_pack`, `input_load_pack`,
  `runner_after_input_load_pack`, `hot_query_median`, and
  `signature_match_status`.

External review state:

- Antigravity accepted M71 with verdict:
  `accept_m71_local_dry_run_gate_continue_no_execution_no_pod`.
- M70 Claude backfill remains required before M70 completion.
- M71 itself is provisional and not goal-complete.

Files:

- M71 generator:
  `scripts/v3_phoenix_m71_rtnn_local_harness_dry_run_gate.py`
- M71 gate:
  `tests/v3_phoenix_m71_rtnn_local_harness_dry_run_gate_test.py`
- Packet:
  `docs/rebuild/v3/phoenix_v3_m71_rtnn_local_harness_dry_run_gate_2026-06-23.json`
- Report:
  `docs/reports/phoenix_v3_m71_rtnn_local_harness_dry_run_gate_2026-06-23.md`
- Call for review:
  `docs/reviews/call_for_review_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_2026-06-23.md`
- Antigravity review:
  `docs/reviews/antigravity_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_review_2026-06-23.md`
- Provisional 2AI consensus:
  `docs/reviews/codex_antigravity_phoenix_v3_m71_local_dry_run_gate_provisional_2ai_consensus_pending_claude_2026-06-23.md`
- Status:
  `docs/reports/phoenix_v3_m71_status_provisional_2ai_pending_claude_2026-06-23.md`
- Final rebuild:
  `docs/reports/phoenix_v3_m71_v3_rebuild_after_provisional_2ai_2026-06-23.json`
  with `module_count=144`, `Ran 736 tests`, `OK`.

Next allowed action:

1. Do not mark M70 or M71 complete until Claude review debt is backfilled and a
   final 3AI completion path exists.
2. If continuing locally while Claude is blocked, stay in no-execution work:
   schema hardening, dry-run harness design, or review-debt preparation only.
3. Do not run live benchmarks, spend POD, run all-app, run a runbook, make
   public speedup wording, claim broad V3-over-V2 performance, claim RT-core
   speedup, claim whole-app or paper results, claim automatic partner selection,
   do route-specific RTNN app tuning, claim external device-buffer interop,
   start future host-integration or low-level host-interface work, or close
   watch rows.

## Latest Update - 2026-06-23 M70

Current Phoenix V3 work remains `redo_required`, not release-authorized.

M70 drafted the RTNN focused protocol selected by M69. It is a protocol draft
only: no execution, no POD, no all-app run, no runbook, no release, and no
public performance claim.

M70 protocol state:

- Protocol status:
  `m70_rtnn_focused_protocol_draft_ready_for_review_no_execution_no_pod_no_release`.
- Shape groups named: `7`.
- Frozen RTNN rows named: `14`.
- Same-contract incumbents named for OptiX and Embree rows.
- Required carry-forward boundaries: uniform-only M69 repeat50 phase evidence,
  per-distribution phase bounds before clustered/shell use, full-batch
  self-query constraint, separated hot-query/runner-wall/prepare/input-pack
  metrics, and the `0.988781x` hot-query boundary.

External review state:

- Antigravity accepted M70 with verdict:
  `accept_m70_protocol_draft_continue_m71_local_harness_no_execution_no_pod`.
- Claude is blocked by session limit and has not yet provided a M70 review.
- Therefore M70 is pending Claude backfill and is not 3AI goal-complete.

Files:

- M70 generator:
  `scripts/v3_phoenix_m70_rtnn_focused_protocol.py`
- M70 gate:
  `tests/v3_phoenix_m70_rtnn_focused_protocol_gate_test.py`
- Packet:
  `docs/rebuild/v3/phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.json`
- Report:
  `docs/reports/phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md`
- Call for review:
  `docs/reviews/call_for_review_phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md`
- Antigravity review:
  `docs/reviews/antigravity_phoenix_v3_m70_rtnn_focused_protocol_review_2026-06-23.md`
- Claude blocked record:
  `docs/reviews/external_review_blocked_phoenix_v3_m70_claude_session_limit_2026-06-23.md`
- Provisional 2AI consensus:
  `docs/reviews/codex_antigravity_phoenix_v3_m70_provisional_2ai_consensus_pending_claude_2026-06-23.md`
- Pending status:
  `docs/reports/phoenix_v3_m70_status_pending_claude_backfill_2026-06-23.md`
- Final rebuild:
  `docs/reports/phoenix_v3_m70_v3_rebuild_after_provisional_2ai_pending_claude_2026-06-23.json`
  with `module_count=143`, `Ran 729 tests`, `OK`.

Next allowed action while Claude is blocked:

1. Continue only with M71 local RTNN harness design/dry-run gate.
2. M71 must validate schema, configuration, source-surface routing, required
   telemetry fields, and fail-closed behavior.
3. M71 must not execute live benchmarks, spend POD, run all-app, run a runbook,
   make public speedup wording, claim broad V3-over-V2 performance, claim
   RT-core speedup, claim whole-app or paper results, claim automatic partner
   selection, do route-specific RTNN app tuning, claim external device-buffer
   interop, start future host-integration or low-level host-interface work, or
   close watch rows.

## Latest Update - 2026-06-23 M69

Current Phoenix V3 work remains `redo_required`, not release-authorized.

M69 completed the local RTNN fixed-radius ranked-summary phase/shape bridge
audit selected by M68. The 3-AI conclusion is that RTNN is bridgeable to the
generic ranked-summary prepared-session runner surface, but M69 does not
authorize execution, POD, all-app, release, or any public performance claim.

Generic runner surface:

```text
fixed_radius_ranked_summary_3d_prepared_session
```

Frozen RTNN state:

- Frozen RTNN all-app rows mapped to ranked-summary shapes: `14`.
- Rows below `1.05x`: `13`.
- Shape groups below `1.05x`: `6`.
- Bridge status: `bridgeable_but_not_runbook_authorized`.
- Next allowed goal:
  `M70_draft_reviewed_rtnn_focused_protocol_no_execution`.

Phase attribution:

- Total runner-wall delta: `0.866893s`.
- Input load/pack share of delta: `0.323`.
- Runner-after-pack share of delta: `0.677`.
- Execution-prepare delta: `0.357405s`.
- Hot-query speedup vs legacy: `0.988781x`.

Interpretation boundary:

- The positive repeat50 runner-wall signal is not hot-query speedup.
- The current phase attribution is uniform-distribution evidence only.
- Per-distribution phase bounds are required before any protocol uses clustered
  or shell shapes.
- `prepared_execution_ranked_summary` currently requires full-batch
  self-queries.
- Exact aggregate, productized prepared-session runner, graph partner bridge,
  and paper/author diagnostic rows must not be merged into one public claim.

3-AI consensus is complete:

- M69 packet:
  `docs/rebuild/v3/phoenix_v3_m69_rtnn_phase_shape_bridge_audit_2026-06-23.json`
- M69 report:
  `docs/reports/phoenix_v3_m69_rtnn_phase_shape_bridge_audit_2026-06-23.md`
- Claude recorded review:
  `docs/reviews/claude_phoenix_v3_m69_rtnn_phase_shape_bridge_audit_recorded_review_2026-06-23.md`
- Antigravity review:
  `docs/reviews/antigravity_phoenix_v3_m69_rtnn_phase_shape_bridge_audit_review_2026-06-23.md`
- 3-AI consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m69_rtnn_phase_shape_bridge_audit_3ai_consensus_2026-06-23.md`
- Goal completion audit:
  `docs/reports/phoenix_v3_m69_goal_completion_audit_2026-06-23.md`
- Final rebuild:
  `docs/reports/phoenix_v3_m69_v3_rebuild_after_final_handoff_2026-06-23.json`
  with `module_count=142`, `Ran 722 tests`, `OK`.

Next allowed action:

1. Start M70 as a no-execution RTNN focused protocol draft only.
2. Name exact frozen RTNN shapes and same-contract incumbents.
3. Keep hot-query, runner-wall, prepare, and input-loading/packing metrics
   separate.
4. Carry the uniform-only phase-evidence boundary, clustered/shell
   per-distribution requirement, full-batch self-query constraint, and
   `0.988781x` hot-query boundary.
5. Do not run all-app, spend POD, execute a runbook, make public speedup
   wording, claim broad V3-over-V2 performance, claim RT-core speedup, claim
   whole-app or paper results, claim automatic partner selection, do
   route-specific RTNN app tuning, claim external device-buffer interop, start
   future host-integration or low-level host-interface work, or close watch
   rows.

## Latest Update - 2026-06-23 M68

Current Phoenix V3 work remains `redo_required`, not release-authorized.

M68 completed the next Set-A family selection after M67. The 3-AI conclusion is
to select RTNN fixed-radius ranked-summary for M69 local phase/shape bridge
audit. This is a generic runtime-family selection, not RTNN app tuning.

Selected family:

```text
fixed_radius_ranked_summary_3d_prepared_session
```

Decision basis:

- Barnes-Hut is already counted internally by M67 and must not be reopened as
  Barnes-Hut-specific work.
- Spatial/RayJoin topology-stream repeat execution is M66 non-go because the
  current route removes no new physical work.
- LibRTS is Set-B control work, not the next Set-A runtime family.
- Hausdorff is already above the frozen Set-A app-win threshold.
- RTNN remains below the app-win threshold (`1.003327x`) and has a generic
  productized ranked-summary prepared-session runner with existing focused
  repeat50 evidence.

Boundary facts:

- RTNN runner vs legacy runner-wall: `1.370176x`.
- RTNN runner vs legacy hot query: `0.988781x`.
- The runner-wall signal is repeat50 focused evidence only. It is not a
  single-shot, whole-app, public speedup, broad V3-over-V2, or release claim.

Claude P2 was applied before completion:

- M69 must separate input-loading/packing consolidation from ranked-summary
  execution phase compression.
- If the runner-wall improvement is attributable entirely to input-loading or
  packing consolidation with no ranked-summary phase compression, M69 must stop
  before any runbook.

3-AI consensus is complete:

- M68 packet:
  `docs/rebuild/v3/phoenix_v3_m68_next_set_a_family_selection_2026-06-23.json`
- M68 report:
  `docs/reports/phoenix_v3_m68_next_set_a_family_selection_2026-06-23.md`
- Claude recorded review:
  `docs/reviews/claude_phoenix_v3_m68_next_set_a_family_selection_recorded_review_2026-06-23.md`
- Antigravity review:
  `docs/reviews/antigravity_phoenix_v3_m68_next_set_a_family_selection_review_2026-06-23.md`
- 3-AI consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m68_next_set_a_family_selection_3ai_consensus_2026-06-23.md`
- Goal completion audit:
  `docs/reports/phoenix_v3_m68_goal_completion_audit_2026-06-23.md`
- Final rebuild:
  `docs/reports/phoenix_v3_m68_v3_rebuild_after_3ai_completion_2026-06-23.json`
  with `module_count=141`, `Ran 715 tests`, `OK`.

Next allowed action:

1. Start M69 local-only RTNN ranked-summary phase/shape bridge audit.
2. Map frozen RTNN all-app rows to the generic ranked-summary runner surface.
3. Attribute the existing repeat50 runner-wall signal by phase before any
   runbook is proposed.
4. Do not run all-app, spend POD, make public speedup wording, claim broad
   V3-over-V2 performance, claim RT-core speedup, claim whole-app or paper
   results, claim automatic partner selection, do route-specific RTNN app
   tuning, claim external device-buffer interop, start future-version
   host-integration or low-level host-interface work, or close watch rows.

## Latest Update - 2026-06-23 M67

Current Phoenix V3 work remains `redo_required`, not release-authorized.

M67 completed the local Barnes-Hut phase-structure pre-audit required after
M66's topology-stream non-go redirect. The 3-AI conclusion is that Barnes-Hut
may be counted internally as an existing Step-1 material family, but it should
not receive more Barnes-Hut-specific engineering right now.

The reconciled read is:

- M45/M66 remain valid: do not reopen Barnes-Hut app tuning.
- Historical prepared OptiX/frontier work is predecessor-displacement evidence
  at `12.730691x` geomean versus the productized runner.
- Current fused-control runner parity is `0.999328x` geomean, so this is not a
  same-contract V3-over-V2.14 speedup row.
- M29 classifies the V2.14 surface as
  `v2_14_has_cpu_fused_or_typed_stream_only`, so Barnes-Hut is counted as a V3
  runtime capability/productized-route addition, not broad release evidence.

3-AI consensus is complete:

- M67 packet:
  `docs/rebuild/v3/phoenix_v3_m67_barnes_hut_phase_structure_pre_audit_2026-06-23.json`
- M67 report:
  `docs/reports/phoenix_v3_m67_barnes_hut_phase_structure_pre_audit_2026-06-23.md`
- Claude recorded review:
  `docs/reviews/claude_phoenix_v3_m67_barnes_hut_phase_structure_pre_audit_recorded_review_2026-06-23.md`
- Antigravity review:
  `docs/reviews/antigravity_phoenix_v3_m67_barnes_hut_phase_structure_pre_audit_review_2026-06-23.md`
- 3-AI consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m67_barnes_hut_phase_structure_pre_audit_3ai_consensus_2026-06-23.md`
- Goal completion audit:
  `docs/reports/phoenix_v3_m67_goal_completion_audit_2026-06-23.md`
- Final rebuild:
  `docs/reports/phoenix_v3_m67_v3_rebuild_after_3ai_completion_2026-06-23.json`
  with `module_count=140`, `Ran 709 tests`, `OK`.

Next allowed action:

1. Select the next generic Set-A family.
2. Keep work local until a separate reviewed authorization exists.
3. Do not run all-app, spend POD, make public speedup wording, claim broad
   V3-over-V2 performance, claim RT-core speedup for the Numba CUDA route,
   claim whole-app or paper reproduction results, claim automatic partner
   selection, do Barnes-Hut-specific engine tuning, claim external device-buffer
   interop, start future-version host-integration or low-level host-interface
   work, or close watch rows.

## Latest Update - 2026-06-23 M59

Current Phoenix V3 work remains `redo_required`, not release-authorized.

M59 closed the decision after M58 LibRTS/AABB evidence: LibRTS remains a
Set-B yellow/open control limitation, not the next Step-2 runtime optimization
gap. The OptiX cold single-shot row stays a release-risk debt; it is not green.

3-AI consensus is complete:

- M59 report:
  `docs/reports/phoenix_v3_m59_librts_yellow_open_decision_2026-06-23.md`
- Claude recorded review:
  `docs/reviews/claude_phoenix_v3_m59_librts_yellow_open_decision_recorded_review_2026-06-23.md`
- Antigravity review:
  `docs/reviews/antigravity_phoenix_v3_m59_librts_yellow_open_decision_review_2026-06-23.md`
- 3-AI consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m59_librts_yellow_open_decision_3ai_consensus_2026-06-23.md`
- Goal completion audit:
  `docs/reports/phoenix_v3_m59_goal_completion_audit_2026-06-23.md`

Next allowed action:

1. Start M60 as a reviewed Step-2 Set-A selection packet.
2. Choose the next architecture-bearing runtime family; do not tune LibRTS as
   the active runtime target.
3. Do not run all-app, do not spend broad POD, do not make public performance
   wording, and do not close LibRTS watch rows.

## Latest Update - 2026-06-23 M60

Current Phoenix V3 work remains `redo_required`, not release-authorized.

M60 selected Spatial/RayJoin point-location topology stream as the next local
Step-2 Set-A runtime-family target. The selected scope is generic
topology-stream prepared-handle, internal RTDL-owned residency, and full-M3
phase accounting. It is not RayJoin app-specific route tuning and not POD
authorization.

3-AI consensus is complete:

- M60 report:
  `docs/reports/phoenix_v3_m60_step2_set_a_selection_spatial_topology_stream_2026-06-23.md`
- Claude recorded review:
  `docs/reviews/claude_phoenix_v3_m60_step2_set_a_selection_recorded_review_2026-06-23.md`
- Antigravity review:
  `docs/reviews/antigravity_phoenix_v3_m60_step2_set_a_selection_review_2026-06-23.md`
- Antigravity debt follow-up:
  `docs/reviews/antigravity_phoenix_v3_m60_debt_followup_2026-06-23.md`
- 3-AI consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m60_step2_set_a_selection_3ai_consensus_2026-06-23.md`
- Goal completion audit:
  `docs/reports/phoenix_v3_m60_goal_completion_audit_2026-06-23.md`

M61 carry-forward rules:

1. Label the `2.282x` device-resident delta as
   `internal_routing_delta_not_public_row`.
2. Do not imply RTDL beats RayJoin author timing.
3. Do not call internal residency true zero-copy.
4. Map or supplement `PreparedExecutionReport` so the full topology-stream M3
   table can be emitted.
5. Keep M61 local no-POD gap-ledger/design/gate work only.

## Latest Update - 2026-06-23 M61

Current Phoenix V3 work remains `redo_required`, not release-authorized.

M61 built the local no-POD topology-stream gap ledger required by M60. It
labels the large-PIP device-resident delta as
`internal_routing_delta_not_public_row`, records the phase-vocabulary bridge
between `PreparedExecutionReport` and the topology-stream M3 table, checks the
current prepared-session topology-stream surface, and checks that the M50
runner remains fail-closed.

3-AI consensus is complete:

- M61 report:
  `docs/reports/phoenix_v3_m61_topology_stream_gap_ledger_2026-06-23.md`
- Ledger JSON:
  `docs/rebuild/v3/phoenix_v3_m61_topology_stream_gap_ledger_2026-06-23.json`
- Claude recorded review:
  `docs/reviews/claude_phoenix_v3_m61_topology_stream_gap_ledger_recorded_review_2026-06-23.md`
- Antigravity review:
  `docs/reviews/antigravity_phoenix_v3_m61_topology_stream_gap_ledger_review_2026-06-23.md`
- 3-AI consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m61_topology_stream_gap_ledger_3ai_consensus_2026-06-23.md`
- Goal completion audit:
  `docs/reports/phoenix_v3_m61_goal_completion_audit_2026-06-23.md`

M62 carry-forward rules:

1. Upgrade text-mining surface checks to behavioral or metadata-value gates
   where possible.
2. Explicitly set `true_zero_copy_claim_authorized=false` in topology-stream
   runner metadata.
3. Add a sanity cap or equivalent guard for the internal delta ratio.
4. Keep M62 local no-POD contract/gate implementation only.

## Latest Update - 2026-06-23 M30-M37

Current Phoenix V3 work remains `redo_required`, not release-authorized.

Do not run all-app. Do not spend POD on broad suites. Do not make public
speedup, broad V3-over-V2, true-zero-copy, automatic partner-selection, V4,
C ABI, or embedding claims.

## Latest Update - 2026-06-23 M38-M40

Current Phoenix V3 status remains `redo_required`, not release-authorized.

M38 defined the focused component-union POD protocol and M39 implemented the
reviewed local harness. Claude accepted M39 with verdict
`accept_m39_authorize_one_focused_component_union_pod`, authorizing exactly one
focused component-union POD run using `--variant all --require-rt-hardware`.

M40 executed that single authorized focused POD run on
`NVIDIA RTX 4000 Ada Generation` hardware. Local evidence copied back:

- `docs/rebuild/v3/evidence/phoenix_v3_component_union_m39_focused_pod_ab_20260623_142706/`
- Intake report:
  `docs/reports/phoenix_v3_m40_component_union_focused_pod_intake_2026-06-23.md`
- Review request:
  `docs/reviews/call_for_review_phoenix_v3_m40_component_union_focused_pod_intake_2026-06-23.md`

M40 preliminary intake:

- exit code: `0`
- failed checks: `0`
- component signatures match across Embree, legacy OptiX, and productized
  runner
- productized runner records `runtime_executed=true`,
  `runtime_trunk_executes_end_to_end=true`,
  `internal_device_residency_between_rtdl_phases=true`,
  `hot_path_host_materialization=false`
- runner vs Embree hot: `1.221027x`
- runner vs Embree inclusive wall: `2.421405x`
- runner vs legacy inclusive wall: `1.254316x`
- runner vs legacy hot is only parity/slightly slower, about `0.994x`; do not
  claim hot-path superiority over the existing legacy OptiX route from this run

Interpretation boundary:

- This is one positive Step-1-shaped focused probe, not release evidence.
- It supports continuing to Step 2 only if external review accepts the intake.
- It does not authorize all-app POD spend, public speedup wording, broad
  V3-over-V2 claims, V4/embedding/C-ABI work, or release.

M40 harness caveat already fixed locally after the run:

- `scripts/v3_phoenix_component_union_m38_pod_ab.py` now emits a real-run
  status distinct from the dry-run `not_pod_run` label.
- It now exposes `runner_vs_legacy_hot_speedup` as a first-class comparison.
- Focused local validation after this fix:
  `py -3 -m unittest tests.v3_phoenix_m39_component_union_harness_test tests.v3_release_wording_gate_test`
  ran 9 tests OK.

Claude M40 review and Codex+Claude consensus are complete:

- raw Claude review:
  `docs/reviews/claude_phoenix_v3_m40_component_union_focused_pod_intake_review_2026-06-23.raw.md`
- recorded Claude review:
  `docs/reviews/claude_phoenix_v3_m40_component_union_focused_pod_intake_recorded_review_2026-06-23.md`
- consensus:
  `docs/reviews/codex_claude_phoenix_v3_m40_component_union_focused_pod_intake_2ai_consensus_2026-06-23.md`
- consensus verdict: `accept_with_caveats_fixed_locally_continue_step2`

Full V3 rebuild after caveat fixes:

```text
PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 119
Ran 620 tests in 72.675s
OK
stdout: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m40_harness_caveat_fixes_20260623_143417.stdout.txt
```

Next action:

1. Move to Step 2 by wiring a second Set-A family into the same
   productized runner discipline.
2. Run local gates and prepare review.
3. Do not spend additional POD until Step-2 local work is reviewed.
4. Do not reinterpret M40 numbers into a release claim.

## Latest Update - 2026-06-23 M41

M41 selected `grouped_vector_sum_2d` / grouped reduction as the second Step-2
local family after M40 component-union. This is local harness work only; it
does not authorize additional POD.

Files:

- harness:
  `scripts/v3_phoenix_grouped_reduction_m41_local_harness.py`
- tests:
  `tests/v3_phoenix_m41_grouped_reduction_harness_test.py`
- report:
  `docs/reports/phoenix_v3_m41_grouped_reduction_second_family_local_harness_2026-06-23.md`
- review request:
  `docs/reviews/call_for_review_phoenix_v3_m41_grouped_reduction_second_family_local_harness_2026-06-23.md`

M41 local validation:

```text
Focused: Ran 14 tests OK
v3_rebuild: module_count 120; Ran 625 tests in 74.220s; OK
stdout: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m41_grouped_reduction_harness_20260623_144304.stdout.txt
```

Claude review is in progress through:

- `scratch/run_claude_m41_review.ps1`
- raw output:
  `docs/reviews/claude_phoenix_v3_m41_grouped_reduction_second_family_local_harness_review_2026-06-23.raw.md`

Do not request or run paid POD for M41 until the external review returns and a
Codex+external consensus is saved.

M41 follow-up local evidence:

- small free local CUDA smoke:
  `docs/reports/phoenix_v3_m41_grouped_reduction_local_cuda_smoke_intake_2026-06-23.md`
- Claude small-smoke review:
  `docs/reviews/claude_phoenix_v3_m41_grouped_reduction_local_cuda_smoke_recorded_review_2026-06-23.md`
- serious free local run:
  `docs/reports/phoenix_v3_m41_grouped_reduction_serious_free_local_intake_2026-06-23.md`

Serious local result is externally reviewed and consensus-closed:

- recorded Claude review:
  `docs/reviews/claude_phoenix_v3_m41_grouped_reduction_serious_free_local_recorded_review_2026-06-23.md`
- Codex+Claude consensus:
  `docs/reviews/codex_claude_phoenix_v3_m41_grouped_reduction_2ai_consensus_2026-06-23.md`
- consensus verdict:
  `m41_contract_positive_performance_blocked_paid_pod_blocked`

M41 final read: contract-positive (`failed_check_count=0`,
`step2_local_runner_contract_candidate=true`) but paid-POD-blocked because
runner vs CPU hot is `0.4979998501868343x` and low occupancy persists. Do not
request paid POD for grouped reduction unless a later review explicitly
authorizes it.

Next step must choose:

- Path A: diagnose grouped-reduction grid-size/occupancy root cause before one
  bounded free-local shape experiment; or
- Path B: move Step-2 performance evidence to another family.

Current M30-M37 packet:

- `docs/reviews/call_for_review_phoenix_v3_m30_m33_external_review_bundle_2026-06-23.md`
- `docs/reports/phoenix_v3_m35_focused_evidence_gap_ledger_2026-06-23.md`
- `docs/reviews/call_for_review_phoenix_v3_m35_focused_gap_ledger_2026-06-23.md`
- `docs/reviews/claude_phoenix_v3_m35_focused_gap_ledger_recorded_review_2026-06-23.md`
- `docs/reviews/codex_claude_phoenix_v3_m35_focused_gap_ledger_2ai_consensus_2026-06-23.md`
- `docs/reports/phoenix_v3_m36_grouped_vector_sum_prepared_session_core_node_2026-06-23.md`
- `docs/reviews/codex_claude_phoenix_v3_m36_grouped_reduction_core_node_2ai_consensus_2026-06-23.md`
- `docs/reports/phoenix_v3_m37_component_union_core_node_and_adapter_metadata_gate_2026-06-23.md`
- `docs/reviews/call_for_review_phoenix_v3_m37_component_union_core_node_2026-06-23.md`
- `docs/reviews/claude_phoenix_v3_m37_component_union_core_node_recorded_review_2026-06-23.md`
- `docs/reviews/codex_claude_phoenix_v3_m37_component_union_core_node_2ai_consensus_2026-06-23.md`
- Codex local self-review, not external consensus:
  `docs/reviews/codex_phoenix_v3_m30_m33_bundle_local_self_review_2026-06-23.md`
- Claude recorded external review:
  `docs/reviews/claude_phoenix_v3_m30_m34_bundle_recorded_review_2026-06-23.md`
- Codex+Claude 2-AI consensus:
  `docs/reviews/codex_claude_phoenix_v3_m30_m34_2ai_consensus_2026-06-23.md`

Local state:

- M30 RTNN remains a focused repeat50 prepared-runner candidate, pending
  external review under the post-M22/M29 framing.
- M31 adds a shared Step-3 audit surface that distinguishes
  `runtime_executed=true` from real residency-default readiness.
- M32 adds a shared Step-4 continuation-core audit surface.
- M33 classifies all 11 current prepared-session helpers as seven local-audit
  ready families, one blocked Set-A seed, and three blocked Set-B controls.
- AABB helpers now report `set_a_probe_candidate=false` and
  `set_b_control_candidate=true`; the LibRTS wrapper propagates those fields to
  the prepared-runner payload.
- M31/M32 audit payloads echo Set-A/Set-B classification for review.
- A dedicated M30-M33 review-bundle gate now checks non-authorization wording,
  referenced packet paths, and the boundary between local matrix evidence and
  external consensus. It is included in `v3_rebuild`.
- M34 local addendum while awaiting external review: added
  `scripts/v3_phoenix_prepared_session_surface_ledger_gate.py` and
  `tests/v3_phoenix_prepared_session_surface_ledger_gate_test.py`; the gate
  found and fixed one surface drift:
  `run_fixed_radius_threshold_reached_count_2d_prepared_session` was in the
  M33 ledger but missing from `prepared_execution.__all__`. Focused validation:
  39 tests OK.
- M34 report:
  `docs/reports/phoenix_v3_m34_prepared_session_surface_ledger_gate_2026-06-23.md`.
- M35 adds a focused evidence gap ledger and machine gate:
  `docs/reports/phoenix_v3_m35_focused_evidence_gap_ledger_2026-06-23.md`
  and `tests/v3_phoenix_m35_focused_gap_ledger_test.py`. It freezes RTDBSCAN
  component-signature and RayJoin point-location as structurally ready but not
  material, and redirects M36/M37 to generic grouped-reduction and
  component-union core nodes.
- Claude accepted M35 with verdict `accept_m35_gap_ledger_continue_m36`. The
  only P1 was traceability: M35 needed to acknowledge that M3.4 recommended
  AABB runner generalization and explain why the later M30-M34 bundle review
  redirects the next trunk step to grouped reduction. That P1 is applied in the
  M35 report and recorded in the Codex+Claude consensus.
- M36 adds a generic grouped vector-sum/reduction prepared-session helper:
  `run_grouped_vector_sum_2d_prepared_session`. Claude accepted M36 with
  verdict `accept_m36_grouped_reduction_core_node_continue`; the carry-forward
  check was to verify the real adapter reports `row_count` and `group_count`
  before focused grouped-reduction POD evidence.
- M37 adds a generic component-union prepared-session helper:
  `run_radius_graph_component_union_3d_prepared_session`. It splits
  component-union accounting from component-signature accounting, fails closed
  if signature output is treated as union output, gates the real grouped-vector
  adapter metadata path for `row_count`/`group_count`, and fixes top-level
  `rtdsl` exports for current prepared-session helpers. Claude accepted M37
  with verdict `accept_m37_component_union_core_node_continue`; Codex+Claude
  consensus records it as continue-only, not release/all-app/performance
  evidence.

Latest local focused gate:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_rtnn_prepared_execution_runner_wiring_test \
  tests.v3_phoenix_rtnn_prepared_execution_runner_repeat50_pod_evidence_test \
  tests.v3_phoenix_triangle_runner_m18_pod_ab_test \
  tests.v3_phoenix_m18_triangle_runner_harness_packet_test \
  tests.v3_phoenix_m16_triangle_runner_wiring_test \
  tests.v3_phoenix_barnes_hut_runner_parity_pod_ab_test \
  tests.v3_phoenix_step1_rtdbscan_trunk_probe_report_test \
  tests.v3_phoenix_rayjoin_point_location_runner_pod_ab_test \
  tests.v3_phoenix_hausdorff_threshold_runner_pod_ab_test \
  tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test \
  tests.v3_phoenix_spatial_segment_intersection_runner_wiring_test \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_librts_aabb_count_runner_test \
  tests.v3_release_wording_gate_test \
  tests.v3_phoenix_set_ab_scorecard_gate_test
Ran 91 tests
OK
```

Latest local V3 rebuild matrix:

```text
PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 117
Ran 608 tests in 74.624s
OK
stdout: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m37_label_column_tightening_20260623_134306.stdout.txt
stderr: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m37_label_column_tightening_20260623_134306.stderr.txt
```

This matrix is local contract/gate evidence only. It is not external consensus,
not POD evidence, not release authorization, not all-app authorization, and not
a public performance claim.

Gemini M30/M31/M32/M33, M30-M33 bundle, and final M30-M33 bundle attempts
failed with `IneligibleTierError` / `UNSUPPORTED_CLIENT`; these are
blocked-review records, not consensus. Final blocked record:
`docs/reviews/external_review_blocked_phoenix_v3_m30_m33_bundle_final_gemini_interim_review_2026-06-23.md`.
Use Claude via the known Windows binary when quota is available:

```text
C:\Users\Lestat\.local\bin\claude.exe
```

Next action:

1. Keep release/all-app/public-claim gates closed.
2. Preserve Claude's required clarification: "Step-4 ready by local audit" is
   structural readiness, not material performance proof.
3. M36 is accepted by Claude and local consensus; the grouped-vector real
   adapter metadata check is now covered by M37 local gate.
4. M37 local implementation is complete and externally accepted: split
   component-union and component-signature accounting so union-pass cost is
   visible as a core node, not hidden in an RTDBSCAN route packet. Do not treat
   this as material speedup evidence.
5. Do not run all-app until focused Set-A evidence and Set-B parity
   preconditions are met and externally reviewed.

## Read First

This is the current handoff for Phoenix V3. Older V3/V4 handoffs are history
unless they are explicitly cited by the current V3 rebuild control docs.

Do not resume V4. Do not re-promote old V3/V4 release wording.

Current authority:

- `docs/rebuild/v3/README.md`
- `docs/rebuild/v3/v3_current_status_2026-06-20.md`
- `docs/rebuild/v3/phoenix_v3_readiness_distance_packet_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_release_completion_audit_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_user_facing_performance_dossier_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_objective_conformance_gate_2026-06-22.json`
- `docs/rebuild/v3/phoenix_v3_bounded_external_review_protocol_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_redo_mandate_major_version_performance_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_serious_paired_benchmark_preregistration_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_major_performance_mandate_gate_2026-06-22.json`
- `docs/rebuild/v3/phoenix_v3_release_readiness_gate_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_release_wording_gate_2026-06-21.json`
- `docs/reports/phoenix_v3_release_ready_wording_guard_update_2026-06-22.md`
- `docs/reports/phoenix_v3_short_user_path_guard_update_2026-06-22.md`
- `docs/reports/phoenix_v3_serious_v2x_paired_run_status_2026-06-22.md`
- `docs/reports/phoenix_v3_barnes_hut_symbol_cache_focused_evidence_2026-06-22.md`
- `docs/reports/phoenix_v3_librts_aabb_count_cache_focused_evidence_2026-06-22.md`
- `docs/reports/phoenix_v3_rtnn_neighbor_symbol_cache_focused_evidence_2026-06-22.md`
- `docs/reports/phoenix_v3_fixed_radius_symbol_cache_focused_evidence_2026-06-22.md`
- `docs/reports/phoenix_v3_fixed_radius_graph_self_query_refresh_focused_evidence_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_next_dominant_engine_hotpath_selection_2026-06-22.md`
- `docs/reviews/claude_phoenix_v3_external_review_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_core_gaps_external_verdict_intake_2026-06-22.json`
- `docs/rebuild/v3/phoenix_v3_core_gaps_external_verdict_status_2026-06-22.md`
- `docs/reviews/phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_set_a_set_b_classification_2026-06-22.json`
- `docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.json`
- `docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md`
- `docs/reviews/call_for_review_phoenix_v3_set_a_set_b_classification_gate_2026-06-22.md`
- `docs/reviews/claude_phoenix_v3_set_a_set_b_classification_gate_review_2026-06-22.md`
- `docs/reviews/codex_phoenix_v3_set_a_set_b_classification_gate_2ai_consensus_2026-06-22.md`
- `docs/reports/phoenix_v3_prepared_execution_session_runner_m1_smoke_2026-06-22.md`
- `docs/reports/phoenix_v3_fixed_radius_self_query_runner_binding_m1_1_2026-06-22.md`
- `docs/reports/phoenix_v3_grouped_stream_runner_route_m1_2_2026-06-22.md`
- `docs/reports/phoenix_v3_grouped_stream_runner_route_pod_ab_2026-06-22.md`
- `docs/reports/phoenix_v3_aabb_native_query_handle_runner_route_m2_2026-06-22.md`
- `docs/reports/phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md`
- `docs/reports/phoenix_v3_rtdbscan_component_signature_runner_route_m3_2026-06-22.md`
- `docs/reports/phoenix_v3_rtdbscan_component_signature_runner_route_m3_1_2026-06-22.md`
- `docs/reports/phoenix_v3_rtdbscan_component_signature_runner_route_m3_1_pod_ab_2026-06-22.md`
- `docs/reports/phoenix_v3_optimization_effectiveness_and_remaining_plan_2026-06-22.md`
- `docs/reports/phoenix_v3_performance_failure_optimization_accounting_2026-06-22.md`
- `docs/reports/phoenix_v3_no_performance_optimization_technical_accounting_cn_2026-06-22.md`
- `docs/reports/phoenix_v3_performance_failure_root_cause_and_remaining_optimizations_cn_2026-06-22.md`
- `docs/reviews/call_for_review_phoenix_v3_performance_failure_accounting_2026-06-22.md`
- `docs/reviews/claude_phoenix_v3_performance_failure_accounting_review_2026-06-22.md`
- `docs/reviews/codex_phoenix_v3_performance_failure_accounting_2ai_consensus_2026-06-22.md`
- `docs/reviews/call_for_review_phoenix_v3_performance_failure_root_cause_remaining_optimizations_cn_2026-06-22.md`
- `docs/reviews/external_ai_blocked_phoenix_v3_performance_failure_root_cause_remaining_optimizations_cn_2026-06-22.md`
- `docs/reviews/codex_phoenix_v3_performance_failure_root_cause_remaining_optimizations_cn_record_2026-06-22.md`
- `docs/reports/phoenix_v3_runner_fingerprint_overhead_fix_m3_2_2026-06-22.md`
- `docs/reports/phoenix_v3_rtdbscan_component_signature_runner_route_m3_2_pod_ab_2026-06-22.md`
- `docs/reports/phoenix_v3_repeated_prepared_session_runner_m3_3_2026-06-22.md`
- `docs/reports/phoenix_v3_rtdbscan_repeated_runner_route_m3_4_pod_ab_2026-06-22.md`
- `docs/reports/phoenix_v3_aabb_count_runner_librts_route_m4_2026-06-22.md`
- `docs/reviews/call_for_review_phoenix_v3_repeated_prepared_session_runner_m3_3_2026-06-22.md`
- `docs/reviews/claude_phoenix_v3_repeated_prepared_session_runner_m3_3_review_2026-06-22.md`
- `docs/reviews/codex_phoenix_v3_repeated_prepared_session_runner_m3_3_2ai_consensus_2026-06-22.md`
- `docs/reviews/call_for_review_phoenix_v3_rtdbscan_m3_4_pod_ab_parity_classification_2026-06-22.md`
- `docs/reviews/external_ai_blocked_phoenix_v3_rtdbscan_m3_4_pod_ab_parity_classification_2026-06-22.md`
- `docs/reviews/codex_phoenix_v3_rtdbscan_m3_4_pod_ab_parity_classification_record_2026-06-22.md`
- `docs/reviews/claude_phoenix_v3_rtdbscan_m3_1_pod_ab_negative_classification_review_2026-06-22.md`
- `docs/reviews/codex_phoenix_v3_rtdbscan_m3_1_pod_ab_negative_classification_2ai_consensus_2026-06-22.md`
- `docs/reviews/call_for_review_phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md`
- `docs/reviews/call_for_review_phoenix_v3_core_gaps_status_and_next_work_after_claude_2026-06-22.md`
- `docs/reviews/claude_phoenix_v3_core_gaps_status_and_next_work_after_claude_review_2026-06-22.md`
- `docs/reviews/codex_phoenix_v3_core_gaps_status_and_next_work_after_claude_2ai_consensus_2026-06-22.md`
- `docs/reports/phoenix_v3_hausdorff_threshold_runner_m5_pod_ab_2026-06-22.md`
- `docs/reviews/codex_kepler_phoenix_v3_hausdorff_m5_negative_classification_2ai_consensus_2026-06-22.md`
- `docs/reports/phoenix_v3_trunk_first_pod_resource_plan_2026-06-22.md`
- `docs/reports/phoenix_v3_runner_metadata_overhead_reduction_m6_2026-06-22.md`
- `docs/reports/phoenix_v3_runner_prepare_metric_alignment_m6_1_2026-06-22.md`
- `docs/reports/phoenix_v3_hausdorff_threshold_runner_m5_pod_ab_after_m6_1_2026-06-22.md`
- `docs/reviews/codex_kepler_phoenix_v3_hausdorff_m5_after_m6_1_result_2ai_consensus_2026-06-22.md`
- `docs/reports/phoenix_v3_set_ab_scorecard_update_after_hausdorff_m6_1_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_barnes_hut_blocker_intake_m7_2026-06-22.json`
- `docs/reports/phoenix_v3_barnes_hut_blocker_intake_m7_2026-06-22.md`
- `docs/reviews/codex_erdos_phoenix_v3_barnes_hut_m7_blocker_reclassification_2ai_consensus_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_m8_remaining_blocker_queue_2026-06-22.json`
- `docs/reports/phoenix_v3_m8_remaining_blocker_queue_2026-06-22.md`
- `docs/reviews/codex_tesla_phoenix_v3_m8_remaining_blocker_queue_2ai_consensus_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_raydb_grouped_reduction_redo_alignment_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_rtdbscan_component_union_redo_alignment_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_spatial_topology_stream_redo_alignment_2026-06-22.md`

## Current State

Phoenix V3 is not release-authorized. The previous scoped 13-row interpretation
is downgraded to internal evidence because V3 must be a major RTRDL
language/runtime improvement over V2.x, not a collection of app rows:

```text
status: redo_required
Phoenix M7-qualified release rows: 13
planned capability families: 9 / 9
missing capability families: none
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
blocking_reasons:
  - broad_v2x_performance_not_proven
  - serious_all_app_paired_evidence_failed_release_bar
  - current_scoped_13_row_surface_not_v3_major_release
  - current_core_gap_external_review_blocks_release
```

Latest full local validation:

```text
docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_core_call_for_review_20260622.json
111 modules / 557 tests OK
docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_aabb_runner_m2_20260622.json
111 modules / 557 tests OK
docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m2_1_review_packet_20260622.json
111 modules / 557 tests OK
docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_core_review_label_cleanup_20260622.json
111 modules / 557 tests OK
docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_rtdbscan_component_signature_runner_m3_20260622.json
111 modules / 559 tests OK
```

Latest focused local validation after the RTDBSCAN component-signature runner
contract:

```text
PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test tests.v3_release_wording_gate_test tests.v3_phoenix_release_readiness_gate_test
17 tests OK
PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_rtdbscan_component_signature_optimization_test tests.v3_phoenix_prepared_execution_session_runner_test tests.v3_phoenix_next_dominant_hotpath_selection_test
21 tests OK
```

## What Is Done

- Old V3/V4 user-facing material is quarantined out of the current user path.
- Current user/front-door docs must say V3 is `redo_required`; the
  `source_tree_pod_gated_thirteen_row` scope is internal evidence only.
- We are RTRDL language/runtime designers, not benchmark-app developers.
  Benchmark apps exist to develop and verify reusable runtime capabilities.
- The current surface has 13 exact row-scoped/supplemental M7 rows across 9
  capability families.
- The user-facing performance dossier now summarizes the 13-row surface, all-app
  verdicts, and non-claims in one place.
- The release-surface breadth gate now includes a 13-row integrity manifest:
  every current surface row has existing evidence/review/consensus paths,
  blocked release/public-speed/broad-V3-over-V2 flags, and a planned generic
  capability family.
- The old missing-Spatial / surface-width blocker is closed.
- The objective conformance gate maps the current Phoenix V3 goal to exact
  reusable capability evidence for RayDB grouped reduction, RTDBSCAN component
  union, Spatial topology stream, Triangle prepared graph, and RTNN ranked
  summary; it also keeps V4/C ABI/embedding and broad V3-over-V2 claims out.
- RayDB grouped_reduction is now closed for Phoenix redo by
  `docs/rebuild/v3/phoenix_v3_raydb_grouped_reduction_redo_alignment_2026-06-22.md`.
  Keep exactly three grouped_reduction rows as reusable engine evidence, but do
  not read them as V3 release, whole-RayDB/database acceleration,
  true-zero-copy, broad V3-over-V2, or Gap-1 productized execution-path
  completion.
  The older grouped_reduction device-column `subagent_codex_consensus_complete`
  record is historical only. Current closure comes from
  `docs/reviews/claude_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_review_2026-06-22.md`
  plus
  `docs/reviews/codex_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_claude_supersession_consensus_2026-06-22.md`.
- RTDBSCAN component_union is now closed for Phoenix redo by
  `docs/rebuild/v3/phoenix_v3_rtdbscan_component_union_redo_alignment_2026-06-22.md`.
  Keep exactly one component_union row as reusable engine evidence, but do not
  read it as full RTDBSCAN/DBSCAN acceleration, paper reproduction, broad
  V3-over-V2, or Gap-1 productized execution-path completion.
- Spatial topology_stream is now closed for Phoenix redo by
  `docs/rebuild/v3/phoenix_v3_spatial_topology_stream_redo_alignment_2026-06-22.md`.
  Keep exactly one point_location_topology_stream row as internal reusable
  engine evidence, but do not read it as public Spatial speedup,
  `RTDL beats RayJoin`, RayJoin paper reproduction, broad V3-over-V2, or
  Gap-1 productized execution-path completion.
- The scoped installer blocker is closed only for
  `source_tree_pod_gated_thirteen_row`.
- The secondary hardware blocker is closed only by the scoped
  `single_rtx_4000_ada_driver_550_127_05_pod` waiver.
- The generic-engine queue is closed as `generic_engine_work_queue_closed_not_release`.
- Wording gates keep broad V3-over-V2, package-install, hardware portability,
  whole-app, true-zero-copy, V4/C ABI/embedding, public Spatial, and
  RTDL-beats-RayJoin claims blocked.
- The final-public-surface wording guard update is recorded in
  `docs/reports/phoenix_v3_release_ready_wording_guard_update_2026-06-22.md`;
  it also records the corrected Claude handling rule: one bounded attempt,
  record no-output timeout, continue non-release V3 cleanup.
- The wording guard now auto-discovers and scans every current
  `docs/learn/*.md` page, so learning docs are covered by the public
  claim-boundary gate instead of relying on a hand-picked subset.
- The current public documentation map and tutorial README expose a short,
  safe learner path into V3: first run, hello world, backend choice, one
  benchmark row, and claim boundaries.
- The short user path guard is recorded in
  `docs/reports/phoenix_v3_short_user_path_guard_update_2026-06-22.md`.
- The accepted external Claude verdict is recorded in
  `docs/reviews/claude_phoenix_v3_aggregate_release_readiness_13_row_after_dossier_review_2026-06-22.md`.
- The completed serious paired pod-run status is recorded in
  `docs/reports/phoenix_v3_serious_v2x_paired_run_status_2026-06-22.md`.
- The completed serious paired benchmark report is recorded in
  `docs/rebuild/v3/phoenix_v3_serious_v2x_paired_benchmark_2026-06-22.md`.
- A focused generic runtime fix after the serious run is recorded in
  `docs/reports/phoenix_v3_barnes_hut_symbol_cache_focused_evidence_2026-06-22.md`.
  It caches OptiX library/symbol lookup on
  `PreparedOptixFixedRadiusCountThreshold2D` prepared scenes and recovers the
  largest Barnes-Hut prepared OptiX regressions from 0.622x/0.591x to
  0.999x/1.038x on the same RTX 4000 Ada pod. This is focused runtime evidence,
  not release authorization.
- A second focused generic runtime fix after the serious run is recorded in
  `docs/reports/phoenix_v3_librts_aabb_count_cache_focused_evidence_2026-06-22.md`.
  It adds prepared query packing/symbol caching for Embree
  `AABB_INDEX_QUERY_2D` count calls and recovers the LibRTS Embree count-only
  regression in repeat=3 and repeat=9 focused runs. The LibRTS OptiX row remains
  unstable/inconclusive and needs separate route analysis. This is focused
  runtime evidence, not release authorization.
- A third focused generic runtime hygiene patch after the serious run is
  recorded in
  `docs/reports/phoenix_v3_rtnn_neighbor_symbol_cache_focused_evidence_2026-06-22.md`.
  It caches optional native symbols on prepared Embree/OptiX fixed-radius 3-D
  neighbor handles and passes local/remote targeted tests, but the serious RTNN
  stress focused rerun shows only 1.001x geomean patched V3 vs V2.14 across 12
  rows. Classify this as validated no-material-speedup hygiene, not V3 release
  progress.
- A fourth focused generic runtime fix after the serious run is recorded in
  `docs/reports/phoenix_v3_fixed_radius_symbol_cache_focused_evidence_2026-06-22.md`.
  It broadens prepared fixed-radius count-threshold symbol/library caching in
  the generic Embree/OptiX runtime surfaces. The same-pod focused rerun covers
  17 same-metric rows across Hausdorff XHD, RTDBSCAN, and Barnes-Hut, with
  1.062x geomean patched V3 vs V2.14, 4 rows faster by >5%, 12 within +/-5%,
  and 1 slower by >5%. Classify this as validated focused runtime cleanup, not
  V3 release evidence and not enough to rerun the full all-app benchmark yet.
- A fifth focused generic runtime contract fix after the serious run is
  recorded in
  `docs/reports/phoenix_v3_fixed_radius_graph_self_query_refresh_focused_evidence_2026-06-22.md`.
  It changes grouped-stream core-flag refresh from host query-point upload to
  prepared self-query device-search columns. Same-pod CuPy A/B shows unchanged
  signatures and the intended metadata transition, but only 0.998x geomean
  after-vs-before across 3 rows. Classify this as device-residency/contract
  cleanup, not material speedup and not release evidence. The pod partner venv
  is required for CuPy evidence; Numba remains blocked by PTX/toolkit mismatch.
- The current Phoenix V3 performance-failure accounting is recorded in
  `docs/reports/phoenix_v3_performance_failure_optimization_accounting_2026-06-22.md`.
  It states that Phoenix V3 currently has no release-level performance proof,
  inventories completed optimizations by category, explains why many fixes
  recovered parity rather than major speed, and lists remaining generic runtime
  optimizations with explicit failure modes. Claude reviewed it as
  `approve_with_required_edits`; Codex applied the required edits and recorded
  two-AI consensus in
  `docs/reviews/codex_phoenix_v3_performance_failure_accounting_2ai_consensus_2026-06-22.md`.
  This accounting is now the current handoff basis for performance work.
- The Chinese technical version requested by the user is recorded in
  `docs/reports/phoenix_v3_no_performance_optimization_technical_accounting_cn_2026-06-22.md`.
  It keeps the same non-release conclusion, lists each completed optimization,
  explains why the expectation was technically plausible, why the measured
  result did not become broad V3 performance, and defines the remaining
  generic runtime optimizations that can still be justified.
- The stricter Chinese root-cause and remaining-optimization review document is
  recorded in
  `docs/reports/phoenix_v3_performance_failure_root_cause_and_remaining_optimizations_cn_2026-06-22.md`.
  It updates the technical accounting through M3.3/M3.4, separates failed or
  parity-only optimizations from material evidence, explains why each path was
  expected to work and why it did not yet produce V3-level performance, and
  lists the remaining generic runtime optimizations with explicit success and
  stop rules.
  Its fresh Claude review attempt timed out without substantive output and is
  recorded in
  `docs/reviews/external_ai_blocked_phoenix_v3_performance_failure_root_cause_remaining_optimizations_cn_2026-06-22.md`;
  Codex recorded the document as an internal technical accounting only in
  `docs/reviews/codex_phoenix_v3_performance_failure_root_cause_remaining_optimizations_cn_record_2026-06-22.md`.
  This is not fresh 2-AI release consensus and does not authorize release,
  public speedup wording, broad V3-over-V2 wording, or full all-app pod rerun.
- The next redo-era dominant hotpath selection is recorded in
  `docs/rebuild/v3/phoenix_v3_next_dominant_engine_hotpath_selection_2026-06-22.md`.
  It does not reopen the old 13-row promotion queue. It selects
  `prepared_execution_session_runner` as the current Phoenix P0 because V3 now
  needs a productized prepared execution/session layer that actually routes
  reusable primitives with explicit backend/partner, phase accounting,
  residency metadata, and release/public-claim flags false.
- Claude's external review of the core-gap packet is recorded in
  `docs/reviews/claude_phoenix_v3_external_review_2026-06-22.md` and
  machine-ingested at
  `docs/rebuild/v3/phoenix_v3_core_gaps_external_verdict_intake_2026-06-22.json`.
  Status line:
  `external_verdict_obtained_claude_approve_blocked_not_release`. Verdict:
  `approve_blocked_not_release`. Direction: continue with redirect to Gap 1.
  Release remains blocked, broad V3-over-V2 wording remains blocked, and the
  major-version mandate is not overridden.
- Claude's companion Set A / Set B release-bar proposal is recorded in
  `docs/reviews/phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md`.
  It is a measurement-design recommendation only, not an authorization or gate
  change by itself. Before another all-app pod run, freeze Set A
  residency/multi-phase probes and Set B ceiling/materializing controls.
- The proposal has now been turned into a frozen measurement-control gate:
  `docs/rebuild/v3/phoenix_v3_set_a_set_b_classification_2026-06-22.json`,
  `scripts/v3_phoenix_set_ab_scorecard_gate.py`,
  `docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.json`,
  and
  `docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md`.
  Claude reviewed the gate as `approve_with_required_edits`; Codex applied the
  edits and recorded consensus in
  `docs/reviews/codex_phoenix_v3_set_a_set_b_classification_gate_2ai_consensus_2026-06-22.md`.
  Current scorecard: 52/52 rows classified, Set A geomean `1.012934x`, Set B
  geomean `1.006943x`, Set A apps over `1.05x` is `1/5` required, severe Set A
  regression is Barnes-Hut at `0.8441965x`, Set B has one sub-0.95 row
  (`librts_embree_aabb_index`), verified focused material productized probes
  are now `2/2` required after the AABB M2.1 and Hausdorff M6.1 probes.
  Therefore the focused-probe-count precondition is closed, but
  `all_app_pod_spend_authorized: false` and
  `release_candidate_under_two_number_bar: false` remain because the
  broad-scorecard blockers still stand.
- Gap-1 M1 runner smoke work is recorded in
  `docs/reports/phoenix_v3_prepared_execution_session_runner_m1_smoke_2026-06-22.md`.
  `src/rtdsl/prepared_execution.py` now has a minimal generic
  `run_prepared_execution_session` path that actually executes a caller-supplied
  prepared operation and records explicit backend/partner, prepared-session
  residency, phases, validation, and all claim flags false.
- Gap-1 M1.1 fixed-radius self-query runner binding is recorded in
  `docs/reports/phoenix_v3_fixed_radius_self_query_runner_binding_m1_1_2026-06-22.md`.
  `src/rtdsl/prepared_execution.py` now exposes
  `run_fixed_radius_count_threshold_3d_self_query_prepared_session`, which
  routes the generic `fixed_radius_count_threshold_self_query` family through
  the prepared execution/session runner and the existing
  `fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns`
  adapter. Local contract tests record `runtime_executed: true`, explicit
  partner/cache metadata, Set-A probe candidacy, and all release/public/broad/
  true-zero-copy/automatic-selection flags false. It is not yet wired into a
  real benchmark route and has no pod performance evidence.
- Gap-1 M1.2 grouped-stream route wiring is recorded in
  `docs/reports/phoenix_v3_grouped_stream_runner_route_m1_2_2026-06-22.md`.
  `PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D.run` now refreshes
  fixed-radius core flags through
  `run_fixed_radius_count_threshold_3d_self_query_prepared_session`, so the
  productized runner path is visible in one real Set-A probe route. Local gates
  pass.
- M1.2 focused pod A/B is recorded in
  `docs/reports/phoenix_v3_grouped_stream_runner_route_pod_ab_2026-06-22.md`.
  Same RTX 4000 Ada evidence shows signatures preserved and runner metadata
  present, but geomean before/after speedup is `0.9979x`. This is neutral route
  evidence, not a performance win. There is still no release, public-speedup,
  broad V3-over-V2, or all-app rerun authorization.
- Gap-1 M2 AABB native query-handle runner contract is recorded in
  `docs/reports/phoenix_v3_aabb_native_query_handle_runner_route_m2_2026-06-22.md`.
  `src/rtdsl/prepared_execution.py` now exposes
  `run_aabb_index_query_2d_range_intersection_prepared_session`, so a second
  Set-A primitive family can route through the same prepared execution/session
  runner at contract level. Local tests record `runtime_executed: true`,
  explicit backend/partner/cache metadata, Set-A probe candidacy, and all
  release/public/broad/true-zero-copy/automatic-selection flags false.
- Gap-1 M2.1 AABB route wiring is also recorded in the same report.
  `examples/current/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py::aabb_broadphase_witness_rows`
  now calls the productized runner for Embree/OptiX prepared repeat paths.
  `tests/v3_phoenix_aabb_prepare_reuse_pod_runner_test.py::test_contact_aabb_route_uses_productized_prepared_session_runner`
  verifies `productized_execution_path: prepared_execution_session_runner`,
  `runtime_executed_count: 3`, and `cache_hit_count: 2` in a route-level
  contract test.
- Gap-1 M2.1 focused AABB pod A/B is recorded in
  `docs/reports/phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md` and
  `docs/rebuild/v3/evidence/phoenix_v3_aabb_runner_m2_1_pod_ab_20260622_180241/summary.json`.
  Same RTX 4000 Ada evidence shows the productized runner visible for both
  Embree and OptiX prepared backends, `runtime_executed_count: 50`,
  `cache_hit_count: 49`, and correctness signatures preserved. OptiX vs Embree
  on the runner-backed route is `1.346x` cold-plus-collect wall and `1.738x`
  query-total. This is positive focused Set-A evidence pending external review,
  not M7 promotion, release authorization, public speedup wording, broad
  V3-over-V2 wording, or all-app rerun authorization.
- The bounded external-review request for that M2.1 candidate is
  `docs/reviews/call_for_review_phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md`.
- Claude's current core-gaps review is recorded in
  `docs/reviews/claude_phoenix_v3_core_gaps_status_and_next_work_after_claude_review_2026-06-22.md`.
  Codex accepted it in
  `docs/reviews/codex_phoenix_v3_core_gaps_status_and_next_work_after_claude_2ai_consensus_2026-06-22.md`.
  The consensus verdict is `approve_blocked_not_release`: AABB M2.1 may proceed
  toward restricted M7 review with full phase disclosure, but release, public
  speedup wording, broad V3-over-V2 wording, true-zero-copy wording, and all-app
  rerun remain unauthorized.
- The misleading grouped-reduction device-column current status was renamed to
  `m7_row_evidence_scoped_not_release_after_claude_codex_consensus`, and the
  older aggregate `release_ready` verdict is now recorded as
  `external_verdict_obtained_claude_scoped_dossier_release_ready_not_v3_release`.
- Gap-1 RTDBSCAN/component-union M3 local contract work is recorded in
  `docs/reports/phoenix_v3_rtdbscan_component_signature_runner_route_m3_2026-06-22.md`.
  `src/rtdsl/prepared_execution.py` now exposes
  `run_radius_graph_component_signature_3d_prepared_session`, an app-agnostic
  fixed-radius graph component-signature wrapper routed through
  `prepared_execution_session_runner`. Local contract tests show
  `runtime_executed: true`, explicit `partner: numba`, cache miss/hit
  behavior, and all release/public/broad/true-zero-copy/automatic-selection
  flags false. This is not pod evidence, not RTDBSCAN paper reproduction, and
  not a second Set-A material win until it is wired into a real benchmark route
  and measured on the pod.
- Gap-1 RTDBSCAN/component-union M3.1 route wiring is recorded in
  `docs/reports/phoenix_v3_rtdbscan_component_signature_runner_route_m3_1_2026-06-22.md`.
  The existing RTDBSCAN grouped-stream Numba column-signature route now calls
  `run_radius_graph_component_signature_3d_prepared_session` and records
  `prepared_execution_session_runner_used`,
  `prepared_execution_session_runner_runtime_executed_count`, and
  `prepared_execution_session_runner_cache_hit_count`. A fake-runner local
  route test executes the app branch and verifies the metadata contract.
- Gap-1 RTDBSCAN/component-union M3.1 pod A/B is recorded in
  `docs/reports/phoenix_v3_rtdbscan_component_signature_runner_route_m3_1_pod_ab_2026-06-22.md`
  and
  `docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_m3_1_pod_ab_20260622_191459/summary.json`.
  Same RTX 4000 Ada evidence shows runner metadata present, stable signatures,
  and all claim flags false, but the runner-backed OptiX route is only
  `0.5038x` geomean versus the incumbent legacy OptiX grouped-stream path.
  It is `1.4917x` versus the Embree control, but that is not sufficient for
  Set-A material evidence because the relevant incumbent is legacy OptiX. This
  is valid negative evidence, not the second Set-A material win, not release
  authorization, and not all-app rerun authorization.
- Claude reviewed the M3.1 negative classification in
  `docs/reviews/claude_phoenix_v3_rtdbscan_m3_1_pod_ab_negative_classification_review_2026-06-22.md`.
  Codex accepted the review in
  `docs/reviews/codex_phoenix_v3_rtdbscan_m3_1_pod_ab_negative_classification_2ai_consensus_2026-06-22.md`.
  Consensus verdict: `approve_blocked_not_release`. Next action is a bounded
  generic runner overhead and fingerprint correctness fix, because
  `_stable_input_fingerprint` currently performs large sequence
  `repr(tuple(value))[:2048]` work inside the hot path and is collision-prone
  as a cache-key component.
- Gap-1 M3.2 local runner fingerprint/overhead fix is recorded in
  `docs/reports/phoenix_v3_runner_fingerprint_overhead_fix_m3_2_2026-06-22.md`.
  `make_prepared_input_fingerprint` now uses a full streaming SHA-256
  sequence digest instead of truncated large sequence reprs, and the RTDBSCAN
  component-signature runner route precomputes the point-row fingerprint
  outside the measured loop. Focused local tests pass. This is local
  correctness/overhead work only; it is not pod evidence, not the second Set-A
  material win, not release authorization, and not all-app rerun authorization.
- Gap-1 M3.2 focused pod A/B is recorded in
  `docs/reports/phoenix_v3_rtdbscan_component_signature_runner_route_m3_2_pod_ab_2026-06-22.md`
  and
  `docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_m3_2_pod_ab_20260622_193805/classification_corrected.json`.
  The generic fingerprint fix recovered RTDBSCAN runner-vs-legacy from
  `0.5038x` to `0.9930x` geomean, with runner metadata present and claim flags
  false. This is successful parity recovery, not material Set-A evidence,
  because the runner is not materially faster than the incumbent legacy OptiX
  route. The raw `summary.json` field `material_set_a_candidate: true` follows
  the older parity-plus-Embree gate and is superseded by
  `classification_corrected.json`.
- Gap-1 M3.3 local repeated prepared-session runner work is recorded in
  `docs/reports/phoenix_v3_repeated_prepared_session_runner_m3_3_2026-06-22.md`.
  `src/rtdsl/prepared_execution.py` now exposes
  `run_repeated_prepared_execution_session`, which performs one cache lookup /
  prepare phase, warmup plus N measured prepared executions inside one runner
  call, and one report payload. The fixed-radius self-query, AABB query-handle,
  and radius-graph component-signature generic helpers now accept
  `measured_repeat_count` with default behavior unchanged. The runner metadata
  schema is now `rtdl.v3.phoenix.prepared_execution_session_runner.m3_3`.
  Focused local validation passes: 18 tests across the prepared runner,
  RTDBSCAN component-signature contract, and Set A/B gate. Claude reviewed the
  step as `approve_with_required_edits_not_release`; Codex applied the schema
  version bump and `measured_repeat_count=0` rejection test, then recorded
  2-AI consensus in
  `docs/reviews/codex_phoenix_v3_repeated_prepared_session_runner_m3_3_2ai_consensus_2026-06-22.md`.
  This is local contract progress only: not pod evidence, not a second material
  Set-A win, not release authorization, and not all-app pod rerun
  authorization.
- Gap-1 M3.4 focused same-pod RTDBSCAN repeated-runner A/B is recorded in
  `docs/reports/phoenix_v3_rtdbscan_repeated_runner_route_m3_4_pod_ab_2026-06-22.md`
  and
  `docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_m3_4_pod_ab_20260622_204719/summary.json`.
  The pod run used the same RTX 4000 Ada hardware and compared the productized
  repeated runner route against the relevant incumbent legacy OptiX
  grouped-stream route, plus an Embree control. Result:
  `runner_vs_legacy_geomean: 0.997557675600175`,
  `runner_vs_embree_geomean: 2.941644953697829`,
  `legacy_parity_recovered: true`, `material_set_a_candidate: false`.
  Runner metadata was present for all runner samples, repeated execution was
  true, and all claim flags stayed false. Classification: parity-preserving
  route progress only, not the second Set-A material probe. Stop RTDBSCAN as
  the immediate second material-probe path and redirect to AABB runner
  generalization or productized typed continuation. This does not authorize
  release, public speedup wording, broad V3-over-V2 wording, or a full all-app
  pod rerun.
  A fresh Claude review attempt for the parity classification timed out without
  substantive output and is recorded in
  `docs/reviews/external_ai_blocked_phoenix_v3_rtdbscan_m3_4_pod_ab_parity_classification_2026-06-22.md`.
  Codex recorded the classification in
  `docs/reviews/codex_phoenix_v3_rtdbscan_m3_4_pod_ab_parity_classification_record_2026-06-22.md`.
  This is not fresh 2-AI release consensus; it is a non-release engineering
  redirect based on the measured incumbent comparison.
- Gap-1/AABB generalization M4 local contract work is recorded in
  `docs/reports/phoenix_v3_aabb_count_runner_librts_route_m4_2026-06-22.md`.
  `src/rtdsl/prepared_execution.py` now exposes
  `run_aabb_index_query_2d_count_prepared_session`, a generic count-only AABB
  prepared-session helper for `all`, `point_contains`, `range_contains`, and
  `range_intersects`. `src/rtdsl/__init__.py` exports it. The LibRTS Embree
  count route now uses the productized prepared execution/session runner for
  warmup plus measured repeats and records
  `prepared_execution_session_runner_used`,
  `productized_execution_path: prepared_execution_session_runner`, and count
  contract metadata. Focused local validation passes: 32 tests across the
  prepared runner, RTDBSCAN route, Set A/B gate, AABB prepare-reuse,
  AABB prepared-query cache, and LibRTS AABB count runner. This is local
  contract progress only: not pod evidence, not a second material Set-A probe,
  not release authorization, and not all-app pod rerun authorization. The
  OptiX LibRTS prepared-query-set fast path has not been replaced; next work is
  a productized runner wrapper for that incumbent route before focused pod A/B.
- Hausdorff M5 was first closed as valid negative evidence in
  `docs/reviews/codex_kepler_phoenix_v3_hausdorff_m5_negative_classification_2ai_consensus_2026-06-22.md`
  because the productized runner lost to the legacy prepared OptiX front door
  by about 2-3%. The follow-up shared runner work is now recorded in
  `docs/reports/phoenix_v3_runner_metadata_overhead_reduction_m6_2026-06-22.md`
  and
  `docs/reports/phoenix_v3_runner_prepare_metric_alignment_m6_1_2026-06-22.md`.
  M6 cached prepared-session `stable_id`, removed `dataclasses.asdict()` from
  phase timing serialization, and reduced report summary scans. M6.1 separated
  native prepared-object prepare timing from outer runner prepare/cache timing,
  preserving wrapper-wall accountability while aligning the Hausdorff
  runner-vs-legacy phase-total scope.
- The M6.1 focused Hausdorff POD canary is recorded in
  `docs/reports/phoenix_v3_hausdorff_threshold_runner_m5_pod_ab_after_m6_1_2026-06-22.md`
  and accepted by Codex+Kepler in
  `docs/reviews/codex_kepler_phoenix_v3_hausdorff_m5_after_m6_1_result_2ai_consensus_2026-06-22.md`.
  Same RTX 4000 Ada evidence at 1,048,576 points per side, repeat 5, warmup 1:
  `failed_checks=[]`, runner-vs-legacy phase-total `1.0317x`, wrapper wall
  `1.0541x`, query `1.0841x`; runner-vs-Embree phase-total `1.2228x` and
  wrapper wall `1.5378x`. This is positive focused productized-runner
  Hausdorff/threshold-summary evidence, not release authorization and not
  all-app authorization.
- The Set-A/B scorecard was regenerated after adding the accepted Hausdorff
  M6.1 probe in
  `docs/reports/phoenix_v3_set_ab_scorecard_update_after_hausdorff_m6_1_2026-06-22.md`.
  Focused productized material probes are now `2/2` verified: AABB M2.1 plus
  Hausdorff M6.1. However `all_app_pod_spend_authorized` remains `false` and
  `release_candidate_under_two_number_bar` remains `false` because Set A
  geomean is still `1.012934x`, only `1/5` Set-A apps are over `1.05x`, the
  frozen all-app scorecard still contains the old Barnes-Hut severe regression
  at `0.8441965x`, and Set B still has the LibRTS Embree AABB index row below
  `0.95x`.
- M7 Barnes-Hut blocker intake is recorded in
  `docs/rebuild/v3/phoenix_v3_barnes_hut_blocker_intake_m7_2026-06-22.json`
  and
  `docs/reports/phoenix_v3_barnes_hut_blocker_intake_m7_2026-06-22.md`.
  It does not authorize release or all-app POD spend. It does record that the
  focused same-hardware generic fixed-radius OptiX symbol/cache fix covers all
  six frozen Barnes-Hut rows for planning: Barnes-Hut app geomean projects from
  `0.8441965x` to `1.008971x`, and all-row geomean projects from `1.011779x`
  to `1.032810x` if only those Barnes-Hut rows supersede. Runner parity evidence
  also remains clean: productized runner vs existing fused-control geomean
  `0.999328x`, failed checks empty, all claim flags false. Treat Barnes-Hut as
  focused-fix-covered pending full-suite validation, not as the next POD target.
  Codex+Erdos recorded 2-AI consensus in
  `docs/reviews/codex_erdos_phoenix_v3_barnes_hut_m7_blocker_reclassification_2ai_consensus_2026-06-22.md`
  with verdict `accept_m7_reclassification_not_release`; it explicitly
  authorizes no release, no public speedup claim, no broad V3-over-V2 claim, and
  no all-app POD spend.
- M8 remaining-blocker queue is recorded in
  `docs/rebuild/v3/phoenix_v3_m8_remaining_blocker_queue_2026-06-22.json` and
  `docs/reports/phoenix_v3_m8_remaining_blocker_queue_2026-06-22.md`, with
  Codex+Tesla consensus in
  `docs/reviews/codex_tesla_phoenix_v3_m8_remaining_blocker_queue_2ai_consensus_2026-06-22.md`.
  Verdict: `accept_m8_spatial_next_not_pod`. M8 keeps release/public/broad
  claims and both focused/all-app POD spend unauthorized. Planning projection
  after covered Barnes-Hut and LibRTS Embree fixes is still far below release:
  all-row geomean `1.048703x`, Set-A geomean `1.039066x`, Set-A app wins
  `1/5`. The accepted next target is non-POD local intake of
  `spatial_rayjoin_lsi_optix_topology_stream`, because the largest uncovered
  Set-A row loss is
  `goal2636_stress|spatial_rayjoin|rayjoin_lsi_authored_tiled_x2048|optix|rayjoin_optix_promoted_lsi_tiled_x2048`
  at `0.888121x`. LibRTS OptiX AABB is a watch row, not the current primary
  target.

## What Blocks Release

The top-level blocker is now the major-version performance mandate:

```text
V3 major release requires broad V2.x performance superiority
current_scoped_13_row_surface_not_v3_major_release
serious_all_app_paired_evidence_failed_release_bar
current_core_gap_external_review_blocks_release
```

The scoped external packet verdict is still recorded, but it is not V3 release
authorization:

```text
external_verdict_obtained_claude_scoped_dossier_release_ready_not_v3_release
external_verdict_obtained_claude_approve_blocked_not_release
release_authorized: false
```

The first line is historical scoped 13-row evidence. The second line is the
current core-gap verdict and is the controlling non-release engineering
redirect. Neither line authorizes V3 release.

The aggregate external-review packet is:

`docs/reviews/call_for_review_phoenix_v3_aggregate_release_readiness_13_row_2026-06-22.md`

The latest external-review blocked record is historical:

`docs/reviews/external_ai_blocked_phoenix_v3_aggregate_release_readiness_13_row_after_dossier_2026-06-22.md`

The current fallback consensus is:

`docs/reviews/codex_phoenix_v3_aggregate_release_readiness_13_row_2ai_fallback_consensus_2026-06-22.md`

The fallback consensus does not replace external release authorization. The
accepted Claude verdict also does not override the major-version performance
mandate.

Latest accepted core-gap review:

```text
verdict: approve_blocked_not_release
next_engineering_spine: rtdbscan_grouped_reduction_component_union_runner_route
all_app_rerun_authorized: false
```

## Completed Pod Run

Serious same-RT-hardware V2.14 vs Phoenix V3 evidence completed on the RTX
4000 Ada pod:

```text
run_id: phoenix_v3_serious_v2x_paired_20260622_074100
pod: root@213.173.108.14 -p 11592
key: C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
remote_base: /root/rtdl_v3_rebuild_20260620
remote_run_dir: /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_serious_v2x_paired_20260622_074100
hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.05, 20475 MiB
runner: scripts/phoenix_v3_serious_paired_v2x_runner.sh
analyzer: scripts/phoenix_v3_serious_v2x_paired_analysis.py
```

The run executes V2.14 and current Phoenix V3 on the same data and same RT
hardware:

```text
goal2626_large: --scale large --case-repeat 3
goal2636_stress: --tier stress --case-repeat 3
goal3828_full: full current benchmark scale profile runner
```

The analyzer is intentionally strict:

```text
expected_promoted_app_count: 10
missing_promoted_apps must be []
primary_metric_source_mismatch_count must be 0
overall_geomean_v3_speedup_vs_v2 must be >= 1.20x for release consideration
at least 8 of 10 app geomeans must be > 1.05x
no app geomean may be < 0.95x without accepted explanation
OptiX-vs-Embree rows must include ratio-change interpretation
```

Completed suite status:

```text
v2_14 goal2626_large rc=0
v2_14 goal2636_stress rc=0
v2_14 goal3828_full rc=0
current goal2626_large rc=0
current goal2636_stress rc=0
current goal3828_full rc=0
```

Analyzer result:

```text
same_metric_comparison_count: 52
V3 faster by >5%: 12
Within +/-5%: 35
V3 slower by >5%: 5
Geomean V3 speedup vs V2.14: 1.012x
release_consideration_eligible: false
actual_app_geomean_wins_gt_1_05x: 1
actual_app_geomean_regressions_lt_0_95x: 2
missing_promoted_apps: []
primary_metric_source_mismatch_count: 0
```

Therefore:

```text
status: redo_required
release_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

Focused supersession after the serious run:

```text
report: docs/reports/phoenix_v3_barnes_hut_symbol_cache_focused_evidence_2026-06-22.md
scope: Barnes-Hut generic prepared OptiX fixed-radius threshold hot path
result: largest Barnes-Hut OptiX losses recovered to parity/slight win
release_authorized: false
```

Second focused supersession:

```text
report: docs/reports/phoenix_v3_librts_aabb_count_cache_focused_evidence_2026-06-22.md
scope: LibRTS generic Embree AABB_INDEX_QUERY_2D count hot path
result: Embree count-only regression recovered; OptiX AABB row remains unstable/inconclusive
release_authorized: false
```

Third focused supersession:

```text
report: docs/reports/phoenix_v3_rtnn_neighbor_symbol_cache_focused_evidence_2026-06-22.md
scope: RTNN generic prepared Embree/OptiX fixed-radius 3-D neighbor symbol-cache hygiene
result: tests pass, but 12-row RTNN focused geomean is 1.001x; no material release-performance gain
release_authorized: false
```

Fourth focused supersession:

```text
report: docs/reports/phoenix_v3_fixed_radius_symbol_cache_focused_evidence_2026-06-22.md
scope: generic Embree/OptiX prepared fixed-radius count-threshold symbol/library cache
result: 17-row focused geomean is 1.062x; useful cleanup, not release-performance proof
release_authorized: false
```

Fifth focused supersession:

```text
report: docs/reports/phoenix_v3_fixed_radius_graph_self_query_refresh_focused_evidence_2026-06-22.md
scope: grouped-stream core-flag refresh uses prepared self-query device-search columns
result: contract/device-residency metadata improved; 3-row CuPy A/B geomean is 0.998x, no material speedup
release_authorized: false
```

M9 Spatial/RayJoin LSI OptiX local mechanics intake:

```text
report: docs/reports/phoenix_v3_spatial_lsi_optix_m9_intake_2026-06-22.md
json: docs/rebuild/v3/phoenix_v3_spatial_lsi_optix_m9_intake_2026-06-22.json
review: docs/reviews/codex_heisenberg_phoenix_v3_m9_spatial_lsi_optix_2ai_consensus_2026-06-22.md
scope: Spatial/RayJoin LSI OptiX active Set-A row loss
result: 0.888x is a V3-vs-V2 15.4 microsecond same-metric micro-regression outside the productized runner, not an OptiX-vs-Embree failure
verdict: approve_m9_enter_m10_no_pod
release_authorized: false
public_speedup_claim_authorized: false
focused_pod_spend_authorized: false
all_app_pod_spend_authorized: false
M10_local_implementation_authorized: true
```

M10/M11 Spatial/RayJoin segment-intersection runner:

```text
M10_report: docs/reports/phoenix_v3_spatial_segment_intersection_runner_m10_2026-06-22.md
M10_review: docs/reviews/codex_linnaeus_phoenix_v3_m10_spatial_segment_intersection_2ai_consensus_2026-06-22.md
M11_report: docs/reports/phoenix_v3_spatial_segment_intersection_runner_m11_pod_ab_2026-06-22.md
M11_json: docs/rebuild/v3/phoenix_v3_spatial_segment_intersection_runner_m11_pod_ab_2026-06-22.json
M11_evidence: docs/rebuild/v3/evidence/phoenix_v3_spatial_lsi_segment_runner_m10_focused_pod_ab_20260622
scope: one focused POD A/B, old LSI dense-count route vs productized segment-intersection topology-stream route
result: productized-runner coverage pass; performance fail
old_hot_median_sec: 0.00012440979480743408
new_inner_hot_median_sec: 0.00013191252946853638
new_runner_median_sec: 0.00020245462656021118
old_vs_new_inner_speedup: 0.9431234114656877x
old_hot_vs_new_runner_speedup: 0.6145070474367939x
release_authorized: false
public_speedup_claim_authorized: false
all_app_pod_spend_authorized: false
```

M12/M13 Spatial/RayJoin runner-overhead reduction and guarded rerun:

```text
M12_report: docs/reports/phoenix_v3_runner_overhead_m12_local_2026-06-22.md
M12_review: docs/reviews/codex_schrodinger_phoenix_v3_m12_runner_overhead_2ai_consensus_2026-06-22.md
M13_report: docs/reports/phoenix_v3_spatial_segment_intersection_runner_m13_pod_ab_2026-06-22.md
M13_json: docs/rebuild/v3/phoenix_v3_spatial_segment_intersection_runner_m13_pod_ab_2026-06-22.json
M13_call_for_review: docs/reviews/call_for_review_phoenix_v3_m13_spatial_segment_intersection_pod_rerun_2026-06-22.md
M13_consensus: docs/reviews/codex_rawls_phoenix_v3_m13_spatial_segment_intersection_2ai_consensus_2026-06-22.md
M13_evidence: docs/rebuild/v3/evidence/phoenix_v3_spatial_lsi_segment_runner_m13_focused_pod_ab_20260622
scope: exact repeat of M11 focused POD A/B after generic runner finalize-once overhead reduction
result: overhead improved versus M11, but still speed-fail versus the old route
old_hot_median_sec: 0.0001227855682373047
new_inner_hot_median_sec: 0.00012449920177459717
new_runner_median_sec: 0.00015626102685928345
old_vs_new_inner_speedup: 0.9862357869539198x
old_hot_vs_new_runner_speedup: 0.7857721832832689x
m13_vs_m11_new_runner_speedup: 1.2956181757497736x
verdict: accept_m13_stop_spatial_retarget
Spatial_LSI_productized_runner_coverage: true
Spatial_LSI_speed_coverage: false
release_authorized: false
public_speedup_claim_authorized: false
focused_pod_spend_authorized_for_another_run: false
all_app_pod_spend_authorized: false
next_action: stop Spatial LSI speed work and retarget the next Set-A runtime-trunk family
```

M14 runtime-trunk retarget/status reconciliation:

```text
M14_json: docs/rebuild/v3/phoenix_v3_m14_runtime_trunk_retarget_status_2026-06-22.json
M14_report: docs/reports/phoenix_v3_m14_runtime_trunk_retarget_status_2026-06-22.md
M14_call_for_review: docs/reviews/call_for_review_phoenix_v3_m14_runtime_trunk_retarget_status_2026-06-22.md
M14_consensus: docs/reviews/codex_bernoulli_phoenix_v3_m14_runtime_trunk_retarget_2ai_consensus_2026-06-22.md
scope: reconcile post-M13 runtime-trunk evidence before any new POD/all-app decision
negative_or_coverage_only:
  - Spatial LSI M13: coverage only, runner/old hot 0.785772x
  - RTDBSCAN Step 1: structural only, runner vs legacy 0.994858x
  - RayJoin PIP Step 2: structural only, runner vs legacy total-repeat 0.973754x
positive_focused_runtime_trunk_evidence:
  - Barnes-Hut: runner vs existing fused control 0.999328x; historical OptiX/runner 12.730691x
  - RTNN repeat50: accepted second Set-A material probe; runner vs legacy runner-wall 1.370176x
  - Hausdorff M6.1: accepted positive focused probe; runner vs legacy wrapper-wall 1.054105x, but not strict third material Set-A evidence
verdict: accept_m14_need_third_strict_probe
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
focused_pod_spend_authorized_now: false
next_action: M15 local audit for a third strict Set-A probe, likely Triangle or another family with a real runtime performance source; no POD until 2-AI approval
```

M15 third strict Set-A probe audit:

```text
M15_json: docs/rebuild/v3/phoenix_v3_m15_third_strict_set_a_probe_audit_2026-06-22.json
M15_report: docs/reports/phoenix_v3_m15_third_strict_set_a_probe_audit_2026-06-22.md
M15_call_for_review: docs/reviews/call_for_review_phoenix_v3_m15_third_strict_set_a_probe_audit_2026-06-22.md
M15_consensus: docs/reviews/codex_bernoulli_phoenix_v3_m15_third_strict_set_a_probe_2ai_consensus_2026-06-22.md
verdict: accept_m15_triangle_m16_local_runner_wiring_no_pod
selected_candidate: triangle_counting
selected_capability: prepared_graph_chunk_non_graph_stream
triangle_counts_as_third_strict_set_a_material_probe_now: false
triangle_next_local_implementation_target: true
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
next_action: M16 local-only Triangle prepared_execution_session_runner wiring/protocol; no POD until M16 review authorizes it
```

M16 Triangle runner wiring:

```text
M16_json: docs/rebuild/v3/phoenix_v3_m16_triangle_runner_wiring_2026-06-22.json
M16_report: docs/reports/phoenix_v3_m16_triangle_runner_wiring_2026-06-22.md
M16_call_for_review: docs/reviews/call_for_review_phoenix_v3_m16_triangle_runner_wiring_2026-06-22.md
M16_consensus: docs/reviews/codex_bernoulli_phoenix_v3_m16_triangle_runner_wiring_2ai_consensus_2026-06-22.md
verdict: accept_m16_prepare_m17_focused_pod_protocol_no_run
helper: run_ray_triangle_weighted_summary_device_output_stream_prepared_session
primitive: ray_triangle_weighted_summary_device_output_stream
productized_execution_path: prepared_execution_session_runner
m16_closes_local_runner_wiring: true
triangle_counts_as_third_strict_set_a_material_probe_now: false
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
next_action: M17 protocol-only focused Triangle POD plan/review; do not run POD unless M17 2-AI review explicitly authorizes one focused run
```

M17 Triangle focused POD protocol:

```text
M17_json: docs/rebuild/v3/phoenix_v3_m17_triangle_focused_pod_protocol_2026-06-22.json
M17_report: docs/reports/phoenix_v3_m17_triangle_focused_pod_protocol_2026-06-22.md
M17_call_for_review: docs/reviews/call_for_review_phoenix_v3_m17_triangle_focused_pod_protocol_2026-06-22.md
M17_consensus: docs/reviews/codex_bernoulli_phoenix_v3_m17_triangle_focused_pod_protocol_2ai_consensus_2026-06-22.md
verdict: accept_m17_authorize_m18_runner_harness_no_pod
row: Generated K4 clique ladder, 80,000 cliques; oracle_triangle_count=320000
protocol_sufficient_for_m18_harness_only: true
runner_harness_is_pre_run_blocker: true
triangle_counts_as_third_strict_set_a_material_probe_now: false
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
next_action: M18 local Triangle runner harness implementation/tests only; no POD until a later 2-AI verdict explicitly authorizes one focused run
```

M18 Triangle runner harness:

```text
M18_json: docs/rebuild/v3/phoenix_v3_m18_triangle_runner_harness_2026-06-22.json
M18_report: docs/reports/phoenix_v3_m18_triangle_runner_harness_2026-06-22.md
M18_call_for_review: docs/reviews/call_for_review_phoenix_v3_m18_triangle_runner_harness_2026-06-22.md
M18_initial_review: docs/reviews/codex_bernoulli_phoenix_v3_m18_triangle_runner_harness_initial_review_2026-06-22.md
M18_second_review: docs/reviews/codex_bernoulli_phoenix_v3_m18_triangle_runner_harness_second_review_2026-06-22.md
M18_final_pod_authorization: docs/reviews/codex_bernoulli_phoenix_v3_m18_triangle_runner_harness_final_pod_authorization_2026-06-22.md
M18_attempt_1_failed_env_intake: docs/reports/phoenix_v3_m18_triangle_focused_pod_failed_env_intake_2026-06-22.md
M18_attempt_1_evidence: docs/rebuild/v3/evidence/phoenix_v3_triangle_runner_m18_focused_pod_ab_20260622
M19_call_for_review: docs/reviews/call_for_review_phoenix_v3_m19_triangle_env_corrected_rerun_2026-06-22.md
M19_claude_authorization: docs/reviews/claude_phoenix_v3_m19_triangle_env_corrected_rerun_review_2026-06-22.md
M19_2ai_consensus: docs/reviews/codex_claude_phoenix_v3_m19_triangle_env_corrected_rerun_2ai_consensus_2026-06-22.md
M19_result_report: docs/reports/phoenix_v3_m19_triangle_env_corrected_pod_result_2026-06-22.md
M19_result_review: docs/reviews/claude_phoenix_v3_m19_triangle_env_corrected_pod_result_review_2026-06-22.md
M19_result_consensus: docs/reviews/codex_claude_phoenix_v3_m19_triangle_result_2ai_consensus_2026-06-22.md
M19_evidence: docs/rebuild/v3/evidence/phoenix_v3_triangle_runner_m18_focused_pod_ab_venv_20260622
script: scripts/v3_phoenix_triangle_runner_m18_pod_ab.py
helper: run_ray_triangle_weighted_summary_device_output_stream_prepared_session
device_output_executor: prepare_ray_batch_any_hit_weighted_sum_device_output_graph_executor
initial_verdict: revise_m18_harness
initial_blocker: weighted_hit_sum_out.get was inside measured runner body while hot_path_host_materialization=false
second_verdict: revise_m18_harness
second_blockers: control oracle checks missing for Embree/legacy; edge-file checksum not recorded/enforced
final_verdict: accept_m18_authorize_one_focused_triangle_pod
revision: scalar read/finalization moved to finalize_weighted_summary_device_output_stream after measured repeats
revision_2: real runs fail closed on K4 edge-file sha256/edge-count/byte-count and all three variant oracle checks
local_verification: 58 tests OK; dry-run failed_check_count=0; wording gate pass; py_compile OK
attempt_1_status: consumed focused authorization, failed wrong-interpreter environment gate, no performance evidence
attempt_1_command_interpreter: /usr/bin/python3
attempt_1_failure: CuPy missing from /usr/bin/python3, so legacy OptiX and productized runner produced no payloads
attempt_1_passed_gates: K4 edge sha256/edge-count/byte-count pass; RTX 4000 Ada hardware gate pass; Embree same-contract control oracle match
verified_project_venv: /root/rtdl_v3_rebuild_20260620/.venv/bin/python has cupy present and numba present
M19_authorization: Claude authorized one venv-based replacement run after subprocess sys.executable prelaunch check
M19_result_status: accepted by Claude result review as third strict Set-A material runtime-trunk probe
M19_exit_code: 0
M19_failed_check_count: 0
M19_all_variant_oracle_checks_passed: true
M19_productized_execution_path: prepared_execution_session_runner
M19_runtime_trunk_executes_end_to_end: true
M19_runner_vs_embree_hot_speedup: 2414.807809480132x
M19_runner_vs_embree_wall_speedup: 13.408780700958467x
M19_runner_vs_legacy_wall_speedup: 2.1167140613609914x
third_strict_set_a_material_probe_closed: true
another_focused_triangle_rerun_authorized: false
Set_A_Set_B_scorecard_probe_count: 3/2 verified focused productized material probes after M19
Set_A_Set_B_scorecard_all_app_status: still blocked by current Set-A severe regression/app-win shortfall and Set-B parity row
M20_scorecard_sync_report: docs/reports/phoenix_v3_m20_scorecard_sync_after_triangle_m19_2026-06-22.md
M20_call_for_review: docs/reviews/call_for_review_phoenix_v3_m20_scorecard_sync_after_triangle_2026-06-22.md
M20_claude_review: docs/reviews/claude_phoenix_v3_m20_scorecard_sync_after_triangle_review_2026-06-22.md
M20_2ai_consensus: docs/reviews/codex_claude_phoenix_v3_m20_scorecard_sync_2ai_consensus_2026-06-22.md
M20_verdict: authorize_m20_all_app_protocol_preparation_no_run
M21_authorized_scope: prepare all-app POD protocol packet only; no run
M21_required_protocol_bars: Barnes-Hut app geomean >=0.90x, librts_embree_aabb_index >=0.95x, Set-B geomean >=0.98x, no new app-level severe regression below 0.90x; Set-A geomean and app wins reported exactly but not pass/fail for this evidence run
M21_protocol_json: docs/rebuild/v3/phoenix_v3_m21_all_app_pod_protocol_2026-06-23.json
M21_protocol_md: docs/rebuild/v3/phoenix_v3_m21_all_app_pod_protocol_2026-06-23.md
M21_report: docs/reports/phoenix_v3_m21_all_app_pod_protocol_2026-06-23.md
M21_call_for_review: docs/reviews/call_for_review_phoenix_v3_m21_all_app_pod_protocol_2026-06-23.md
M21_claude_prompt: docs/reviews/claude_prompt_phoenix_v3_m21_all_app_pod_protocol_2026-06-23.txt
M21_review_status: Claude review in progress; no substantive verdict recorded yet
M21_runner_guard: scripts/phoenix_v3_serious_paired_v2x_runner.sh now uses PYTHON_BIN/base venv explicitly and fails before benchmarks on missing interpreter or sys.executable mismatch
M21_protocol_gate: scripts/v3_phoenix_m21_all_app_protocol_gate.py evaluates future all-app summary.json against M21 fail-closed bars; old 1.012x summary fails this stricter gate
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
next_action: wait for M21 external review; only exact verdict authorize_m21_one_all_app_pod_run can unlock one all-app POD run, otherwise revise/focus as directed
```

## External Review Discipline

Follow:

`docs/rebuild/v3/phoenix_v3_bounded_external_review_protocol_2026-06-22.md`

Rule:

```text
one complete packet
one bounded automated attempt in the active work loop
no substantive verdict before timeout -> record external_review_not_obtained
release promotion only after a real external verdict
continue V3 cleanup while preserving claim boundaries
```

Do not rediscover Claude. The known Windows binary is:

```text
C:\Users\Lestat\.local\bin\claude.exe
```

If Claude quota/auth/tooling fails, record the exact failure and keep working on
non-release V3 cleanup. Do not call Gemini again until the user explicitly says
the Google policy/tooling issue is solved; use Antigravity or another explicit
external-AI fallback for review seats instead.

## Next Useful Work

1. Keep current docs synchronized with the `redo_required` V3 state.
2. Continue the new redo-era P0 from
   `docs/rebuild/v3/phoenix_v3_next_dominant_engine_hotpath_selection_2026-06-22.md`:
   focused productized-runner probes are now `2/2`, but the current all-app
   scorecard still blocks full pod spend and release. Do not spend more
   Phoenix time on RayDB-specific grouped_sum variants unless the work lands in
   a shared grouped_reduction or productized runner primitive.
3. Apply Claude's `approve_blocked_not_release` redirect: Gap 1 is the critical
   path. M7 intake classifies Barnes-Hut as focused-fix-covered for planning,
   pending full-suite validation. M8 classifies LibRTS Embree AABB as covered
   pending full-suite validation and LibRTS OptiX AABB as a watch row. M9
   classifies Spatial/RayJoin LSI OptiX as a productized-runner coverage gap,
   not an OptiX failure. M10 implements the generic
   `segment_intersection_topology_stream` prepared-session route. M11 confirms
   this is coverage-clean on POD but slower than the old route. M12 reduces
   generic runner overhead locally. M13 confirms the overhead reduction on POD
   but still speed-fails versus the old route. Do not run all-app from M13 and
   do not run another Spatial LSI POD. The reviewed verdict is
   `accept_m13_stop_spatial_retarget`. M14 reconciles the newer runtime-trunk
   state: RTDBSCAN and RayJoin are structural-only; Barnes-Hut and RTNN count
   as material runtime-trunk Set-A evidence; Hausdorff is positive focused
   evidence but not a strict third material Set-A probe. M14 verdict is
   `accept_m14_need_third_strict_probe`; do not prepare all-app protocol yet.
   M15 selects Triangle as the next local target. M16 closes local Triangle
   runner wiring only; it does not count Triangle as the third strict Set-A
   material probe and does not authorize POD. M17 freezes the focused Triangle
   POD protocol, but Bernoulli accepts it only for M18 local harness work; the
   runner harness is a pre-run blocker.
4. Do not spend more Phoenix time on RTNN symbol lookup as a release-performance
   hypothesis; it has been measured and classified no-material-speedup.
   Do not spend Phoenix time on public Spatial/RayJoin speedup wording unless
   author result-count parity and paper-scope proof are separately obtained.
5. Build and run a serious same-RT-hardware V3-vs-V2.x benchmark plan across
   all benchmark apps as language/runtime stress tests after enough broad
   generic runtime fixes accumulate.
6. Keep package-install, broad V3-over-V2 until proven, true-zero-copy, V4/C ABI/embedding,
   hardware-portability, public Spatial speedup, and whole-app claims forbidden.
7. Promote only reusable runtime capabilities, not app-specific patches.
8. Hausdorff M5 is closed as valid negative evidence by
   `docs/reviews/codex_kepler_phoenix_v3_hausdorff_m5_negative_classification_2ai_consensus_2026-06-22.md`.
   This negative evidence has been superseded for the current path by the M6.1
   focused POD canary and Codex+Kepler result consensus. Do not rerun the same
   Hausdorff sample hoping for noise. Treat the M6.1 result as one positive
   focused productized-runner Hausdorff/threshold-summary probe, then move to
   the next Phoenix V3 runtime-trunk gate. Use
   `docs/reports/phoenix_v3_trunk_first_pod_resource_plan_2026-06-22.md` for
   the current pod budget: focused validations only, no all-app run until the
   controlling Set-A/Set-B gate says preconditions are met and 2-AI review
   authorizes the spend.
9. The immediate remaining V3 blockers are no longer "focused probe count,"
   "rerun Barnes-Hut until it looks good," "fix LibRTS Embree again," or
   "prove OptiX is not slow." M7 records Barnes-Hut as focused-fix-covered
   pending full-suite validation. M8 records LibRTS Embree as
   focused-fix-covered pending full-suite validation. M9 records Spatial/RayJoin
   LSI OptiX as approved for local M10 productized-runner work only. M10/M11
   then shows productized-runner coverage but not speed. M12/M13 shows generic
   runner-overhead improvement but still no Spatial LSI speed win. M10-M13 must
   stay classified as generic runtime-trunk coverage/overhead work, not
   RayJoin-specific app feature work; M11/M13 must not be counted as speed wins.
   M14 required a third strict Set-A material probe before all-app protocol.
   M15 selected Triangle as the correct next local target but did not count the
   old Triangle row as the third strict probe. M16 implemented and reviewed the
   local Triangle prepared_execution_session_runner wiring. M17 reviewed the
   protocol and authorized M18 local harness work only. M18/M19 closed Triangle
   as the third strict Set-A material probe after the venv-corrected focused
   POD run, and M20 authorized only all-app protocol preparation. M21 has now
   prepared the protocol, patched the serious paired runner's interpreter
   preflight, and added a dedicated M21 protocol gate. Do not run all-app POD
   unless the M21 external review returns exactly
   `authorize_m21_one_all_app_pod_run`.
   Current continuation note: M37 added the generic component-union prepared
   execution session route and was accepted by Claude. M38 then froze the
   focused component-union POD protocol and obtained Codex+Claude consensus:
   `accept_m38_authorize_one_focused_component_union_pod_after_harness_gate`.
   M38 itself ran no POD and authorizes no release, all-app run, public speedup
   claim, V4, C ABI, embedding, or true-zero-copy wording. The next allowed
   step is M39 local harness implementation. If the harness passes local gates,
   enforces same generated input across variants, confirms RT hardware, prints
   heartbeat output, emits M37 metadata, and preserves the `2h / $0.50` cap, one
   focused component-union POD run is authorized by the M38 consensus.
   M39 has now implemented the harness
   `scripts/v3_phoenix_component_union_m38_pod_ab.py`, passed focused and full
   `v3_rebuild` gates (`119` modules, `619` tests, OK), and obtained
   Codex+Claude consensus:
   `accept_m39_authorize_one_focused_component_union_pod`. The next allowed
   action is exactly one focused component-union POD run with `--variant all`
   and `--require-rt-hardware`. Interpret timeout/exit `124`, correctness
   failure, metadata failure, or speed below bar as blocked/negative/coverage
   evidence, not a release claim. All-app POD and V3 release remain blocked.
   M40 then executed that single focused component-union POD run and M41
   selected grouped reduction as the second local Step-2 family. M41 serious
   free local at `262144` rows / `1024` groups was contract-positive but
   performance-blocked (`runner_vs_cpu_hot_speedup=0.4979998501868343x`).
   M42 diagnosed the blocker: the current Numba offsets grouped-reduction
   kernel parallelizes over `group_count`, so the M41 shape launched only
   `4` blocks. M42 added generic launch-shape metadata and ran one bounded free
   local lx1 shape at `262144` rows / `65536` groups, producing failed checks
   `0`, runtime trunk executes end-to-end `true`, internal residency `true`,
   hot-path host materialization `false`, `program_count=256`, and
   `runner_vs_cpu_hot_speedup=6.443935850755532x`. Codex+Claude consensus:
   `accept_m42_shape_positive_require_tiled_kernel`. M42 is not release,
   all-app, or paid-POD authorization. The next authorized work is M43:
   local-only tiled/row-parallel generic grouped-reduction kernel work, measured
   first on the original blocked `262144 x 1024` shape.
   M43 local implementation found that Numba tiled variants improved but stayed
   CPU-slower on the original shape (`0.6217x` and `0.6777x`). The productized
   CuPy RawKernel warp prepared-session route cleared the original CPU-hot gate:
   `runner_vs_cpu_hot_speedup=3.454249350723889x`,
   `runner_vs_legacy_hot_speedup=6.670789510185146x`, failed checks `0`,
   runtime trunk executes end-to-end `true`, internal residency `true`, and
   hot-path host materialization `false`. Evidence:
   `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m43_lx1_cupy_warp_original_262144x1024_20260623_153707/`.
   Trusted-offset follow-up on the same shape cleared the wall caveat:
   `runner_vs_cpu_hot_speedup=3.634392783864349x`,
   `runner_vs_legacy_hot_speedup=3.3163301846618403x`,
   `runner_vs_legacy_wall_speedup=15.409127696720203x`; evidence:
   `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m43_lx1_cupy_warp_trust_offsets_262144x1024_20260623_154342/`.
   Full `v3_rebuild` passed `120` modules / `627` tests. M43 is now closed for
   bounded Step-2 grouped-reduction technical purposes through user-provided
   Antigravity GUI external review plus Codex consensus. Antigravity verdict:
   `accept_m43_original_shape_hot_gate_cleared_continue_step2`; external
   review:
   `docs/reviews/antigravity_phoenix_v3_m43_grouped_reduction_cupy_warp_review_2026-06-23.md`;
   Codex+Antigravity consensus:
   `docs/reviews/codex_antigravity_phoenix_v3_m43_grouped_reduction_cupy_warp_2ai_consensus_2026-06-23.md`.
   This does not authorize paid POD, all-app run, release, public speedup claim,
   broad V3-over-V2 claim, V4, embedding, C ABI, or true-zero-copy work. Next
   authorized work is Step-2 scorecard synchronization and next-family planning
   under the same generic runtime-trunk discipline.
   Claude review debt remains open for M43 and must be paid when Claude is
   available:
   `docs/reviews/phoenix_v3_claude_review_debt_register_2026-06-23.md`.
   User rule from 2026-06-23: major decisions, or at least each six-hour
   sustained-work interval, require `2+` AI consensus; any goal-completion audit
   requires `3-AI` review/consensus before the goal is called complete.
   M44 has now synchronized the Step-2 scorecard after M43:
   `docs/reports/phoenix_v3_m44_step2_scorecard_sync_after_m43_2026-06-23.md`.
   Call for review:
   `docs/reviews/call_for_review_phoenix_v3_m44_step2_scorecard_sync_after_m43_2026-06-23.md`.
   Claude helper:
   `scripts/run_claude_phoenix_v3_m44_scorecard_sync_review_2026_06_23.ps1`.
   M44 recommendation, pending external review, is to avoid all-app/paid POD and
   move next to M45 Barnes-Hut severe-regression root-cause audit as generic
   runtime-trunk work around prepared graph / aggregate-tree / fused
   continuation behavior. This recommendation is not goal-complete and not
   release/all-app/POD authorization.
   M45 read-only audit then found Barnes-Hut should be treated as
   focused-fix-covered for planning, pending next reviewed full-suite
   validation, not as the next active coding target:
   `docs/reports/phoenix_v3_m45_barnes_hut_blocker_reaudit_2026-06-23.md`.
   Call for review:
   `docs/reviews/call_for_review_phoenix_v3_m45_barnes_hut_blocker_reaudit_2026-06-23.md`.
   Claude helper:
   `scripts/run_claude_phoenix_v3_m45_barnes_hut_reaudit_review_2026_06_23.ps1`.
   M45 preserves that the old frozen `barnes_hut=0.844x` was concentrated in
   OptiX node-coverage rows and that M24/M7 already projected a focused generic
   prepared-query fix; do not start more Barnes-Hut route tuning before review.
   The next active engineering target should move to remaining non-covered
   scorecard blockers, especially LibRTS Set-B parity or another Set-A app-win
   shortfall, pending external review.
   M46 read-only LibRTS status:
   `docs/reports/phoenix_v3_m46_librts_set_b_watch_rows_status_and_next_protocol_2026-06-23.md`.
   Call for review:
   `docs/reviews/call_for_review_phoenix_v3_m46_librts_set_b_watch_rows_status_2026-06-23.md`.
   Claude helper:
   `scripts/run_claude_phoenix_v3_m46_librts_watch_rows_review_2026_06_23.ps1`.
   M46 keeps M27's accepted retain-output fix, but leaves both LibRTS watch rows
   open: OptiX cold single-shot is `improved_not_closed`; Embree 32768 is a
   `stability_watch_blocker`. Next recommended work is M47 protocol preparation
   for a focused cold-start/stability run, not a code rewrite, not all-app, and
   not paid POD before review.
   M47 protocol draft is prepared:
   `docs/rebuild/v3/phoenix_v3_m47_librts_stability_protocol_2026-06-23.md`.
   Call for review:
   `docs/reviews/call_for_review_phoenix_v3_m47_librts_stability_protocol_2026-06-23.md`.
   Claude helper:
   `scripts/run_claude_phoenix_v3_m47_librts_stability_protocol_review_2026_06_23.ps1`.
   M47 does not run anything and does not authorize paid POD. It defines two
   focused scenarios, eight paired samples each, alternating V2.14/current
   order, green/yellow/red labels, and stop conditions. Only an explicit
   external verdict may authorize exactly one focused LibRTS stability POD run.
   M47 local dry-run/intake harness has also been implemented:
   `scripts/v3_phoenix_m47_librts_stability_protocol.py`, with tests
   `tests/v3_phoenix_m47_librts_stability_protocol_test.py`. Focused validation:
   `py_compile` passed and `Ran 5 tests OK`. Dry-run evidence:
   `docs/rebuild/v3/evidence/phoenix_v3_m47_librts_stability_protocol_dry_run_20260623/`;
   summary status
   `m47_librts_stability_protocol_dry_run_no_pod_not_release`, `execute=false`,
   `schedule_row_count=32`, `failed_check_count=0`, and all claim flags false.
   Real execution requires `--execute` plus token
   `M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED`, so the harness itself does not
   authorize or run POD.
   M44 goal-completion audit is prepared but not complete:
   `docs/reports/phoenix_v3_m44_goal_completion_audit_pending_3ai_2026-06-23.md`.
   Completion review packet:
   `docs/reviews/call_for_review_phoenix_v3_m44_goal_completion_audit_2026-06-23.md`.
   Antigravity/user-GUI prompt:
   `docs/reviews/antigravity_prompt_phoenix_v3_m44_goal_completion_audit_2026-06-23.txt`.
   Current prompt status: refreshed after M52 so a user-forwarded GUI fallback
   reviews the current packet, not the older M47-only completion shape.
   Antigravity GUI review:
   `docs/reviews/antigravity_phoenix_v3_m44_goal_completion_audit_review_2026-06-23.md`.
   Codex+Antigravity interim consensus:
   `docs/reviews/codex_antigravity_phoenix_v3_m44_goal_completion_audit_interim_2ai_consensus_2026-06-23.md`.
   Claude completion review:
   `docs/reviews/claude_phoenix_v3_m44_goal_completion_audit_recorded_review_2026-06-23.md`.
   Final 3-AI consensus:
   `docs/reviews/codex_claude_antigravity_phoenix_v3_m44_goal_completion_3ai_consensus_2026-06-23.md`.
   Antigravity verdict:
   `accept_m44_substantively_done_but_do_not_mark_complete_until_3ai`.
   Local review-debt/completion-gate validation:
   `docs/reports/phoenix_v3_m44_review_debt_gate_and_rebuild_validation_2026-06-23.md`.
   Claude helper:
   `scripts/run_claude_phoenix_v3_m44_goal_completion_audit_review_2026_06_23.ps1`.
   Current Codex read:
   `accept_m44_goal_complete_pending_claude_debt_backfill`.
   The active M44 process goal may be marked complete because the required
   `3-AI` completion review is saved. Claude is still owed backfill review for
   M43-M52 as discrete milestone reviews. This completion does not authorize
   V3 release, POD, all-app, public speedup wording, or broad V3-over-V2
   claims. Default external-review order remains:
   Codex calls Claude first. Gemini is disabled until the user restores it.
   Antigravity is only a temporary user-GUI fallback, not the normal review
   path.
   M48 local continuation while Claude is unavailable:
   `docs/reports/phoenix_v3_m48_librts_stability_harness_execution_safety_2026-06-23.md`.
   Review request:
   `docs/reviews/call_for_review_phoenix_v3_m48_librts_stability_harness_execution_safety_2026-06-23.md`.
   Claude helper:
   `scripts/run_claude_phoenix_v3_m48_librts_harness_execution_safety_review_2026_06_23.ps1`.
   M48 hardens the M47 harness with preflight capture, tree-specific cwd,
   fixture/contract mismatch checks, and metadata-failure red classification.
   Evidence:
   `docs/rebuild/v3/evidence/phoenix_v3_m48_librts_stability_harness_execution_safety_dry_run_20260623/`.
   M48 ran no benchmark and authorizes no POD, all-app, release, public speedup
   claim, broad V3-over-V2 claim, V4, embedding, C ABI, or true-zero-copy.
   M49 current blocker queue refresh:
   `docs/reports/phoenix_v3_m49_current_blocker_queue_after_m48_2026-06-23.md`.
   Review request:
   `docs/reviews/call_for_review_phoenix_v3_m49_current_blocker_queue_after_m48_2026-06-23.md`.
   Claude helper:
   `scripts/run_claude_phoenix_v3_m49_current_blocker_queue_review_2026_06_23.ps1`.
   M49 says old M8 Spatial/RayJoin next-target wording is stale if read as route
   tuning; after M35 it is allowed only as generic topology-stream residency and
   full-M3 phase-accounting work. It authorizes no POD/all-app/release.
   Claude review-debt batch helper for M43-M49 and M44 completion audit:
   `scripts/run_claude_phoenix_v3_review_debt_backfill_2026_06_23.ps1`.
   M50 then hardened the Spatial/RayJoin topology-stream M3 runner so stale
   historical commands cannot accidentally spend POD. The runner now emits a
   dry-run packet by default; in short, it is dry-run by default and requires
   both `--execute` and token
   `M50_SPATIAL_TOPOLOGY_STREAM_M3_POD_AUTHORIZED` for any real execution.
   Report:
   `docs/reports/phoenix_v3_m50_spatial_topology_stream_runner_fail_closed_2026-06-23.md`.
   Review request:
   `docs/reviews/call_for_review_phoenix_v3_m50_spatial_topology_runner_fail_closed_2026-06-23.md`.
   Claude helper:
   `scripts/run_claude_phoenix_v3_m50_spatial_topology_runner_fail_closed_review_2026_06_23.ps1`.
   Current external-review priority remains: Codex calls Claude first. Gemini is
   disabled until the user restores it. Antigravity is only an occasional
   user-forwarded GUI fallback, not the normal path. M50 authorizes no POD,
   all-app run, release, public speedup claim, broad V3-over-V2 claim, V4,
   embedding, C ABI, or true-zero-copy work.
   Direct M44 completion review attempt after updating the packet to M50:
   Claude returned session-limit/quota reset and Gemini returned
   `IneligibleTierError / UNSUPPORTED_CLIENT`. Blocked record:
   `docs/reviews/external_review_blocked_phoenix_v3_m44_completion_claude_gemini_2026-06-23.md`.
   This is not consensus and does not complete the active M44 goal.
   M51 prepared the LibRTS authorized-run runbook:
   `docs/rebuild/v3/phoenix_v3_m51_librts_authorized_runbook_2026-06-23.md`.
   Review request:
   `docs/reviews/call_for_review_phoenix_v3_m51_librts_authorized_runbook_2026-06-23.md`.
   Claude helper:
   `scripts/run_claude_phoenix_v3_m51_librts_authorized_runbook_review_2026_06_23.ps1`.
   M51 still runs nothing. It only says that any future LibRTS execution must
   first get the exact external verdict
   `authorize_m47_one_focused_librts_stability_pod_run`, must dry-run first,
   must use separate current and V2.14 roots, and must copy back full evidence.
   It authorizes no POD, all-app, release, public speedup claim, broad
   V3-over-V2 claim, V4, embedding, C ABI, or true-zero-copy work.
   M52 audited the POD runner authorization surface:
   `docs/reports/phoenix_v3_m52_pod_runner_authorization_surface_audit_2026-06-23.md`.
   Review request:
   `docs/reviews/call_for_review_phoenix_v3_m52_pod_runner_authorization_surface_audit_2026-06-23.md`.
   Claude helper:
   `scripts/run_claude_phoenix_v3_m52_pod_surface_audit_review_2026_06_23.ps1`.
   Current whitelist: only M47 and M50 are active fail-closed token-gated
   execution surfaces, and neither may execute now. Historical
   `v3_phoenix_*pod*` scripts are not current authorization unless a new
   review packet re-gates and re-authorizes them.
  Completion status: Claude explicitly accepted the saved Antigravity M44
  completion review as adequate for the original M44 objective while Claude
  reviewed the current packet through M52. Therefore the M44 process goal is
  complete pending Claude debt backfill. This is not release/POD/all-app
  authorization.
  M53 current state:
  `docs/reviews/call_for_review_phoenix_v3_m53_open_claude_debt_backfill_2026-06-23.md`;
  `docs/reviews/claude_phoenix_v3_m53_open_debt_backfill_recorded_review_2026-06-23.md`;
  `docs/reviews/codex_claude_phoenix_v3_m53_open_debt_backfill_2ai_consensus_2026-06-23.md`.
  Claude verdict:
  `accept_m53_open_debt_backfill_no_authorization_continue_m54`.
  Per-debt result: M43, M44-scorecard, and M45-M52 all accepted. This pays the
  open Claude bundle backfill at the technical-review level. M53 goal
  completion is now satisfied by the user-required 3-AI completion audit:
  Codex + Claude + Antigravity. M53 does not authorize
  POD/all-app/release/public speedup claims. Carry forward P1 items before any
  future LibRTS run: supply a real V2.14 root and explicit Linux/POD Python
  paths; do not use the dry-run placeholders literally.
  M54 recommended next item from Claude: prepare a separate bounded external
  review packet requesting authorization for exactly one focused LibRTS
  stability POD run using the M47/M48/M51 suite. This is a recommendation to
  prepare a review packet only, not authorization to run.
  M53 goal-completion audit:
  `docs/reports/phoenix_v3_m53_goal_completion_audit_pending_3ai_2026-06-23.md`.
  Review packet:
  `docs/reviews/call_for_review_phoenix_v3_m53_goal_completion_audit_2026-06-23.md`.
  Antigravity review:
  `docs/reviews/antigravity_phoenix_v3_m53_goal_completion_audit_review_2026-06-23.md`.
  Final 3-AI consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m53_goal_completion_3ai_consensus_2026-06-23.md`.
  Antigravity prompt:
  `docs/reviews/antigravity_prompt_phoenix_v3_m53_goal_completion_audit_2026-06-23.txt`.
  Gemini M53 completion attempt:
  `docs/reviews/external_review_blocked_phoenix_v3_m53_completion_gemini_2026-06-23.md`.
  Gemini remains unavailable and is now disabled by user instruction until the
  user restores it, but the saved Antigravity review supplies the third
  external-AI seat for M53 completion only. User installed Antigravity CLI at
  `C:\Users\Lestat\AppData\Local\agy\bin\agy.exe`; use that absolute path for
  future Antigravity review attempts if Claude is unavailable. M54 remains not
  authorized.
  Final M53 local validation after recording the Antigravity CLI/Gemini-disabled
  rule: `v3_rebuild` passed with module_count 126 and 644 tests in 77.784s.
  Captured output:
  `docs/reports/phoenix_v3_m53_v3_rebuild_after_antigravity_cli_rule_2026-06-23.stdout.txt`;
  stderr:
  `docs/reports/phoenix_v3_m53_v3_rebuild_after_antigravity_cli_rule_2026-06-23.stderr.txt`.
  M54 status: completed by 3-AI consensus. Claude authorized exactly one
  focused M47 LibRTS stability POD run with verdict
  `authorize_m47_one_focused_librts_stability_pod_run`; Antigravity accepted
  M54 goal completion with verdict
  `accept_m54_goal_complete_authorization_narrow_one_run_no_release`; Codex
  recorded final 3-AI consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m54_goal_completion_3ai_consensus_2026-06-23.md`.
  The only authorized token is `M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED`, for
  one run of `scripts/v3_phoenix_m47_librts_stability_protocol.py` only. Before
  using the token, the executor must identify real current and V2.14 roots plus
  explicit Linux/POD Python paths, run the target-machine dry-run, and confirm
  `failed_check_count=0`. This does not authorize V3 release, all-app
  benchmarking, broad paid POD campaign, public speedup wording, broad
  V3-over-V2 claims, V4, embedding, C ABI, true-zero-copy claims, repeated M47
  runs, changed scenario parameters, or watch-row closure without later
  external review of copied evidence.
  M54 completion audit:
  `docs/reports/phoenix_v3_m54_goal_completion_audit_2026-06-23.md`.
  Final M54 validation: `v3_rebuild` passed with module_count 127 and 649 tests
  in 79.993s. Captured output:
  `docs/reports/phoenix_v3_m54_v3_rebuild_after_authorization_consensus_2026-06-23.stdout.txt`;
  stderr:
  `docs/reports/phoenix_v3_m54_v3_rebuild_after_authorization_consensus_2026-06-23.stderr.txt`.
  M55 status: completed by 3-AI consensus. The one M54-authorized M47 focused
  LibRTS stability POD run was executed on `NVIDIA RTX 4000 Ada Generation`
  driver `550.127.05` with current root `/root/rtdl_v3_rebuild_20260620/current`
  and V2.14 root `/root/rtdl_v3_rebuild_20260620/v2_14`. Current pod SSH key
  that worked: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`;
  plain `id_ed25519` failed and `id_ed25519_rtdl_codex` had local load
  permission failure. Target dry-run and execution evidence were copied back:
  `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_target_dry_run_20260623_2339/`;
  `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_execution_20260623_2340/`.
  M55 intake:
  `docs/reports/phoenix_v3_m55_librts_authorized_pod_run_intake_2026-06-23.md`.
  Claude verdict:
  `accept_m55_valid_red_watch_rows_open_no_rerun`.
  Antigravity verdict:
  `accept_m55_goal_complete_valid_red_no_rerun_no_release`.
  Final 3-AI consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m55_goal_completion_3ai_consensus_2026-06-23.md`.
  Final read: both `optix_cold_single_shot` and `embree_32768_stress` remain
  `red_failure_watch_row_open` because `set_b_control_candidate_missing` appears
  in current metadata. The M54 token is consumed. No rerun, watch-row closure,
  release, all-app benchmark, public speedup wording, broad V3-over-V2 claim,
  V4, embedding, C ABI, or true-zero-copy claim is authorized. Next allowed work
  is local diagnosis/repair planning for `set_b_control_candidate_missing` and,
  only if needed, a future separate authorization packet.
  M55 completion audit:
  `docs/reports/phoenix_v3_m55_goal_completion_audit_2026-06-23.md`.
  Final M55 validation: `v3_rebuild` passed with module_count 128 and 653 tests
  in 76.999s. Captured output:
  `docs/reports/phoenix_v3_m55_v3_rebuild_after_valid_red_consensus_2026-06-23.stdout.txt`;
  stderr:
  `docs/reports/phoenix_v3_m55_v3_rebuild_after_valid_red_consensus_2026-06-23.stderr.txt`.
  M56 status: completed by 3-AI consensus. M56 locally diagnosed the M55
  `set_b_control_candidate_missing` failure without POD rerun. The M55 current
  payloads did use `prepared_execution_session_runner` and the expected AABB
  primitive contracts; the red cause is missing Set-B metadata exposure or
  insufficient target-root signature, not proof that the runner was skipped.
  Local source already exposes Set-B metadata, so M56 added a required M47
  preflight row `current_librts_set_b_source_signature` in
  `scripts/v3_phoenix_m47_librts_stability_protocol.py`. Any future M47 run
  must pass that source-signature check before measured samples execute.
  M56 report:
  `docs/reports/phoenix_v3_m56_librts_set_b_metadata_diagnosis_and_preflight_repair_2026-06-23.md`.
  Claude verdict:
  `accept_m56_local_diagnosis_and_preflight_repair_no_pod_authorization`.
  Antigravity verdict:
  `accept_m56_goal_complete_preflight_repair_no_pod_no_release`.
  Final 3-AI consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m56_goal_completion_3ai_consensus_2026-06-23.md`.
  Completion audit:
  `docs/reports/phoenix_v3_m56_goal_completion_audit_2026-06-23.md`.
  Final M56 validation: `v3_rebuild` passed with module_count 129 and 657 tests
  in 76.102s. Captured output:
  `docs/reports/phoenix_v3_m56_v3_rebuild_after_3ai_completion_2026-06-23.combined.txt`.
  M56 does not authorize another M47 run, release, all-app benchmark, public
  speedup wording, broad V3-over-V2 claim, V4, embedding, C ABI,
  true-zero-copy claim, or watch-row closure. Next POD work requires a new
  separately reviewed authorization packet.
  M57 status: completed by 3-AI consensus and authorizes exactly one future
  source-signature-gated M47 LibRTS rerun, but no M57 POD run has been executed
  yet. Authorized token:
  `M57_SOURCE_SIGNATURE_GATED_M47_RERUN_AUTHORIZED`. Authorization consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m57_one_rerun_authorization_3ai_consensus_2026-06-23.md`.
  Completion audit:
  `docs/reports/phoenix_v3_m57_goal_completion_audit_2026-06-23.md`.
  M57 fixed a code-level gap before final authorization: if
  `execute_preflight()` returns errors, `scripts/v3_phoenix_m47_librts_stability_protocol.py`
  now returns `STATUS_FAILED` before `execute_schedule()` runs. The behavior is
  tested by `test_execute_aborts_before_samples_when_preflight_fails`.
  Required next-run sequence: target dry-run first with `--run-preflight`;
  confirm `failed_checks=[]`; confirm
  `current_librts_set_b_source_signature` exists, returns 0, and stdout
  contains `"failed": []`; only then run exactly once with
  `--execute --authorization-token M57_SOURCE_SIGNATURE_GATED_M47_RERUN_AUTHORIZED`.
  Use unchanged scenarios and exactly 8 paired samples. Copy back full evidence.
  Do not close watch rows or make performance/public claims from raw output; a
  later evidence-intake review is required. Final M57 validation:
  `v3_rebuild` passed with module_count 130 and 662 tests in 76.205s. Captured
  output:
  `docs/reports/phoenix_v3_m57_v3_rebuild_after_3ai_authorization_2026-06-23.combined.txt`.
  M58 status: completed by 3-AI consensus. M58 executed the one M57-authorized
  source-signature-gated LibRTS M47 POD rerun. Before execution, target dry-run
  was run with `--run-preflight`; `failed_checks=[]`; source-signature preflight
  returned 0 and stdout contained `"failed": []`. Execution evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_m58_librts_m57_authorized_execution_20260624_0055/`.
  Dry-run evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_m58_librts_m57_authorized_target_dry_run_20260624_0054/`.
  Intake:
  `docs/reports/phoenix_v3_m58_librts_m57_authorized_pod_rerun_intake_2026-06-23.md`.
  Consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m58_rerun_intake_3ai_consensus_2026-06-23.md`.
  Completion audit:
  `docs/reports/phoenix_v3_m58_goal_completion_audit_2026-06-23.md`.
  Final read: M55 metadata failure is cleared (`current_metadata_failures=[]`
  across paired rows), but both LibRTS watch rows remain open/yellow:
  `embree_32768_stress` geomean 1.030501x, median 1.022440x, pass 6/8;
  `optix_cold_single_shot` geomean 0.979485x, median 0.938318x, pass 3/8.
  Claude explicitly warned the OptiX row is a real stability concern, not a
  success. M58 authorizes no second M57 run, no watch-row closure, no release,
  no all-app benchmark, no public speedup wording, no broad V3-over-V2 claim,
  no V4, no embedding, no C ABI, and no true-zero-copy claim. Final M58
  validation: `v3_rebuild` passed with module_count 131 and 666 tests in
  73.434s. Captured output:
  `docs/reports/phoenix_v3_m58_v3_rebuild_after_3ai_completion_2026-06-23.combined.txt`.
  M59 status: completed by 3-AI consensus. M59 decided the LibRTS/AABB yellow
  open rows are accepted Set-B control limitations, not an active Step-2
  runtime-trunk gap. No additional LibRTS POD run is authorized. Claude carried
  forward a P2/P1 risk: the OptiX cold single-shot row remains below the Set-B
  0.98x bar and must be explained or resolved before any release wording.
  Consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m59_librts_yellow_open_decision_3ai_consensus_2026-06-23.md`.
  Completion audit:
  `docs/reports/phoenix_v3_m59_goal_completion_audit_2026-06-23.md`.
  Final M59 validation: `v3_rebuild` passed with module_count 132 and 670 tests.
  M60 status: completed by 3-AI consensus. M60 selected the Spatial/RayJoin
  point-location topology-stream lane as the next local Step-2 Set-A family,
  strictly scoped to generic topology-stream prepared-handle/internal residency
  and full-M3 accounting. It explicitly does not authorize RayJoin app tuning,
  RTDL-beats-RayJoin claims, POD, all-app, release, or true-zero-copy wording.
  Consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m60_step2_set_a_selection_3ai_consensus_2026-06-23.md`.
  Completion audit:
  `docs/reports/phoenix_v3_m60_goal_completion_audit_2026-06-23.md`.
  Final M60 validation: `v3_rebuild` passed with module_count 133 and 675 tests.
  M61 status: completed by 3-AI consensus. M61 built the local no-POD
  topology-stream gap ledger and phase-bridge contract. It labeled the 2.2815x
  Spatial/RayJoin delta as `internal_routing_delta_not_public_row`, not a public
  speedup row, and kept M50 fail-closed. Claude accepted but left three P2s for
  M62: replace text-mining with behavioral metadata checks, explicitly set
  `true_zero_copy_claim_authorized=false` in topology-stream runner metadata,
  and add an internal-delta sanity cap.
  Ledger:
  `docs/rebuild/v3/phoenix_v3_m61_topology_stream_gap_ledger_2026-06-23.json`.
  Consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m61_topology_stream_gap_ledger_3ai_consensus_2026-06-23.md`.
  Completion audit:
  `docs/reports/phoenix_v3_m61_goal_completion_audit_2026-06-23.md`.
  Final M61 validation: `v3_rebuild` passed with module_count 134 and 683 tests.
  M62 status: completed by 3-AI consensus. M62 closed the M61 P2s locally:
  both topology-stream family runners now explicitly write
  `metadata["true_zero_copy_claim_authorized"] = False`; the M61 ledger executes
  two stable fake probes through the real point-location and
  segment-intersection topology-stream prepared-session runners; the internal
  routing delta now has a `1.0x < delta < 10.0x` sanity cap; and tests use
  strict identity checks so `None` cannot pass as false. Claude first caught a
  wrong broad patch placement; the final code was corrected and Claude's final
  recorded review accepted with no blocking issue. Antigravity also accepted.
  Report:
  `docs/reports/phoenix_v3_m62_topology_stream_contract_gate_tightening_2026-06-23.md`.
  Claude:
  `docs/reviews/claude_phoenix_v3_m62_topology_stream_contract_gate_tightening_recorded_review_2026-06-23.md`.
  Antigravity:
  `docs/reviews/antigravity_phoenix_v3_m62_topology_stream_contract_gate_tightening_review_2026-06-23.md`.
  Consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m62_topology_stream_contract_gate_tightening_3ai_consensus_2026-06-23.md`.
  Completion audit:
  `docs/reports/phoenix_v3_m62_goal_completion_audit_2026-06-23.md`.
  Final M62 validation: `v3_rebuild` passed with module_count 135 and 686 tests.
  Captured JSON:
  `docs/reports/phoenix_v3_m62_v3_rebuild_after_3ai_completion_2026-06-23.json`.
  Next allowed work: continue local Phoenix V3 Step-2 topology-stream
  implementation. Still no V3 release, no all-app run, no POD spend, no public
  speedup wording, no broad V3-over-V2 claim, no RTDL-beats-RayJoin claim, no
  true-zero-copy claim, no V4, no embedding, no C ABI, and no watch-row closure.
  M63 status: completed by 3-AI consensus. M63 closed the M61 phase-bridge gap
  at the prepared-session runner level by adding
  `_topology_stream_m3_bridge_metadata`, a generic bridge from prepared-execution
  output metadata to `topology_stream_m3_phase_table_v1` and
  `topology_stream_prepared_handle_v1`. Both point-location and
  segment-intersection topology-stream runners now attach
  `prepared_execution_to_topology_stream_m3_bridge_v1`; ledger probes for both
  families report `complete_non_authorizing_m3_bridge`,
  `topology_stream_m3_phase_table_complete=true`, and `failed_check_count=0`.
  Claude and Antigravity accepted with verdict
  `accept_m63_topology_stream_m3_phase_bridge_continue_local_step2_no_pod_no_release`.
  Claude suggested a non-blocking sentinel comment around `prepared_query_sec`;
  Codex applied the comment. Report:
  `docs/reports/phoenix_v3_m63_topology_stream_m3_phase_bridge_2026-06-23.md`.
  Claude:
  `docs/reviews/claude_phoenix_v3_m63_topology_stream_m3_phase_bridge_recorded_review_2026-06-23.md`.
  Antigravity:
  `docs/reviews/antigravity_phoenix_v3_m63_topology_stream_m3_phase_bridge_review_2026-06-23.md`.
  Consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m63_topology_stream_m3_phase_bridge_3ai_consensus_2026-06-23.md`.
  Completion audit:
  `docs/reports/phoenix_v3_m63_goal_completion_audit_2026-06-23.md`.
  Final M63 validation: `v3_rebuild` passed with module_count 136 and 690 tests.
  Captured JSON:
  `docs/reports/phoenix_v3_m63_v3_rebuild_after_3ai_completion_2026-06-23.json`.
  Next allowed work remains local Step-2 topology-stream runtime work only; no
  V3 release, all-app run, POD spend, public speedup wording, broad V3-over-V2
  claim, RTDL-beats-RayJoin claim, external device-buffer interop claim,
  future-version host integration work, low-level host interface work, or
  watch-row closure is authorized.
  M64 status: completed by 3-AI consensus. M64 promoted the M63 M3 bridge into
  `audit_prepared_execution_session_metadata`: topology-stream Set-A candidates
  now require a complete non-authorizing bridge before `accept_step3_ready`.
  Non-topology and Set-B runners short-circuit through the new gate so they are
  not damaged. Point-location tests include a negative broken-bridge case that
  now becomes `incomplete_step3_audit`; segment-intersection tests verify the
  positive bridge-ready path. Claude and Antigravity accepted with verdict
  `accept_m64_topology_stream_step3_audit_gate_continue_local_step2_no_pod_no_release`.
  Claude carried forward non-blocking M65 hardening: add negative tests for
  bridge contract mismatch, bridge status mismatch, and bridge public-row/M7
  flag mistakes, plus optionally mirror the negative test in the segment path.
  Report:
  `docs/reports/phoenix_v3_m64_topology_stream_step3_audit_gate_2026-06-23.md`.
  Claude:
  `docs/reviews/claude_phoenix_v3_m64_topology_stream_step3_audit_gate_recorded_review_2026-06-23.md`.
  Antigravity:
  `docs/reviews/antigravity_phoenix_v3_m64_topology_stream_step3_audit_gate_review_2026-06-23.md`.
  Consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m64_topology_stream_step3_audit_gate_3ai_consensus_2026-06-23.md`.
  Completion audit:
  `docs/reports/phoenix_v3_m64_goal_completion_audit_2026-06-23.md`.
  Final M64 validation: `v3_rebuild` passed with module_count 137 and 692 tests.
  Captured JSON:
  `docs/reports/phoenix_v3_m64_v3_rebuild_after_3ai_completion_2026-06-23.json`.
  During validation, the wording gate caught a handoff line that used
  future-version technical terms forbidden in current V3 public-surface scans;
  that line was rewritten to V3-safe boundary language before the successful
  full run. Next allowed work remains local only, with no release, all-app run,
  POD spend, public speedup wording, broad V3-over-V2 claim,
  RTDL-beats-RayJoin claim, external device-buffer interop claim,
  future-version host integration work, low-level host interface work, or
  watch-row closure authorized.
  M65 status: completed by 3-AI consensus. M65 closed M64's Step3 bridge
  negative-test carry-forward. Point-location and segment-intersection
  topology-stream paths now both exercise five bad bridge variants: partial M3
  phase table, bad bridge contract, bad bridge status, public-row authorization
  flag true, and M7 authorization flag true. Each variant asserts
  `incomplete_step3_audit`, `topology_stream_m3_bridge_ready=false`, the
  missing `complete_non_authorizing_topology_stream_m3_bridge` sentinel, and
  the disaggregated bridge sub-field that must fail: contract, completion, or
  non-authorization. M65 also added an explicit non-topology-stream Set-A
  bypass test so the topology-stream bridge gate does not over-constrain other
  runtime families. Claude and Antigravity accepted with verdict
  `accept_m65_topology_stream_step3_negative_hardening_continue_local_no_pod_no_release`.
  Report:
  `docs/reports/phoenix_v3_m65_topology_stream_step3_audit_negative_hardening_2026-06-23.md`.
  Claude:
  `docs/reviews/claude_phoenix_v3_m65_topology_stream_step3_audit_negative_hardening_recorded_review_2026-06-23.md`.
  Antigravity:
  `docs/reviews/antigravity_phoenix_v3_m65_topology_stream_step3_audit_negative_hardening_review_2026-06-23.md`.
  Consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m65_topology_stream_step3_audit_negative_hardening_3ai_consensus_2026-06-23.md`.
  Completion audit:
  `docs/reports/phoenix_v3_m65_goal_completion_audit_2026-06-23.md`.
  Final M65 validation: `v3_rebuild` passed with module_count 138 and 696 tests.
  Captured JSON:
  `docs/reports/phoenix_v3_m65_v3_rebuild_after_3ai_completion_2026-06-23.json`.
  Next allowed work remains local only, with no release, all-app run, POD spend,
  public speedup wording, broad V3-over-V2 claim, RTDL-beats-RayJoin claim,
  external device-buffer interop claim, future-version host integration work,
  low-level host interface work, or watch-row closure authorized.
  M66 status: completed by 3-AI consensus as a non-go redirect, not a run
  authorization. M66 hardened the Spatial/RayJoin topology-stream runner with
  a new M66 source-signature-gated token, `--run-preflight`, required current
  source-signature checks, and a fail-closed preflight path that emits
  `STATUS_FAILED` before samples if required checks fail. After rereading the
  serious 2026-06-22 RayJoin focused POD packet, M66 rejected a repeat
  topology-stream POD run because the productized runner and incumbent both
  call the same native scalar-count route and prior measured ratios were
  `0.973465x` hot query, `0.973754x` total repeat, and `0.794180x` process
  wall. Next work is local Barnes-Hut phase-structure pre-audit: identify
  whether that incumbent path has a non-zero physical phase the runner can
  compress before any run authorization is requested. Claude and Antigravity
  accepted with verdict
  `accept_m66_topology_stream_pod_authorization_rejected_continue_barnes_hut_pre_audit_no_pod_no_release`.
  Report:
  `docs/reports/phoenix_v3_m66_topology_stream_pod_authorization_non_go_2026-06-23.md`.
  Claude:
  `docs/reviews/claude_phoenix_v3_m66_topology_stream_pod_authorization_non_go_recorded_review_2026-06-23.md`.
  Antigravity:
  `docs/reviews/antigravity_phoenix_v3_m66_topology_stream_pod_authorization_non_go_review_2026-06-23.md`.
  Consensus:
  `docs/reviews/codex_claude_antigravity_phoenix_v3_m66_topology_stream_pod_authorization_non_go_3ai_consensus_2026-06-23.md`.
  Completion audit:
  `docs/reports/phoenix_v3_m66_goal_completion_audit_2026-06-23.md`.
  M66 added gate:
  `tests/v3_phoenix_m66_topology_stream_pod_authorization_non_go_gate_test.py`.
  During full validation, the M61 ledger first exposed an M50-to-M66 token
  handoff mismatch; `scripts/v3_phoenix_m61_topology_stream_gap_ledger.py`
  was updated and the M61 ledger JSON/Markdown regenerated so the fail-closed
  surface recognizes the M66 active token, the superseded M50 token absence,
  and the source-signature preflight. Final M66 validation: `v3_rebuild`
  passed with module_count 139 and 703 tests. Captured JSON:
  `docs/reports/phoenix_v3_m66_v3_rebuild_after_3ai_completion_2026-06-23.json`.
  Next allowed work remains local Barnes-Hut phase-structure pre-audit only,
  with no release, all-app run, POD spend, public speedup wording, broad
  V3-over-V2 claim, RTDL-beats-RayJoin claim, external device-buffer interop
  claim, future-version host integration work, low-level host interface work,
  or watch-row closure authorized.

## Goal-Level Decision Audit

Decision: downgrade Phoenix V3 from scoped `release_ready` to `redo_required`
because V3 must prove broad V2.x performance superiority as a language/runtime.

1. Was I foolish? Yes.
2. If yes, what actions made it foolish? I let scoped app-row evidence stand in
   for the broader V3 language/runtime performance promise.
3. Was there another path? Yes. Treat benchmark apps as stress tests for
   reusable runtime mechanisms and require broad V2.x improvement before release.
4. Can I now try a different path? Yes. Use this current handoff plus the
   redo mandate as the entry point, keep release blocked, and rerun serious
   all-app V3-vs-V2.x evidence before V3 can exist.


