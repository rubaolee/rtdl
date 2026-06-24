# Goal3515 v2.8 Closeout Goal Sequence 3-AI Consensus

Date: 2026-06-05

## Verdict

`accept-with-boundary`.

This consensus covers the Goal3512 goal-mode sequence for closing RTDL v2.8 as
an internal version. It does not close v2.8 itself, does not authorize a public
release, and does not authorize public speedup, broad RT-core speedup, true
zero-copy, RayJoin paper reproduction, `rtdl beats RayJoin`, or full overlay
claims.

## Inputs

- Codex proposal:
  `docs/reports/goal3512_v2_8_closeout_goal_sequence_and_consensus_plan_2026-06-05.md`
- Claude review:
  `docs/reviews/goal3513_claude_review_goal3512_v2_8_closeout_sequence_2026-06-05.md`
- Gemini review:
  `docs/reviews/goal3514_gemini_review_goal3512_v2_8_closeout_sequence_2026-06-05.md`

## Review Verdicts

| Reviewer | Verdict | Notes |
| --- | --- | --- |
| Codex | `accept-with-boundary` | Proposed sequence after Goal3507/3509/3511 evidence. |
| Claude | `accept-with-boundary` | Accepted ordering; requested three acceptance-bar clarifications. |
| Gemini | `accept-with-boundary` | Accepted ordering; no reorder or missing-goal request. |

## Incorporated Claude Clarifications

Goal3512 has been updated after Claude review:

1. Goal3516 now names the expected Goal3511 review artifact path:
   `docs/reviews/goal3516_claude_review_goal3511_steady_state_relation_stream_2026-06-05.md`.
2. Goal3519 no longer has an implicit RTX pod branch. Runnable RTX example
   validation is moved to Goal3521's final validation packet.
3. Goal3520 now explicitly includes a future-work/TODO migration sweep into
   `docs/research/future_version_to_do_list.md`, plus a rework loop if the audit
   invalidates earlier docs or matrix outputs.
4. Goal3521 now clarifies that final pod validation should be a focused
   single-session packet unless the user explicitly expands the scope.

## Consensus Position

The agreed v2.8 closeout order is:

1. `/goal 3516: close current evidence bookkeeping`
2. `/goal 3517: define the prepared-execution user pattern`
3. `/goal 3518: refresh the 10-app v2.8 benchmark matrix`
4. `/goal 3519: clean v2.8 learner docs and research benchmark docs`
5. `/goal 3520: final claim-boundary and stale-doc audit`
6. `/goal 3521: final v2.8 validation packet`
7. `/goal 3522: final v2.8 internal closeout consensus`

This order is accepted for internal v2.8 closeout work. It should not be
interpreted as a public release plan or as v3.0 device-residency/user-shader
scope.

## Boundaries

All consensus participants preserve these boundaries:

- No release authorization.
- No public speedup wording.
- No broad RT-core speedup wording.
- No true zero-copy wording.
- No RayJoin paper reproduction claim.
- No `rtdl beats RayJoin` claim.
- No full overlay claim.
- No hidden partner auto-selection.
- No app-specific native-engine logic.

## Next Action

Proceed to Goal3516 after the user approves continuing: close evidence
bookkeeping, including committing Goal3511 evidence if still uncommitted,
intaking Goal3507/3509 reviews, and requesting/intaking the Goal3511 external
review.
