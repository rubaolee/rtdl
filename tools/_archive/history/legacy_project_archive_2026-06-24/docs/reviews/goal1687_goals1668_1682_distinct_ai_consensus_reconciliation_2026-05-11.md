# Goal1687 Goals1668-1682 Distinct-AI Consensus Reconciliation

Date: 2026-05-11

Status: reconciliation of Gemini and Claude reviews for current v1.8/v2.0
release-evidence candidates.

## Inputs

- `docs/reviews/goal1684_gemini_review_goals1668_1682_2026-05-11.md`
- `docs/reviews/goal1685_claude_review_goals1668_1682_2026-05-11.md`
- `docs/reviews/goal1685_followup_claude_fresh_review_goals1681_1682_2026-05-11.md`
- `docs/reports/goal1683_consensus_audit_remediation_plan_2026-05-11.md`

## Consensus Rule

The governing rule remains:

```text
2+ AI consensus, with at least two different AI systems.
```

Invalid:

```text
Codex + Codex
```

Codex authoring does not count as independent external review.

## Verdict

Goals1668-1680 now have distinct external Gemini + Claude review coverage for
the current architecture, app-agnostic native-engine direction, partner-track
consensus, migration/quarantine evidence, pod-smoke boundaries, and release
wording boundaries.

Goals1681 and 1682 do not yet have strict distinct-AI consensus because the
Claude review explicitly discloses that the same Claude workstream assisted in
authoring those two migrations. Treat Claude's Goal1681/1682 verdicts as useful
self-audit, but not as fully independent external review.

The later Goal1685 follow-up review confirms additional binding-side details
for Goals1681-1682: old PIP/Hausdorff native ABI references are gone from the
Python runtime bindings, replacement generic symbols are bound, and Python
compatibility surfaces are preserved. It also discloses that strict
cross-session non-authoring Claude independence is not achieved in that
conversation, so it strengthens the technical audit trail without changing the
strict-consensus state.

## Per-Goal Consensus State

| Goals | Gemini verdict | Claude verdict | Reconciled state |
| --- | --- | --- | --- |
| 1668-1670 | `accept` | `accept` | consensus-clean with release boundary |
| 1671-1672 | `accept` | `accept` | consensus-clean with release boundary |
| 1673-1674 | `accept-with-boundary` | `accept-with-boundary` | consensus-clean for local migration/quarantine; hardware proof still pending |
| 1675-1680 | `accept` / `needs-more-evidence` for release readiness | `accept` / `needs-more-evidence` for release readiness | consensus-clean with release boundary |
| 1681-1682 | `accept-with-boundary` | `accept-with-boundary`, but not fully independent | not strict-consensus-clean yet |

## Shared Technical Conclusions

Both external reviews agree that:

- the app-agnostic native-engine direction is correct;
- the partner-track consensus is correct:

```text
Protocol first. PyTorch reference first. CuPy conformance alongside it.
Engine absolutely app-agnostic throughout.
```

- `pip`, `hausdorff`, and `pose` are eliminated from the strict real native
  app-shaped symbol set;
- remaining real app-shaped native callable/export symbols are:
  - `db`: 30
  - `polygon`: 29
  - `knn`: 14
  - `bfs`: 10
- release readiness remains blocked until those families are migrated or
  mechanically quarantined and pod/hardware evidence exists.

## Required Follow-Up

For strict consensus on Goals1681 and 1682, obtain a fresh review from a Claude
session that did not author those migrations, or from another distinct external
AI system. The review should specifically cover:

- Goal1681 PIP to point-primitive any-hit migration.
- Goal1682 Hausdorff to max-distance nearest-candidate migration.
- The claim that both migrations preserve Python compatibility while removing
  native app-shaped ABI names.

Until then, Goals1681 and 1682 remain accepted-with-boundary technically, but
not strict-consensus-clean for final release evidence.

## Release Boundary

Still blocked:

```text
RTDL native internals are fully app-agnostic.
```

Still blocked:

```text
RTDL has general true zero-copy support.
```

This reconciliation does not authorize v1.8/v2.0 release readiness. It only
records which goals now have distinct external review coverage and which still
need clean independent review.
