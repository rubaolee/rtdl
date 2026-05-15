# Goal 477: v0.7 Broad Unittest Discovery Repair

Date: 2026-04-16
Status: Accepted with external AI review

## Objective

Run a broad local unittest discovery pattern that includes both `test*.py` and `goal*_test.py` files, repair any local correctness or portability issues found, and preserve the result as v0.7 pre-release evidence.

## Acceptance Criteria

- Run `python3 -m unittest discover -s tests -p '*test*.py'`.
- Triage every failure/error from the first broad run.
- Apply only narrow fixes that preserve release behavior and honesty boundaries.
- Re-run the broad discovery command and record the final count.
- Do not stage, commit, tag, push, merge, or release.
- Preserve the external AI review verdict in the repo.
