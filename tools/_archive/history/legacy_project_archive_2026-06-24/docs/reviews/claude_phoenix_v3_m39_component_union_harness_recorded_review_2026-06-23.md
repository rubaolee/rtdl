# Recorded External Review: Phoenix V3 M39 Component-Union Harness

Date: 2026-06-23

Reviewer: Claude

Raw review:

- `docs/reviews/claude_phoenix_v3_m39_component_union_harness_review_2026-06-23.raw.md`

## Verdict

`accept_m39_authorize_one_focused_component_union_pod`

## Recorded Interpretation

Claude accepts the M39 harness as satisfying the M38 harness gate. The verdict
authorizes exactly one focused component-union POD run under the M38 consensus
conditions. It does not authorize all-app POD, V3 release, public speedup
wording, broad V3-over-V2 wording, V4 work, C ABI work, embedding work, or
true-zero-copy wording.

## Accepted Conditions

- Use `--variant all --require-rt-hardware` so same-point-set enforcement and
  the OptiX hardware gate are active.
- Use the reviewed M38 row parameters unless a new consensus revises them.
- Interpret outcomes fail-closed:
  - pass: material Set-A candidate only if all M38 bars pass;
  - fail: negative or coverage-only evidence;
  - timeout / exit `124`: blocked evidence, not a speed claim.
- If runner vs Embree hot speedup is below `1.20x`, runner vs Embree wall
  speedup is below `1.20x`, runner vs legacy wall is below `0.98x`, or required
  metadata flags fail, the result is not material release evidence.

## Non-Blocking Note

Claude noted that `component_labels_contract` and
`component_label_outputs_present` are hardcoded for Embree and legacy variants,
but accepted this because `signature_from_numba_label_columns()` requires label
columns and `failure_checks()` catches missing canonical signatures. This is not
a blocker.

## Goal-Level Decision Audit

Decision: accept the M39 external review and allow one focused POD run under
the M38/M39 gates.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   It would be foolish to treat the authorization as release evidence or all-app
   permission. The recorded verdict is narrower.

3. Was there another path?

   Yes. Ask for more reviews before any focused POD. Given M38 and M39 both now
   have Codex+Claude agreement, that would add delay without reducing the main
   measurement risk.

4. Can I now try a different path that actually solves the problem?

   Yes. Run exactly one focused POD, copy artifacts back, and interpret the
   result fail-closed.
