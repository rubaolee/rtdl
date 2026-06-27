# Goal 526: v0.8 Public Doc Stale App-Count Cleanup

Date: 2026-04-18

Status: accepted after Claude/Gemini/Codex consensus

## Purpose

After Goal525, a smaller stale wording issue remained in public docs:

- `docs/release_facing_examples.md` said Goal509 covered "the other two v0.8
  apps", which was accurate before the Goal519/520 Stage-1 proximity apps but
  is now misleading.
- `docs/rtdl_feature_guide.md` listed only Hausdorff, robot collision, and
  Barnes-Hut in the "What RTDL Can Currently Do" v0.8 app bullet, omitting ANN
  candidate search, outlier detection, and DBSCAN.

## Changes

- Reworded `docs/release_facing_examples.md` so Goal509 is described as
  covering the robot collision screening and Barnes-Hut apps specifically.
- Expanded `docs/rtdl_feature_guide.md` so the current capability list names all
  six accepted v0.8 app-building examples:
  - Hausdorff distance
  - ANN candidate search
  - outlier detection
  - DBSCAN clustering
  - robot collision screening
  - Barnes-Hut force approximation
- Updated that capability bullet to cite Goal507, Goal509, and Goal524 as the
  app-specific backend/performance boundary reports.

## Guard Test

Added:

- `tests/goal526_v0_8_public_doc_stale_phrase_test.py`

The test checks that:

- `docs/release_facing_examples.md` no longer contains
  `the other two v0.8 apps`
- Goal509 is scoped specifically to robot collision screening and Barnes-Hut
- `docs/rtdl_feature_guide.md` names all six current v0.8 app examples
- the feature guide points readers to Goal507, Goal509, and Goal524 reports

## Validation

Command:

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

## AI Consensus

- Claude review: `docs/reports/goal526_claude_review_2026-04-18.md`, verdict
  `ACCEPT`.
- Gemini Flash review: `docs/reports/goal526_gemini_review_2026-04-18.md`,
  verdict `ACCEPT`.
- Codex consensus: accepted. The stale v0.8 app-count wording is removed, the
  current six accepted apps are named, and no new performance overclaim is
  introduced.
