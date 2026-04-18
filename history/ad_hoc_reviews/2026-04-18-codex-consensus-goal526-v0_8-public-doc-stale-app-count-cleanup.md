# Codex Consensus: Goal526 v0.8 Public Doc Stale App-Count Cleanup

Date: 2026-04-18

Verdict: ACCEPT

## Reviewed Inputs

- `docs/reports/goal526_v0_8_public_doc_stale_app_count_cleanup_2026-04-18.md`
- `docs/reports/goal526_claude_review_2026-04-18.md`
- `docs/reports/goal526_gemini_review_2026-04-18.md`
- `docs/release_facing_examples.md`
- `docs/rtdl_feature_guide.md`
- `tests/goal526_v0_8_public_doc_stale_phrase_test.py`

## Consensus

Claude and Gemini both accepted Goal526. Codex agrees.

The release-facing docs no longer imply that the current v0.8 app line contains
only the older three apps. `docs/release_facing_examples.md` now scopes Goal509
to robot collision screening and Barnes-Hut specifically. `docs/rtdl_feature_guide.md`
now names all six current v0.8 app-building examples and points to Goal507,
Goal509, and Goal524 for app-specific backend/performance boundaries.

No overclaiming was introduced. The proximity-app performance boundary remains
the Goal524 one: bounded RTDL-backend characterization, not an external-baseline
speedup claim.

## Local Validation

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal526_v0_8_public_doc_stale_phrase_test \
  tests.goal525_v0_8_proximity_perf_doc_refresh_test \
  tests.goal511_feature_guide_v08_refresh_test
```

Result:

```text
Ran 6 tests in 0.001s
OK
```

`git diff --check` passed.
