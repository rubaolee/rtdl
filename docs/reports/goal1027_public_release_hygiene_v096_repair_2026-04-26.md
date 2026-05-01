# Goal1027 Public Release Hygiene v0.9.6 Repair

Date: 2026-04-26

## Problem

The broad local discovery after Goal1026 failed one stale test:

```text
tests.goal648_public_release_hygiene_test.Goal648PublicReleaseHygieneTest.test_history_public_indexes_include_v095
```

The test still expected `history/README.md` to say the archive ran through the `v0.9.5` release. Goal1023 correctly advanced the live history index to `v0.9.6`, so the test was stale.

The historical `docs/release_reports/v0_9/support_matrix.md` also still pointed readers at `../v0_9_5/support_matrix.md` for the current public boundary even though `v0.9.6` is now the current released boundary.

## Changes

- Updated `tests/goal648_public_release_hygiene_test.py` to assert both the current `v0.9.6` history catch-up row and the preserved `v0.9.5` release rows.
- Updated `docs/release_reports/v0_9/support_matrix.md` to point current-boundary readers at `../v0_9_6/support_matrix.md`.

## Verification

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal648_public_release_hygiene_test -v
```

Result:

```text
Ran 3 tests in 0.001s
OK
```

## Boundary

This is a stale-test and stale-link repair after the v0.9.6 history catch-up. It does not run cloud, tag, release, or authorize public RTX speedup claims.

