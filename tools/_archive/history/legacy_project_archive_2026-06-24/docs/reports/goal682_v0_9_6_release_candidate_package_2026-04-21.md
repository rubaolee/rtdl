# Goal682: v0.9.6 Release-Candidate Package

Status: PASS

Date: 2026-04-21

## Scope

Goal682 packages the accepted post-`v0.9.5` current-main prepared/prepacked
visibility/count optimization work as a `v0.9.6` release candidate.

This goal does not tag or release. The current public release remains
`v0.9.5`.

## Files Added

- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_6/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_6/release_statement.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_6/support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_6/audit_report.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_6/tag_preparation.md`

## Boundary

Allowed candidate claim:

- current main has validated prepared/prepacked repeated 2D visibility/count
  optimization paths across Apple RT, OptiX, HIPRT, and Vulkan with
  backend-specific contracts.

Disallowed claims:

- broad DB, graph, full-row, or one-shot speedup;
- RT-core speedup from the GTX 1070 Linux host;
- AMD GPU validation for HIPRT;
- Apple RT full emitted-row speedup from the scalar count path;
- release authorization before the maintainer explicitly approves tag/push.

## Evidence Used

- `/Users/rl2025/rtdl_python_only/docs/reports/goal676_677_consensus_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal678_679_consensus_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal680_consensus_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal681_consensus_2026-04-20.md`

## Verdict

PASS.

The `v0.9.6` release-candidate package is written and held for maintainer
release authorization.
