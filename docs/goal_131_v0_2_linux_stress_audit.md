# Goal 131: v0.2 Linux Stress Audit

Date: 2026-04-06
Status: accepted

## Goal

Push the current v0.2 Linux/PostGIS-backed workload families beyond the earlier
`x1024` line and record what actually happens for:

- correctness
- backend ordering
- large-row performance

Scope is limited to the two closed v0.2 workload families:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`

## Accepted outputs

- [goal131_v0_2_linux_stress_audit_2026-04-06.md](/Users/rl2025/rtdl_python_only/docs/reports/goal131_v0_2_linux_stress_audit_2026-04-06.md)
- [goal131_v0_2_linux_stress_artifacts_2026-04-06](/Users/rl2025/rtdl_python_only/docs/reports/goal131_v0_2_linux_stress_artifacts_2026-04-06)

## Acceptance rule

This goal counts only if it produces:

- real Linux/PostGIS-backed rows beyond `x1024`
- explicit correctness status through the largest practical row
- explicit performance findings, including any degradation or ordering changes
- honest limits about what this does and does not prove
