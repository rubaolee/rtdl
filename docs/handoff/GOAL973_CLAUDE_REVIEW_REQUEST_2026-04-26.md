# Goal973 Claude Review Request

Please review the deferred decision baseline collection and write a verdict to:

```text
docs/reports/goal973_claude_review_2026-04-26.md
```

Scope:

- Read `docs/reports/goal973_deferred_decision_baselines_2026-04-26.md`.
- Read `scripts/goal973_deferred_decision_baselines.py`.
- Read `tests/goal973_deferred_decision_baselines_test.py`.
- Cross-check Goal836/Goal971 generated state.

Review questions:

1. Do the four decision rows now have valid CPU-oracle and Embree same-semantics baselines?
2. Is the facility scale correct (`copies=20000`, `iterations=10`)?
3. Is the reduced Hausdorff local scale honestly documented rather than hidden?
4. Does Goal971 remain conservative, with `public_speedup_claim_authorized_count=0`?
5. Are any public speedup or whole-app claims over-authorized?

Return `ACCEPT` or `BLOCK`, with concrete blockers if any.
