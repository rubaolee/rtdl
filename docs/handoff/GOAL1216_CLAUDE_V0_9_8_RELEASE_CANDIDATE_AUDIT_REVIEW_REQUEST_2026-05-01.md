# Goal1216 External Review Request

Please review Goal1216 as an external AI reviewer for RTDL.

## Scope

Goal1216 is a local v0.9.8 release-candidate audit. It does not tag, publish,
upload packages, authorize new public RTX wording, or require cloud/pod work.

## Files To Review

- `scripts/goal1216_v0_9_8_release_candidate_audit.py`
- `tests/goal1216_v0_9_8_release_candidate_audit_test.py`
- `docs/reports/goal1216_v0_9_8_release_candidate_audit_2026-05-01.json`
- `docs/reports/goal1216_v0_9_8_release_candidate_audit_2026-05-01.md`
- Prior evidence reports referenced by Goal1216:
  - `docs/reports/goal1214_full_local_discovery_after_goal1213_2026-05-01.md`
  - `docs/reports/goal1215_release_surface_doc_audit_2026-05-01.md`
  - `docs/reports/goal1206_repaired_rtx_recovery_merge_intake_2026-05-01.md`
  - `docs/reports/goal1208_public_wording_decision_after_goal1206_2026-05-01.md`
  - `docs/v1_0_rtx_app_status.md`

## Local Validation Already Run

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal1216_v0_9_8_release_candidate_audit_test -v
```

Result: 4 tests OK.

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1210_v0_9_8_release_readiness_audit_test \
  tests.goal1216_v0_9_8_release_candidate_audit_test -v
```

Result: 8 tests OK.

## Requested Verdict

Please answer with `ACCEPT` or `BLOCK`.

Focus on:

1. Whether Goal1216 correctly verifies Goal1204-Goal1215 closure trails.
2. Whether its public-claim boundary is honest: 11 reviewed public RTX wording
   rows, only road hazard newly promoted, DB/Jaccard still blocked.
3. Whether its pod decision is technically appropriate: no immediate pod needed
   for local release-candidate audit; any next pod should be a batched final RTX
   replay only if final release authorization requires fresh hardware evidence.
4. Whether the audit overclaims v0.9.8 release status. It should not.

If accepted, write or return a concise review suitable for saving as:

`docs/reports/goal1216_claude_v0_9_8_release_candidate_audit_review_2026-05-01.md`
