# Goal1250 Two-AI Consensus: v1.0 Release-Surface Documentation Audit

Date: 2026-05-04

## Scope

This consensus covers the v1.0 release-surface documentation gate:

- `scripts/goal1250_v1_0_release_surface_doc_audit.py`
- `tests/goal1250_v1_0_release_surface_doc_audit_test.py`
- `docs/reports/goal1250_v1_0_release_surface_doc_audit_2026-05-04.md`
- `docs/reports/goal1250_v1_0_release_surface_doc_audit_2026-05-04.json`
- the audited public surfaces listed in the Goal1250 report.

It does not release `v1.0`, does not update `VERSION`, does not authorize a
tag, and does not authorize new public speedup wording.

## Audit Result

Goal1250 generated a valid audit:

- valid: `True`
- recommendation: `v1_0_release_surface_ready_for_full_local_discovery`
- version: `v0.9.8`
- version ok: `True`
- surface count: `18`
- failure count: `0`
- pod needed now: `False`

The audit covers the user-facing release surfaces the project currently cares
about most: front page, tutorials, apps/examples, architecture, programming
model, IR/lowering, performance, v1.0 app inventory/status docs, and the v1.0
release-candidate package.

## External-AI Review

Gemini reviewed the audit script, tests, generated report, and audited surfaces.
Gemini returned `VERDICT: ACCEPT`.

Review file:

- `docs/reports/goal1250_gemini_v1_0_release_surface_doc_audit_review_2026-05-04.md`

## Codex Review

Codex accepts the audit:

- v1.0 remains draft/not released.
- v0.9.8 remains the current release marker.
- The public docs retain v1.0/v1.5/v2.0 positioning.
- The app docs and status pages preserve bounded public speedup wording.
- The gate does not require an NVIDIA pod unless release scope changes.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1250_v1_0_release_surface_doc_audit_test
Ran 4 tests in 0.080s
OK

PYTHONPATH=src:. python3 -m unittest \
  tests.goal1250_v1_0_release_surface_doc_audit_test \
  tests.goal1244_public_doc_spine_test \
  tests.goal1232_public_doc_map_test \
  tests.goal646_public_front_page_doc_consistency_test \
  tests.goal1248_v1_0_release_candidate_package_test \
  tests.goal1249_v1_0_release_candidate_audit_test
Ran 22 tests in 0.188s
OK

PYTHONPATH=src:. python3 -m unittest $(rg -l "README.md|front page|public docs|quick_tutorial|Quick Tutorial|release_facing_examples|Goal1177|Goal748|Goal509|v0\\.8|v0\\.9\\.5|rt_count_threshold_prepared|rt_core_flags_prepared|current released version|v1_0_rtx_app_status|v1_0_app_acceleration_inventory|release_reports/v1_0|goal1249|goal1250" tests -g '*test.py' | sed 's#/#.#g; s#.py$##')
Ran 357 tests in 6.522s
OK (skipped=2)
```

## Consensus Verdict

ACCEPT.

Goal1250 is complete. The next v1.0 work is full local discovery or an approved
release-equivalent gate, followed by final external review and final
authorization.
