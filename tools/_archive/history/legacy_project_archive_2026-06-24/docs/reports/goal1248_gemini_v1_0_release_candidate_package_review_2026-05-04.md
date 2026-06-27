# Gemini Review: Goal1248 v1.0 Release Candidate Package

Date: 2026-05-04

Command:

```bash
/opt/homebrew/bin/gemini -p "Review the RTDL v1.0 release-candidate package for release-facing correctness. Focus on overclaims, released-vs-draft boundary, public RTX speedup boundaries, v1.0/v1.5/v2.0 positioning, and whether the package can proceed to final release-candidate audit. Read these files: docs/release_reports/v1_0/README.md docs/release_reports/v1_0/release_statement.md docs/release_reports/v1_0/support_matrix.md docs/release_reports/v1_0/audit_report.md docs/release_reports/v1_0/tag_preparation.md docs/README.md docs/reports/goal1248_v1_0_release_candidate_package_2026-05-04.md tests/goal1248_v1_0_release_candidate_package_test.py. Return VERDICT: ACCEPT or VERDICT: REQUEST_CHANGES, then findings with file/line references and required fixes. Do not edit files." --yolo
```

## Raw Verdict

VERDICT: REQUEST_CHANGES

The RTDL v1.0 release-candidate package is professionally structured and
maintains excellent defensive boundaries regarding its "foundation proof"
status and its relationship with the v1.5/v2.0 roadmap. However, there are
significant naming inconsistencies between the `support_matrix.md` and the
underlying source-of-truth documents (`v1_0_rtx_app_status.md` and
`v1_0_app_acceleration_inventory.md`) that could lead to technical overclaims,
particularly regarding the distinction between "KNN" and "fixed-radius"
queries.

## Findings

1. `docs/release_reports/v1_0/support_matrix.md`: the
   `facility_knn_assignment` sub-path was named `prepared_query_knn`.
   Required fix: change it to the source-of-truth
   `coverage_threshold_prepared_recentered` wording because the reviewed claim
   is a fixed-radius coverage-threshold decision, not ranked KNN assignment.

2. `docs/release_reports/v1_0/support_matrix.md`: the
   `service_coverage_gaps` sub-path was named `prepared_native_nearest_service`.
   Required fix: change it to `prepared_gap_summary` because nearest-clinic
   output is outside the accelerated claim.

3. `docs/release_reports/v1_0/support_matrix.md`: several other sub-path names
   did not precisely match the technical phase names in
   `docs/v1_0_rtx_app_status.md`. Required fix: align the support matrix with
   the source-of-truth reviewed rows.

4. `docs/README.md`: the release sentence repeated `v0.9.8`. Required fix:
   remove the redundant repetition.

5. `tests/goal1248_v1_0_release_candidate_package_test.py`: the test
   hard-coded the inconsistent support-matrix names. Required fix: update test
   tokens after aligning the matrix.

## Codex Response

Accepted. The package kept the correct draft/release boundary, but the support
matrix must use exact reviewed phase names from `docs/v1_0_rtx_app_status.md`.
The fixes were applied in Goal1248 before consensus.
