# Goal1219 External Review Request

Please review Goal1219 as an external AI reviewer for RTDL.

## Scope

Goal1219 writes the v0.9.8 release package under
`docs/release_reports/v0_9_8/`.

This is a release-prepared package only. It must not tag, publish, push, upload
packages, authorize final release, or bump `VERSION` to `v0.9.8`.

## Files To Review

- `docs/release_reports/v0_9_8/README.md`
- `docs/release_reports/v0_9_8/release_statement.md`
- `docs/release_reports/v0_9_8/support_matrix.md`
- `docs/release_reports/v0_9_8/audit_report.md`
- `docs/release_reports/v0_9_8/tag_preparation.md`
- `tests/goal1219_v0_9_8_release_package_test.py`
- `docs/reports/goal1219_v0_9_8_release_package_2026-05-01.md`
- refreshed gate files:
  - `scripts/goal1218_v0_9_8_release_authorization_gate.py`
  - `tests/goal1218_v0_9_8_release_authorization_gate_test.py`
  - `docs/reports/goal1218_v0_9_8_release_authorization_gate_2026-05-01.md`

## Validation Already Run

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1218_v0_9_8_release_authorization_gate_test \
  tests.goal1219_v0_9_8_release_package_test -v
```

Result: 7 tests OK.

## Expected State

- v0.9.8 package files exist.
- Package status is `release-prepared as v0.9.8; not tagged or published`.
- Current public RTX wording remains bounded:
  - reviewed rows: `11`
  - only new row: `road_hazard_screening / prepared_native_compact_summary_40k`
  - `database_analytics` public speedup wording: blocked
  - `polygon_set_jaccard` public speedup wording: blocked
- Goal1218 should now say the blocker is package review pending, not package
  missing.
- No pod is required before package review.

## Requested Verdict

Please answer with `ACCEPT` or `BLOCK`.

Focus on:

1. Whether the v0.9.8 package is coherent and honest.
2. Whether it avoids premature release/tag/publish/version-bump wording.
3. Whether RTX public claims stay correctly bounded.
4. Whether Goal1218 was correctly refreshed after package creation.

If accepted, write or return a concise review suitable for saving as:

`docs/reports/goal1219_gemini_v0_9_8_release_package_review_2026-05-01.md`
