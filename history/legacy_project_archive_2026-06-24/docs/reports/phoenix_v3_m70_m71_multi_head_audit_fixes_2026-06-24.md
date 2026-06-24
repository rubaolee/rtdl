# Phoenix V3 M70/M71 Multi-Head Audit Fixes

Date: 2026-06-24

Status: `multi_head_audit_fixes_complete_pending_claude_backfill_no_execution_no_pod_no_release`

## Findings From Multi-Head Audit

Head B and Head C independently found three issues in the M70/M71 backfill
closure path:

1. The Claude backfill intake recognized reject/block/revise verdict labels and
   could accidentally treat them as accepted if the text gates passed.
2. The M71 dry-run JSON used `source_surface.metadata_fields` with values such
   as `"release_authorized": true` to mean "field present", which could be
   misread by simple scanners as authorization.
3. The M70/M71 backfill prompt/call/intake did not explicitly carry the V4,
   embedding, C ABI, and true-zero-copy prohibitions.

## Actions Taken

- Split M70/M71 verdict handling into recognized verdict labels and accepting
  verdict labels. Reject, block, and revise labels now remain recognized but
  cannot produce `claude_backfill_intake_accept_no_authorization`.
- Replaced M71 `source_surface.metadata_fields` boolean presence map with
  `metadata_fields_present` and `metadata_fields_missing` arrays. All
  `*_authorized` boolean fields remain false-only.
- Added V4, embedding, C ABI, and true-zero-copy prohibitions to:
  - `scripts/v3_phoenix_m70_m71_claude_backfill_intake.py`
  - `docs/reviews/call_for_review_phoenix_v3_m70_m71_claude_backfill_2026-06-24.md`
  - `scratch/claude_prompt_phoenix_v3_m70_m71_backfill_2026-06-24.txt`
  - `docs/reviews/phoenix_v3_claude_review_debt_register_2026-06-23.md`
  - `docs/reports/phoenix_v3_m70_m71_backfill_packet_and_register_status_2026-06-24.md`
  - M70/M71 generated protocol reports and call-for-review files.
- Added/updated tests so non-accept verdicts are blocked, M71 field-presence
  metadata cannot contain `"*_authorized": true`, and current packets/prompts
  preserve the expanded non-authorization block.

## Validation

Focused gate:

```text
py -3 -m unittest tests.v3_phoenix_m70_rtnn_focused_protocol_gate_test tests.v3_phoenix_m71_rtnn_local_harness_dry_run_gate_test tests.v3_phoenix_m70_m71_final_3ai_consensus_test tests.v3_phoenix_m70_m71_goal_completion_audit_test tests.v3_phoenix_m70_m71_claude_backfill_intake_test tests.v3_phoenix_m70_m71_claude_backfill_packet_gate_test tests.v3_release_wording_gate_test
Ran 32 tests
OK
```

Full V3 rebuild:

```text
py -3 scripts/run_test_matrix.py --group v3_rebuild --json-out docs/reports/phoenix_v3_m70_m71_multi_head_fixes_v3_rebuild_2026-06-24.json
module_count=148
Ran 751 tests
OK
```

## Remaining Blocker

The two required Claude backfill review files are still missing until Claude is
run after reset:

- `docs/reviews/claude_phoenix_v3_m70_rtnn_focused_protocol_recorded_review_2026-06-23.md`
- `docs/reviews/claude_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_recorded_review_2026-06-23.md`

M70/M71 remain not goal-complete.

## Non-Authorization

This fix record does not authorize:

- no V3 release
- no all-app benchmark run
- no POD spend
- no paid POD spend
- no focused POD spend
- no runbook execution
- no benchmark execution
- no public speedup wording
- no broad V3-over-V2 wording
- no whole-app speedup wording
- no paper reproduction wording
- no RT-core speedup wording
- no V4 work
- no embedding
- no C ABI
- no true-zero-copy claim
- no automatic partner selection
- no route-specific RTNN app tuning
- no watch-row closure

## Goal-Level Decision Audit

Decision: act on multi-head audit findings before running Claude backfill.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? Not applicable.
3. Was there another path? Yes. I could have waited for Claude and left local
   fail-closed gaps in place, but that would waste the review and risk a false
   readiness result.
4. Can I now try a different path? Yes. The better path is now active: local
   gates are stricter, full V3 rebuild passes, and Claude can review the
   hardened packet after reset.

