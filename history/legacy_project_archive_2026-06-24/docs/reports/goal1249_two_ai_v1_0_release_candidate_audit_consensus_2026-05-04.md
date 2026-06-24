# Goal1249 Two-AI Consensus: v1.0 Release-Candidate Audit

Date: 2026-05-04

## Scope

This consensus covers the v1.0 release-candidate audit gate:

- `scripts/goal1249_v1_0_release_candidate_audit.py`
- `tests/goal1249_v1_0_release_candidate_audit_test.py`
- `docs/reports/goal1249_v1_0_release_candidate_audit_2026-05-04.md`
- `docs/reports/goal1249_v1_0_release_candidate_audit_2026-05-04.json`
- `docs/release_reports/v1_0/support_matrix.md`

It does not release `v1.0`, does not update `VERSION`, does not authorize a
tag, and does not authorize new public speedup wording.

## Audit Result

Goal1249 generated a valid audit:

- valid: `True`
- recommendation: `v1_0_release_candidate_ready_for_release_surface_gate`
- pod needed now: `False`
- release marker: `v0.9.8`
- package ok: `True`
- support matrix ok: `True`
- docs index ok: `True`
- reports ok: `True`

The audit verifies that the v1.0 support matrix and
`docs/v1_0_rtx_app_status.md` both expose the same `12` reviewed RTX phase
names. It also verifies that blocked, not-reviewed, and non-NVIDIA rows stay
bounded.

## External-AI Review

Gemini reviewed the audit script, test, generated report, support matrix, and
v1.0 package files. Gemini returned `VERDICT: ACCEPT`.

Review file:

- `docs/reports/goal1249_gemini_v1_0_release_candidate_audit_review_2026-05-04.md`

## Codex Review

Codex accepts the audit:

- The release marker remains `v0.9.8`.
- The package remains draft/not released.
- The audit does not require a pod for the current scope.
- The support matrix order now matches the status-page reviewed-row source of
  truth.
- The gate points to the right next step: release-surface documentation gate,
  full local discovery or approved equivalent, final external review, and final
  authorization before `VERSION` or tag changes.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1249_v1_0_release_candidate_audit_test
Ran 4 tests in 0.163s
OK

PYTHONPATH=src:. python3 -m unittest \
  tests.goal1248_v1_0_release_candidate_package_test \
  tests.goal1249_v1_0_release_candidate_audit_test \
  tests.goal1229_current_main_v1_0_readiness_audit_test \
  tests.goal646_public_front_page_doc_consistency_test \
  tests.goal1217_version_marker_current_release_sync_test
Ran 16 tests in 0.462s
OK
```

## Consensus Verdict

ACCEPT.

Goal1249 is complete. The next v1.0 work is the release-surface documentation
test gate, followed by full local discovery or an approved release-equivalent
gate.
