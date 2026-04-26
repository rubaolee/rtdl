# Goal940 Pre-Cloud Gate And Runbook Resync

Date: 2026-04-25

## Purpose

Close the local pre-cloud loop after Goals938-939 changed public RTX wording and
the current claim-review package. The objective is to know whether the next RTX
pod can be started efficiently, and whether the single-session runbook still
matches the current manifest and validation policy.

## Changes

- Added the new graph visibility and facility coverage claim-review commands to
  the Goal515 public command truth audit coverage table.
- Regenerated:
  - `docs/reports/goal515_public_command_truth_audit_2026-04-17.json`
  - `docs/reports/goal515_public_command_truth_audit_2026-04-17.md`
  - `docs/reports/goal824_pre_cloud_rtx_readiness_gate_2026-04-23.json`
- Updated `docs/rtx_cloud_single_session_runbook.md` so Group G uses the
  manifest-driven validated command:
  `goal761_rtx_cloud_run_all.py --include-deferred --only directed_threshold_prepared --only candidate_threshold_prepared --only node_coverage_prepared`.
- Removed stale Group G small fallback commands that used `--skip-validation`;
  any smaller retry must reduce scale while keeping validation enabled.
- Updated the copyback list to include
  `goal761_group_g_prepared_decision_summary.json` instead of old small
  skipped-validation artifacts.
- Added a regression assertion to
  `tests/goal829_rtx_cloud_single_session_runbook_test.py`.

## Results

Goal824 pre-cloud gate:

```text
valid: true
active entries: 8
deferred entries: 9
full include-deferred entries: 17
unique commands: 16
public command audit: valid
```

Full manifest dry-run:

```text
status: ok
entry_count: 17
failed_count: 0
unique_command_count: 16
```

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal829_rtx_cloud_single_session_runbook_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test \
  tests.goal939_current_rtx_claim_review_package_test \
  tests.goal938_public_rtx_wording_sync_test
```

Result: 31 tests passed.

Additional tests after the copyback-list cleanup:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal829_rtx_cloud_single_session_runbook_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test \
  tests.goal821_public_docs_require_rt_core_test \
  tests.goal938_public_rtx_wording_sync_test
```

Result: 17 tests passed.

`git diff --check` passed.

## Pod Start Recommendation

The local package is now cloud-ready from a process/gate perspective. If a pod
is available, start exactly one RTX-class pod and run the OOM-safe groups in
`docs/rtx_cloud_single_session_runbook.md`, copying artifacts back after each
group.

Do not run one-off app tests and do not keep the pod running while local review
happens. Stop or terminate the pod after artifacts are copied back.

## Boundary

This goal does not run cloud, does not authorize speedup claims, and does not
promote held apps. It only verifies that the local command package and runbook
are ready for one efficient paid-pod session.
