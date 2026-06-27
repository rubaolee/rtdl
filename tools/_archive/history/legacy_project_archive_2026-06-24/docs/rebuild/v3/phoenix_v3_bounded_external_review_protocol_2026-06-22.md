# Phoenix V3 Bounded External Review Protocol

Date: 2026-06-22
Status: active process guard

## Purpose

Phoenix V3 required external review for aggregate release authorization, and
external AI review must never stall engineering work indefinitely.

This protocol exists because the previous Claude attempt produced no
substantive review text after a timeout. That was not a release verdict. It was
also not a reason to keep fighting the tool while useful V3 work sat idle.
The historical status for that attempt is
`external_review_not_obtained_claude_no_output_timeout`.

## Rule

External AI review is a bounded gate, not an infinite loop.

When a Phoenix V3 decision requires Claude, Gemini, or another external
reviewer:

1. Prepare one complete review packet with exact artifact paths, claim flags,
   and requested verdict labels.
2. Make at most one automated external-AI attempt for that packet in the active
   work loop.
3. Use a hard wall-clock timeout for the attempt. If no substantive verdict is
   returned before the timeout, stop the attempt.
4. Save a blocked review record with the exact status
   `external_review_not_obtained_<tool>_<reason>`.
5. Do not count stderr, login banners, partial chatter, or tool availability as
   a review verdict.
6. Do not promote release wording from a missing external verdict.
7. Continue non-release V3 work that does not depend on the missing verdict.
8. A later accepted verdict can supersede a missing-verdict blocker.
   The intake guard decides whether that later verdict is accepted.

The current aggregate release state is:

```text
aggregate_13_row_scoped_dossier_external_review_status:
  external_verdict_obtained_claude_scoped_dossier_release_ready_not_v3_release
aggregate_13_row_scoped_dossier_external_authorization_obtained: true
status: redo_required
release_authorized: false
```

A scoped external verdict cannot override the major-version performance mandate.

## Valid External Verdicts

Only a written review record with one of these labels can change aggregate
release status:

- `release_ready`
- `approve_blocked_not_release`
- `block_p0`
- `block_p1`

A no-output timeout, authentication message, CLI progress message, or failed
tool invocation is not one of those verdicts.

## Allowed Fallback

Codex may write a fallback consensus or ask a Codex subagent to review the
packet, but that fallback is not external release authorization unless the user
explicitly changes the release rule.

Fallback review can:

- preserve the work already done;
- identify likely blockers;
- keep local gates honest;
- prepare a clean handoff for Claude, Gemini, or a human reviewer.

Fallback review cannot:

- authorize a Phoenix V3 release;
- authorize broad V3-over-V2 wording;
- replace a missing external aggregate verdict.

## Current Operating Decision

For the current 13-row Phoenix V3 surface, the correct action is:

1. keep the release gate at `redo_required`;
2. keep the no-output Claude attempt recorded as historical missing external
   review;
3. keep the accepted Claude `release_ready` verdict as scoped packet evidence,
   not V3 release authorization;
4. preserve every forbidden claim boundary until broad V2.x performance is
   proven.

## Goal-Level Decision Audit

Decision: stop repeated Claude/Gemini struggle, record missing external review
when it happens, and allow a later intake-accepted verdict to supersede that
blocker.

1. Was I foolish? Yes. The earlier behavior was foolish.
2. If yes, what actions made it foolish? I waited on and retried an external
   AI path without turning the no-output result into a bounded process state.
3. Was there another path? Yes. I should have written the review request,
   imposed a timeout, recorded `external_review_not_obtained`, and continued
   work that did not depend on external authorization.
4. Can I now try a different path? Yes. This protocol makes the different path
   mandatory: bounded attempt, recorded result, no release promotion without a
   real verdict, and continued Phoenix V3 cleanup.
