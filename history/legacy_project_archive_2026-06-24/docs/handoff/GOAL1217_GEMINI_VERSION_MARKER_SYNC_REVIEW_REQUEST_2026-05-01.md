# Goal1217 External Review Request

Please review Goal1217 as an external AI reviewer for RTDL.

## Scope

Goal1217 repairs a local release-surface inconsistency discovered while
preparing the v0.9.8 final release-authorization gate.

`VERSION` still said `v0.9.1`, while public docs and release reports identify
the current released baseline as `v0.9.6`. Since `VERSION` is a live
machine-readable release marker, it should match the current public baseline
until an explicit later release action bumps it to a new tag.

## Files To Review

- `VERSION`
- `tests/goal1217_version_marker_current_release_sync_test.py`
- `docs/reports/goal1217_version_marker_current_release_sync_2026-05-01.md`
- public baseline docs:
  - `README.md`
  - `docs/release_reports/v0_9_6/README.md`
  - `docs/release_reports/v0_9_6/release_statement.md`

## Validation Already Run

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal1217_version_marker_current_release_sync_test -v
```

Result: 2 tests OK.

## Requested Verdict

Please answer with `ACCEPT` or `BLOCK`.

Focus on:

1. Whether setting `VERSION` to `v0.9.6` is correct as a current-release
   baseline repair.
2. Whether this does not prematurely authorize or claim v0.9.8.
3. Whether the added test is enough to prevent this specific drift from
   recurring.

If accepted, write or return a concise review suitable for saving as:

`docs/reports/goal1217_gemini_version_marker_sync_review_2026-05-01.md`
