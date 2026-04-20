# RTDL v0.9.5 Release Package

Status: released as `v0.9.5` after Codex, Claude, and Gemini Flash accepted
the release gate.

`v0.9.5` is the bounded any-hit, visibility-row, and emitted-row reduction
release. It builds on the released `v0.9.4` Apple RT consolidation without
widening the Apple DB/graph hardware claims.

## Scope

This package records the `v0.9.5` surface:

- `rt.ray_triangle_any_hit(exact=False)` emits `{ray_id, any_hit}` rows.
- OptiX, Embree, and HIPRT have native early-exit any-hit implementations.
- Vulkan and Apple RT support the any-hit row contract through compatibility
  dispatch by projecting existing hit-count rows.
- `rt.visibility_rows_cpu(...)` and `rt.visibility_rows(..., backend=...)`
  emit `{observer_id, target_id, visible}` rows for bounded line-of-sight apps.
- `rt.reduce_rows(...)` reduces already-emitted rows in Python with `any`,
  `count`, `sum`, `min`, and `max`.

## Start Here

- [Release Statement](release_statement.md)
- [Support Matrix](support_matrix.md)
- [Audit Report](audit_report.md)
- [Tag Preparation](tag_preparation.md)
- [Goal 631 v0.9.5 Goal Ladder](../../reports/goal631_v0_9_5_anyhit_visibility_goal_ladder_2026-04-19.md)
- [Goal 632 Any-Hit Predicate](../../reports/goal632_v0_9_5_ray_triangle_any_hit_2026-04-19.md)
- [Goal 633 Visibility Rows](../../reports/goal633_v0_9_5_visibility_rows_standard_library_2026-04-19.md)
- [Goal 636 Backend Any-Hit Compatibility / Doubt Log](../../reports/goal636_v0_9_5_backend_anyhit_compatibility_and_user_doubt_log_2026-04-19.md)
- [Goal 637 OptiX Native Any-Hit](../../reports/goal637_v0_9_5_optix_native_early_exit_anyhit_2026-04-19.md)
- [Goal 638 Embree Native Any-Hit](../../reports/goal638_v0_9_5_embree_native_early_exit_anyhit_2026-04-19.md)
- [Goal 639 HIPRT Native Any-Hit](../../reports/goal639_v0_9_5_hiprt_native_early_exit_anyhit_2026-04-19.md)
- [Goal 640 Backend Support Audit](../../reports/goal640_v0_9_5_anyhit_visibility_backend_support_audit_2026-04-19.md)
- [Goal 641 Pre-Release Test Report](../../reports/goal641_v0_9_5_pre_release_test_report_2026-04-19.md)
- [Goal 642 Documentation Refresh](../../reports/goal642_v0_9_5_pre_release_doc_refresh_2026-04-19.md)
- [Goal 643 Flow Audit](../../reports/goal643_v0_9_5_pre_release_flow_audit_2026-04-19.md)
- [Goal 644 Reduce Rows](../../reports/goal644_v0_9_5_reduce_rows_standard_library_2026-04-19.md)
- [Goal 645 Public Release Docs And Package](../../reports/goal645_v0_9_5_public_release_docs_and_package_2026-04-19.md)
- [Goals 641-644 Claude Final Review](../../reports/goal641_644_claude_final_release_gate_review_2026-04-19.md)
- [Goals 641-644 Gemini Flash Final Review](../../reports/goal641_644_gemini_flash_final_release_gate_review_2026-04-19.md)
- [Goal 645 Claude Review](../../reports/goal645_claude_review_2026-04-19.md)
- [Goal 645 Gemini Flash Review](../../reports/goal645_gemini_flash_review_2026-04-19.md)

## Build And Test

Portable local checks:

```bash
PYTHONPATH=src:. python examples/rtdl_ray_triangle_any_hit.py
PYTHONPATH=src:. python examples/rtdl_visibility_rows.py
PYTHONPATH=src:. python examples/rtdl_reduce_rows.py
PYTHONPATH=src:. python -m unittest tests.goal632_ray_triangle_any_hit_test tests.goal633_visibility_rows_test tests.goal644_reduce_rows_standard_library_test -v
```

Full local release gate:

```bash
PYTHONPATH=src:. python -m unittest discover -s tests -p '*_test.py' -v
```

Latest recorded local result:

- `1211 tests`
- `179 skips`
- `OK`

For Linux backend-native any-hit validation, see the Goal641 report.
