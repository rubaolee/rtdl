# Handoff: Claude Review Goal4009 Root Path-Halving Rejection

Please perform a read-only external review and write the result to:

`docs/reviews/goal4010_claude_review_goal4009_root_path_halving_rejection_2026-06-08.md`

## Files To Read

- `docs/reports/goal4009_root_path_halving_candidate_rejection_2026-06-08.md`
- `tests/goal4009_root_path_halving_candidate_rejection_test.py`
- `src/native/optix/rtdl_optix_core.cpp`
- `docs/reports/goal4007_grouped_union_root_read_telemetry_pod/clustered3d_65536.json`
- `docs/reports/goal4007_grouped_union_root_read_telemetry_pod/road3d_65536.json`
- `docs/reports/goal4007_grouped_union_root_read_telemetry_pod/ngsim_dense_65536.json`
- `docs/reports/goal4009_root_path_halving_candidate_pod/clustered3d_65536.json`
- `docs/reports/goal4009_root_path_halving_candidate_pod/road3d_65536.json`
- `docs/reports/goal4009_root_path_halving_candidate_pod/ngsim_dense_65536.json`
- `docs/reports/goal4002_direct_side_effect_app_probe_pod/clustered3d_default.json`
- `docs/reports/goal4002_direct_side_effect_app_probe_pod/road3d_default.json`
- `docs/reports/goal4002_direct_side_effect_app_probe_pod/ngsim_dense_default.json`
- `docs/reports/goal4009_root_path_halving_app_signature_pod/clustered3d_candidate.json`
- `docs/reports/goal4009_root_path_halving_app_signature_pod/road3d_candidate.json`
- `docs/reports/goal4009_root_path_halving_app_signature_pod/ngsim_dense_candidate.json`

## Review Questions

1. Does the report correctly distinguish raw grouped-union telemetry improvement from app-level promotion readiness?
2. Do the artifacts support the claim that path halving reduced parent-link steps but failed or regressed app-level evidence?
3. Is the clustered3d signature mismatch sufficient to reject the candidate as a default?
4. Does committed source keep `find_grouped_union_root_readonly` readonly, with no retained mutating path-halving helper?
5. Does the report avoid overclaiming and keep release/performance/public wording closed?

Use verdict `accept`, `accept-with-boundary`, or `needs-more-evidence`.

Please do not edit source files.
