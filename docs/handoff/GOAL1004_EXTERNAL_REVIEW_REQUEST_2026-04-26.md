# Goal1004 External Review Request

Please independently review the saved RTX A5000 cloud artifacts and the new local audit gate.

## Scope

- Commit under review: `914122ecd2f2c73f6a51ec2d5b04ca3d575d5681`
- Branch: `codex/rtx-cloud-run-2026-04-22`
- Cloud evidence dir: `docs/reports/cloud_2026_04_26/`
- Final pod summary: `docs/reports/cloud_2026_04_26/goal1003_rtx_a5000_pod_run_summary_2026-04-26.md`
- Final artifact report: `docs/reports/cloud_2026_04_26/goal1003_rtx_a5000_final_artifact_report_2026-04-26.md`
- Final merged summary: `docs/reports/cloud_2026_04_26/goal1003_rtx_a5000_final_merged_summary_2026-04-26.json`
- Final bundle: `docs/reports/cloud_2026_04_26/goal1003_rtx_a5000_artifacts_with_report_2026-04-26-v2.tgz`
- Audit script: `scripts/goal1004_rtx_a5000_artifact_audit.py`
- Audit tests: `tests/goal1004_rtx_a5000_artifact_audit_test.py`

## Review Questions

1. Does the saved evidence support the narrow claim that all 17 current RTX app gates executed successfully on real RTX A5000 hardware?
2. Does the evidence avoid overclaiming public speedups, whole-app acceleration, DBMS behavior, or unsupported semantics?
3. Does the audit script check the right hard facts: required files, exact commit, 17 entries, zero failures, final `Status: ok`, RTX A5000 identification, GEOS incident documentation, and no-speedup boundary?
4. Are there any release-blocking issues in how the failed first graph run was preserved and remediated by installing `libgeos-dev` and rerunning only Group F?

## Expected Output

Write a verdict report with `ACCEPT` or `BLOCK`, concrete findings, and any required remediation. Save the report under `docs/reports/` if you have write access; otherwise print the report.
