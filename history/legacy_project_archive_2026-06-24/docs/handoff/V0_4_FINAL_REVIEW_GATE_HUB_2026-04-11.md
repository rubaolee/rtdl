# v0.4 Final Review Gate Hub

This hub packages the final release-gate review work for `v0.4.0`.

Use it only against the clean release-prep workspace:

- `[REPO_ROOT]`

## Current Branch State

- branch: `codex/v0_4_release_prep`
- release state: not yet tagged for public release

## Release Rule

`v0.4.0` must not be finalized until these three reviews complete:

1. total code review
2. total doc review
3. detailed process audit

## Review Inputs

Canonical release package:

- `[REPO_ROOT]/docs/release_reports/v0_4/README.md`
- `[REPO_ROOT]/docs/release_reports/v0_4/release_statement.md`
- `[REPO_ROOT]/docs/release_reports/v0_4/support_matrix.md`
- `[REPO_ROOT]/docs/release_reports/v0_4/audit_report.md`
- `[REPO_ROOT]/docs/release_reports/v0_4/tag_preparation.md`

Most important supporting evidence:

- `[REPO_ROOT]/docs/reports/goal228_v0_4_heavy_nearest_neighbor_perf_2026-04-10.md`
- `[REPO_ROOT]/docs/reports/goal229_fixed_radius_neighbors_accelerated_boundary_fix_2026-04-10.md`
- `[REPO_ROOT]/docs/reports/goal232_final_pre_release_verification_2026-04-10.md`
- `[REPO_ROOT]/docs/reports/goal233_final_release_decision_package_2026-04-10.md`
- `[REPO_ROOT]/docs/reports/goal235_rtnn_experiment_reproducibility_audit_2026-04-11.md`
- `[REPO_ROOT]/docs/reports/goal236_v0_4_final_release_gate_and_v0_5_direction_2026-04-11.md`

## Review Tasks

### 1. Total code review

Handoff:

- `[REPO_ROOT]/docs/handoff/GEMINI_V0_4_TOTAL_CODE_REVIEW_2026-04-11.md`

Expected output:

- `[REPO_ROOT]/docs/reports/gemini_v0_4_total_code_review_2026-04-11.md`

### 2. Total doc review

Handoff:

- `[REPO_ROOT]/docs/handoff/GEMINI_V0_4_TOTAL_DOC_REVIEW_2026-04-11.md`

Expected output:

- `[REPO_ROOT]/docs/reports/gemini_v0_4_total_doc_review_2026-04-11.md`

### 3. Detailed process audit

Handoff:

- `[REPO_ROOT]/docs/handoff/GEMINI_V0_4_DETAILED_PROCESS_AUDIT_2026-04-11.md`

Expected output:

- `[REPO_ROOT]/docs/reports/gemini_v0_4_detailed_process_audit_2026-04-11.md`

## Review Standard

Each review should answer one narrow release question:

- is there a real blocker that should stop `v0.4.0`?

These reviews should not treat the unresolved RTNN full-paper reproduction gap
as a hidden `v0.4` blocker. That gap has already been assigned to `v0.5`.

## After Reviews Return

If all three reviews are non-blocking:

1. write a final review-closure note
2. confirm the clean release-prep branch state
3. only then do the user-authorized release action

If any review is blocking:

1. fix the blocker
2. rerun the affected review
3. update the release package before release
