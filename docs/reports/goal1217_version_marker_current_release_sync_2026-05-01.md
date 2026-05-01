# Goal1217 Version Marker Current-Release Sync

Date: 2026-05-01

## Purpose

Before writing a v0.9.8 final release-authorization gate, this checkpoint fixes
one local release-surface inconsistency found during Goal1217 preparation:

- `VERSION` still said `v0.9.1`.
- Public docs and release reports identify the current released baseline as
  `v0.9.6`.

`VERSION` is a live machine-readable release marker, so it must match the
current released public baseline until an explicit later release action bumps it
to a new tag.

## Change

- Updated `VERSION` from `v0.9.1` to `v0.9.6`.
- Added `tests/goal1217_version_marker_current_release_sync_test.py`.

## Validation

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal1217_version_marker_current_release_sync_test -v
```

Expected result: `2` tests OK.

## Boundary

This is not a v0.9.8 release action. It does not tag, publish, authorize new
public RTX wording, or start a cloud pod. It only repairs the current released
baseline marker so the next v0.9.8 authorization gate starts from a coherent
release surface.
