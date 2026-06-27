# Codex + Claude + Antigravity Consensus: Phoenix V3 M59 LibRTS Yellow/Open Decision

Date: 2026-06-23

Consensus status:

```text
m59_librts_set_b_yellow_open_limit_continue_set_a_step2_no_release
```

## Scope

M59 decides how to treat the M58 LibRTS/AABB yellow/open evidence after M58
was accepted as a valid one-run intake. It does not execute POD.

## Inputs

- `docs/reports/phoenix_v3_m59_librts_yellow_open_decision_2026-06-23.md`
- `docs/reviews/call_for_review_phoenix_v3_m59_librts_yellow_open_decision_2026-06-23.md`
- `docs/reviews/claude_phoenix_v3_m59_librts_yellow_open_decision_recorded_review_2026-06-23.md`
- `docs/reviews/claude_phoenix_v3_m59_librts_yellow_open_decision_review_2026-06-23.raw.md`
- `docs/reviews/antigravity_phoenix_v3_m59_librts_yellow_open_decision_review_2026-06-23.md`
- `docs/reviews/codex_claude_antigravity_phoenix_v3_m58_rerun_intake_3ai_consensus_2026-06-23.md`
- `docs/rebuild/v3/evidence/phoenix_v3_m58_librts_m57_authorized_execution_20260624_0055/summary.json`

## Verdicts

Codex:

```text
accept_m59_librts_set_b_yellow_open_limit_continue_set_a_step2
```

Claude:

```text
accept_m59_librts_set_b_yellow_open_limit_continue_set_a_step2
```

Antigravity:

```text
accept_m59_librts_set_b_yellow_open_limit_continue_set_a_step2
```

## Consensus Read

All three seats agree:

- LibRTS/AABB is a Set-B control row, not a Set-A architecture-bearing probe.
- The source and payload classification
  `set_a_probe_candidate=false` / `set_b_control_candidate=true` is relevant
  and should be preserved.
- The M58 metadata failure is cleared, but the timing rows are not green.
- `optix_cold_single_shot` remains weak and yellow/open.
- Another immediate LibRTS POD run is not authorized by M59 and would distract
  from the Step-2 runtime-trunk work.
- The next action should return Step 2 to a Set-A runtime family.

## Carry-Forward Risk

The reviewers differ only in severity language, not direction:

- Claude marks the OptiX issue as P2 release-stage debt.
- Antigravity marks the OptiX weakness as a P1 release risk.

M59 therefore carries the stricter operational rule:

```text
Before any V3 release decision, the OptiX cold single-shot Set-B row needs an
accepted user-language explanation or a separately reviewed runtime-overhead
fix.
```

That explanation must not rely only on first-sample stripping. It must address
the weak full geomean, weak median, low pass count, and weak stripped median.

## Next Allowed Action

M60 may prepare a reviewed Step-2 Set-A selection packet. The likely work is to
choose one Set-A family and define why it exercises reusable runtime machinery
instead of app-specific route tuning.

M59 does not authorize a LibRTS rerun, LibRTS optimization cycle, all-app run,
or release wording.

## Non-Authorization

This consensus does not authorize:

- no V3 release
- no all-app benchmark run
- no broad paid POD campaign
- no second M57 run
- no additional LibRTS POD run
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true-zero-copy claim
- no watch-row closure

## Goal-Level Decision Audit

Decision: accept M59 as a 3-AI-reviewed classification decision and continue
Step 2 on Set-A runtime-family work.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? The foolish action would be
   treating a Set-B control row as the next V3 performance trunk, or using
   first-sample stripping to hide a still-weak OptiX row.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Preserve the yellow/open status, carry the release risk explicitly,
   and move runtime engineering back to Set-A families.
4. Can I now try a different path that actually solves the problem? Yes. M60
   should select the next Set-A runtime-family target and keep LibRTS as a
   release-risk control row, not as the active optimization target.
