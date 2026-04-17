# Goal 506: v0.8 Public Entry Alignment

Date: 2026-04-17

Status: accepted by external AI review and Codex consensus

Version line: `v0.8` app-building over existing RTDL language features

## Purpose

Goal505 consolidated the v0.8 app suite in tutorials and release-facing
examples. Goal506 extends that alignment to the public entry docs so new users
do not see a stale front page that stops at `v0.7.0` DB work.

## Public Docs Updated

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`

## What Changed

- `README.md` now says the current released version is still `v0.7.0`, while
  `main` also carries accepted `v0.8` app-building work.
- `README.md` now links the v0.8 app-building tutorial and includes portable
  commands for the three current apps:
  - Hausdorff distance
  - robot collision screening
  - Barnes-Hut force approximation
- `docs/README.md` now includes the v0.8 app-building tutorial in the new-user
  path, ten-minute evaluation path, live docs list, and live state summary.
- `docs/current_architecture.md` now describes the public architecture as the
  released `v0.7.0` design plus accepted `v0.8` app-building direction on
  `main`.

## Honesty Boundary

Goal506 does not change runtime behavior. It does not claim a new released
support matrix, backend, or language primitive. The public wording explicitly
states that v0.8 app-building examples use existing RTDL features plus
Python-owned application logic.

## Regression Test

New test:

- `/Users/rl2025/rtdl_python_only/tests/goal506_public_entry_v08_alignment_test.py`

It checks that:

- `README.md` names accepted v0.8 app-building work and the three app commands.
- `README.md` preserves the "not a new released language/backend line" boundary.
- `docs/README.md` routes new users to the v0.8 app-building tutorial and names
  the three current apps.
- `docs/current_architecture.md` links the v0.8 app-building direction and
  preserves the existing-feature framing.

## Validation

Command:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal506_public_entry_v08_alignment_test tests.goal505_v0_8_app_suite_test -v
```

Result:

```text
Ran 7 tests in 0.361s
OK
```

Command:

```text
PYTHONPATH=src:. python3 -m py_compile tests/goal506_public_entry_v08_alignment_test.py
git diff --check
```

Result:

```text
OK
```

## Verdict

Goal506 is accepted.

External AI reviews:

- Claude review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal506_claude_review_2026-04-17.md`
  - Verdict: PASS
  - Finding: the entry docs correctly present accepted v0.8 app-building work
    while preserving the released-v0.7 and no-new-language/backend boundaries.
- Gemini review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal506_gemini_review_2026-04-17.md`
  - Verdict: ACCEPT
  - Finding: public entry points route users to v0.8 app-building examples and
    keep v0.8 framed as existing-feature app work rather than a released
    support-matrix claim.

Codex consensus:

- `/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-17-codex-consensus-goal506-v0_8-public-entry-alignment.md`
