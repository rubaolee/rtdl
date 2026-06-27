# Phoenix V3 External Verdict Response Template

Date: 2026-06-22

Use this exact header shape for any external aggregate release-readiness verdict
that should be consumed by `scripts/v3_phoenix_external_verdict_intake.py`.

```text
Reviewer: Claude
Verdict: `approve_blocked_not_release`
Scope: Phoenix V3 aggregate 13-row / 9-capability release-readiness packet.
```

Allowed `Reviewer:` values:

- `Claude`
- `Gemini`
- `Human external reviewer`

Allowed `Verdict:` labels:

- `release_ready`
- `approve_blocked_not_release`
- `block_p0`
- `block_p1`

Meaning:

- `release_ready`: external reviewer authorizes the exact scoped V3 release
  wording and confirms no P0/P1 blockers remain.
- `approve_blocked_not_release`: external reviewer agrees the current evidence
  is coherent but release must remain blocked for an explicit remaining reason.
- `block_p0`: release must remain blocked by at least one P0 issue.
- `block_p1`: release must remain blocked by at least one P1 issue.

Do not use this template for a Codex self-review, Codex subagent review,
fallback consensus, timeout record, or missing external-review record. Those
records are intentionally rejected by the intake guard and must not authorize
release.

After the header, include:

1. Findings ordered by severity.
2. Required fixes before release, if any.
3. Exact release authorization statement.
4. Exact non-authorized claim boundaries.
5. Goal-level decision audit.
