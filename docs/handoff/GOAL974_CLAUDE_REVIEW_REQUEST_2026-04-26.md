# Goal974 Claude Review Request

Please review the remaining-local-baseline collection and write a verdict to:

```text
docs/reports/goal974_claude_review_2026-04-26.md
```

Scope:

- Read `scripts/goal974_remaining_local_baselines.py`.
- Read `tests/goal974_remaining_local_baselines_test.py`.
- Read `docs/reports/goal974_remaining_local_baselines_2026-04-26.md`.
- Cross-check Goal836 and Goal971 generated state.

Review questions:

1. Were locally available CPU/Embree baselines collected for the six remaining rows?
2. Are there now zero invalid baseline artifacts?
3. Are the remaining missing baselines correctly limited to PostGIS or OptiX-only evidence?
4. Does Goal971 remain conservative with `public_speedup_claim_authorized_count=0`?
5. Are any public speedup or whole-app claims over-authorized?

Return `ACCEPT` or `BLOCK`, with concrete blockers if any.
