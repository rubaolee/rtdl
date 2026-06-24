# Codex Consensus: Phoenix V3 Grouped-Reduction Device-Column Claude Supersession

Date: 2026-06-22

Status: `claude_codex_consensus_complete_after_subagent_gap_supersession_2026-06-22`

## Scope

This consensus supersedes the procedural review gap in the earlier
device-column grouped-reduction packet. The old closure used a Codex subagent
as the second AI after Claude/Gemini CLI attempts failed. Under the current
Phoenix refresh rule, a Codex subagent does not satisfy the external-AI side of
2-AI consensus.

This file records the corrected closure after a real Claude external review.

## Inputs

External Claude review:

```text
docs/reviews/claude_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_review_2026-06-22.md
verdict: approve-with-required-fixes
row_decision: promote_both_rows
P0 findings: none
P1 findings: status-field supersession and source-manifest scope acknowledgement
```

Updated packet:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.json
```

Historical substitute review, retained only as history:

```text
docs/reviews/codex_subagent_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_review_2026-06-21.md
docs/reviews/codex_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2ai_consensus_2026-06-21.md
docs/reviews/external_ai_blocked_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.md
```

## P1 Fixes Applied

P1-A is fixed:

```text
current_packet_external_review_status:
  claude_external_approve_with_required_fixes_p1_applied_2026-06-22
current_packet_2ai_consensus_status:
  claude_codex_consensus_complete_after_subagent_gap_supersession_2026-06-22
local_gate_reading:
  m7_qualified_row_scoped_after_claude_codex_consensus
```

P1-B is fixed:

```text
source_manifest_does_not_cover_orchestration_wrappers: true
manifested_benchmark_entry_point: scripts/v3_0_m28_raydb_prepared_grouped_refresh.py
raw_json_version_confirms_manifested_entry_point: true
future reruns should expand manifest scope
```

The Markdown packet now has a `Manifest scope note` explaining that the source
manifest hashes the runtime, benchmark app, `VERSION`, and measured M28
benchmark entry point, but not the local orchestration wrappers.

## Consensus Decision

Codex accepts Claude's external review after applying both P1 fixes.

The following exact rows remain supplemental M7-qualified row-scoped evidence:

```text
grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups
grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups
```

They are accepted only as exact prepared `grouped_reduction` rows under the
approved wording. The existing scalar-broadcast grouped-reduction row remains
retained and is not replaced.

## Non-Authorization

This consensus does not authorize:

- Phoenix V3 release;
- broad V3-over-V2 speedup wording;
- whole-RayDB or whole-database acceleration;
- true-zero-copy wording;
- automatic backend or partner selection wording;
- `218.248x` as a headline or public end-to-end speedup.

## Goal-Level Decision Audit

Decision: keep both device-column grouped-reduction rows as supplemental
row-scoped M7 evidence after real Claude external review superseded the old
subagent-only gap and after both P1 fixes were applied.

1. Was I foolish?
   No for this corrected decision.
2. If yes, what actions made the decision foolish?
   The foolish action would have been leaving the old `subagent_codex` status
   in place after rereading the refresh rule.
3. Was there another path?
   Yes. I could demote both rows to pending until external review, but Claude
   is now available and has reviewed the packet.
4. Can I now try a different path?
   Yes. Preserve the rows with corrected Claude/Codex provenance, keep release
   blocked, and continue Phoenix work on shared runtime paths.
