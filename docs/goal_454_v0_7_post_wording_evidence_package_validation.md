# Goal 454: v0.7 Post-Wording Evidence Package Validation

Date: 2026-04-16

## Purpose

Mechanically validate the v0.7 DB evidence package after Goal 453 refreshed the
release-facing performance wording.

## Scope

- Required evidence files for Goals 450-453.
- Required consensus files for Goals 450-453.
- Linux correctness evidence:
  - 75 tests
  - `OK`
- Performance JSON evidence:
  - Goal 450 row count / repeats / DSN / hash matches.
  - Goal 451 row count / repeats / DSN / index modes / hash consistency.
  - Goal 452 row count / repeats / DSN / hash matches / mixed query-only
    results / total-time wins.
- Release-facing documentation wording:
  - Goal 452 is canonical.
  - query-only results are mixed.
  - setup-plus-10-query total time favors RTDL in measured Linux evidence.
  - no stale Goal 443/450-only performance wording.

## Non-Goals

- No new Linux benchmark.
- No runtime change.
- No staging.
- No commit.
- No tag.
- No push.
- No merge.
- No release authorization.
