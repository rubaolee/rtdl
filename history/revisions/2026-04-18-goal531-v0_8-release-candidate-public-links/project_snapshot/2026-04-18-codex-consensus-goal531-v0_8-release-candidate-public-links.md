# Codex Consensus: Goal531 v0.8 Release-Candidate Public Links

Date: 2026-04-18

Verdict: ACCEPT

## Reviewed Inputs

- `docs/reports/goal531_v0_8_release_candidate_public_links_2026-04-18.md`
- `docs/reports/goal531_claude_review_2026-04-18.md`
- `docs/reports/goal531_gemini_review_2026-04-18.md`
- `README.md`
- `docs/README.md`
- `docs/current_architecture.md`
- `tests/goal531_v0_8_release_candidate_public_links_test.py`

## Consensus

Claude and Gemini both accepted Goal531. Codex agrees.

The v0.8 release-candidate package is now discoverable from:

- the front page
- the docs index
- the current architecture page

The links consistently use release-candidate wording and do not imply `v0.8.0`
tag authorization. The v0.8 package itself still states that the current
released version remains `v0.7.0` until explicit tag authorization.

Validation passed:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal531_v0_8_release_candidate_public_links_test \
  tests.goal530_v0_8_release_candidate_package_test

Ran 7 tests in 0.000s
OK
```

`git diff --check` passed.
