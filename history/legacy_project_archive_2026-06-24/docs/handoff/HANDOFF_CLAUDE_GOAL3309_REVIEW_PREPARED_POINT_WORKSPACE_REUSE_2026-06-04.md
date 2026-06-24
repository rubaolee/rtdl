# Handoff: Goal3309 Claude Review Of Goal3308 Prepared Point Workspace Reuse

Date: 2026-06-04
Repo: `C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`
Branch: `main`
Expected output: `docs/reviews/goal3309_claude_review_goal3308_prepared_point_workspace_reuse_2026-06-04.md`

## Task

Please perform an independent Claude review of Goal3308, which follows Goal3306's prepared point-probe columns by moving the reusable device count buffer and OptiX launch-parameter buffer into the generic prepared point-probe handle.

## Files To Inspect

- `src/native/optix/rtdl_optix_workloads.cpp`
- `docs/reports/goal3308_prepared_point_workspace_reuse_2026-06-04.md`
- `docs/reports/goal3308_workspace_reuse_prepared_points_rayjoin_same_slice_pod_2026-06-04.json`
- `tests/goal3308_prepared_point_workspace_reuse_test.py`
- `tests/goal3306_prepared_point_probe_columns_scalar_count_test.py`
- `docs/reports/goal3306_prepared_point_probe_columns_scalar_count_2026-06-04.md`
- `docs/reviews/goal3307_claude_review_goal3306_prepared_point_probe_columns_2026-06-04.md`
- `docs/research/future_version_to_do_list.md`

## Review Questions

1. Does Goal3308 keep the native change generic and app-agnostic, with no RayJoin-specific logic or naming added to the native engine?
2. Does the implementation really reuse `PreparedPointProbeColumns2D::d_count` and `PreparedPointProbeColumns2D::d_params` instead of allocating per count call?
3. Does the RTX A5000 artifact support the reported improvement from Goal3306 prepared points (`~0.317 ms`) to Goal3308 workspace reuse (`~0.303 ms`) while preserving count `1430` and exact validation boundaries?
4. Does the report correctly frame this as a small repeated-query overhead win, not a one-shot win, not RayJoin-beating, and not a broad RT-core speedup claim?
5. Are claim-boundary flags, timing units, mode labels, counts, commit hash, and route names internally consistent?
6. Is the recommended next direction sound: batched/replayed scalar-count launches or a more compact generic closed-shape predicate-count path, rather than another tiny allocation tweak?

## Required Output

Write a Markdown review at:

`docs/reviews/goal3309_claude_review_goal3308_prepared_point_workspace_reuse_2026-06-04.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Please lead with findings by severity. If you find no blockers, say so explicitly. Do not authorize release, public speedup claims, RayJoin paper reproduction claims, broad RT-core claims, true-zero-copy claims, or any app-specific native-engine direction.
