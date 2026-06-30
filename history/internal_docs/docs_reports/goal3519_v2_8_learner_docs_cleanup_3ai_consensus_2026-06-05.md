# Goal3519 3-AI Consensus: v2.8 Learner Docs Cleanup

Date: 2026-06-05

## Scope

Goal3519 cleaned the active learner-facing documentation so normal users see one current v2.8 source-tree story. The work covered:

- root front page;
- docs index;
- learner docs;
- tutorial ladder and tutorial pages;
- research benchmark README files;
- a new stale-version/link guard test.

Historical release packages and old evidence were left in history/report paths.

## Reviews

| Reviewer | File | Verdict | Notes |
| --- | --- | --- | --- |
| Codex | `docs/reports/goal3519_v2_8_learner_docs_cleanup_audit_2026-06-05.md` plus tests | accept-with-boundary | Active docs are cleaned; Python source helper names are deferred to Goal3520. |
| Claude | `docs/reviews/goal3519_claude_review_v2_8_learner_docs_cleanup_2026-06-05.md` | accept-with-boundary | Verified active markdown grep, main-door links, claim boundaries, and deferral of code-level helper names. |
| Gemini | `docs/reviews/goal3519_gemini_review_v2_8_learner_docs_cleanup_2026-06-05.md` | accept-with-boundary | Accepted the cleanup; noted Gemini could not run its own shell test and relied on manual inspection plus Codex's test output. |

## Validation

Local validation:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal3519_v2_8_learner_docs_cleanup_test \
  tests.goal3518_v2_8_benchmark_matrix_test

Ran 9 tests in 0.092s
OK
```

Additional active-doc scan found no stale current-version terms in:

- `docs/README.md`
- `docs/learn/`
- `docs/tutorials/`
- `examples/v2_0/research_benchmarks/README.md`

The root `README.md` intentionally keeps historical v2.6 and v2.3 release-package links only inside "History And Audit Trail."

## Consensus Verdict

`accept-with-boundary`

Goal3519 is accepted as the current learner-doc cleanup for v2.8. It does not authorize release, public speedup wording, broad RT-core wording, true-zero-copy wording, package-install claims, paper-reproduction claims, hidden partner selection, or app-specific native-engine behavior.

The remaining boundary is for Goal3520: example Python source files still contain legacy versioned helper names such as `v2_6` and `v2_5` in compatibility paths and docstrings. Goal3520 must decide whether to alias, quarantine, or migrate those names before final v2.8 internal closeout.
