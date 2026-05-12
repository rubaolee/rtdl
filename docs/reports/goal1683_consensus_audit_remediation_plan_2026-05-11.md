# Goal1683 Consensus Audit Remediation Plan

Date: 2026-05-11

Status: release-evidence triage after Gemini's goal-consensus audit.

## Verdict

Gemini's audit is accepted as a meta-audit input, with one important boundary:
Codex cannot close distinct-AI consensus gaps by itself. Codex can triage,
block unsafe release use, and prepare the next review packets, but missing or
ambiguous consensus remains blocked until independent review artifacts exist
from at least two distinct AI systems.

The consensus rule is:

```text
2+ AI consensus, with at least two different AI systems.
```

Invalid:

```text
Codex + Codex
```

Also invalid:

```text
authoring pass + one independent review
```

unless the authoring pass is separately documented as an independent review
artifact, which should not be assumed.

## Source Audit

Source artifacts:

- `docs/reports/goal_consensus_audit_since_v0_15_2026-05-11.md`
- `docs/reports/goal_consensus_audit_since_v0_15_2026-05-11.json`

The user requested `v0.15`, but Gemini found no repository boundary by that
name and used the established `v1.5` tag boundary. That boundary choice is
reasonable and must remain explicit in downstream reports.

Gemini's counts:

| Class | Count |
| --- | ---: |
| Passing | 80 |
| Missing or invalid | 98 |
| Ambiguous | 351 |

## Current Release-Critical Blockers

For the current v1.8/v2.0 work, the important blocker set is smaller than the
full historical list:

| Status | Goals | Meaning |
| --- | --- | --- |
| Ambiguous in Gemini audit | 1668, 1669, 1670 | Do not use as final release evidence until consensus language is reconciled. |
| Not covered by Gemini audit | 1671-1682 | New/current goals need explicit distinct-AI review before release use. |
| Missing or invalid if used | 1649 | Only matters if reused as release evidence. |

The current v1.8/v2.0 app-agnostic native-engine chain therefore needs a new
external review package covering Goals1668-1682.

## Current External Review Status

Gemini review for Goals1668-1682 is complete:

- `docs/reviews/goal1684_gemini_review_goals1668_1682_2026-05-11.md`

That review declares itself independent, rejects Codex+Codex as valid
consensus, accepts the technical direction, and keeps release readiness blocked
until remaining native leakage and hardware evidence gaps are resolved.

Claude review for Goals1668-1682 is now complete:

- `docs/reviews/goal1685_claude_review_goals1668_1682_2026-05-11.md`

The Claude review contains an important independence caveat: Claude disclosed
that the same workstream assisted in authoring Goal1681 and Goal1682. Therefore
Goals1668-1680 have clean Gemini+Claude external review coverage, while
Goals1681 and Goal1682 still need a fresh non-authoring Claude review or
another distinct external AI review before strict consensus-clean release use.

Claude follow-up compatibility audit for Goals1681-1682 is also complete:

- `docs/reviews/goal1685_followup_claude_fresh_review_goals1681_1682_2026-05-11.md`

That follow-up verifies the binding-side details for PIP and Hausdorff:
old native ABI references are absent from Python runtime bindings, the generic
replacement symbols are bound, and Python compatibility surfaces remain in
place. It still discloses the same-conversation authoring caveat, so it is
recorded as useful technical audit evidence but does not close the fresh
non-authoring review requirement for Goals1681-1682.

Reconciliation:

- `docs/reviews/goal1687_goals1668_1682_distinct_ai_consensus_reconciliation_2026-05-11.md`

Remaining required review for strict consensus on the full current chain:

```text
Goals1681-1682 by a fresh non-authoring Claude session or another distinct external AI system.
```

Until that exists, Goals1681-1682 cannot be used as final strict-consensus-clean
release evidence.

## Required Remediation

Before any missing, invalid, ambiguous, or not-covered goal can be used as a
release gate or release evidence:

1. Save independent review output from at least two distinct AI systems in
   `docs/reviews/`.
2. Ensure the review pair is not Codex+Codex.
3. Ensure the review text clearly states whether each reviewer is independent
   of authoring.
4. Add or update a consensus file that names the exact AI families and exact
   verdicts.
5. Keep release wording blocked for any goal still missing this evidence.

Recommended immediate packet:

```text
Goals1668-1682 current app-agnostic native-engine and Python+partner RTDL evidence.
```

Preferred reviewers:

```text
Claude + Gemini
```

Gemini is already complete for Goals1668-1682; Claude is complete for
Goals1668-1680 and complete-with-independence-caveat for Goals1681-1682. Codex
may summarize their results afterward, but Codex's summary must not be counted
as a substitute for either independent review.

## Release-Gate Meaning

The following remain blocked:

- using any of the 98 missing/invalid goals as release evidence;
- using any of the 351 ambiguous goals as release gates without reconciliation;
- using Goals1671-1682 as final v1.8/v2.0 release evidence before distinct-AI
  review;
- treating Codex+Codex as valid 2-AI consensus;
- treating an authoring pass as independent review.

This report does not change technical readiness. It only prevents consensus
evidence from being overclaimed.
