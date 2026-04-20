# RTDL v0.9.5 Release Statement

RTDL `v0.9.5` is the bounded any-hit, visibility-row, and emitted-row
reduction release.

The correct public statement is:

> RTDL `v0.9.5` adds bounded yes/no ray-triangle blocker queries through
> `rt.ray_triangle_any_hit(exact=False)`, line-of-sight row helpers through
> `rt.visibility_rows_cpu(...)` and `rt.visibility_rows(..., backend=...)`,
> and deterministic Python-side row reductions through `rt.reduce_rows(...)`.
> OptiX, Embree, and HIPRT implement native early-exit any-hit. Vulkan and
> Apple RT support the any-hit row contract through compatibility dispatch, not
> native early-exit kernels.

## What v0.9.5 May Claim

- `ray_triangle_any_hit` is a public RTDL predicate that emits stable
  `{ray_id, any_hit}` rows.
- OptiX uses `optixTerminateRay()` for native early-exit any-hit where the
  loaded native library exports the v0.9.5 symbols.
- Embree uses `rtcOccluded1` for native early-exit any-hit where the loaded
  native library exports the v0.9.5 symbols.
- HIPRT uses a HIPRT traversal loop that stops after the first accepted hit
  where the loaded native library exports the v0.9.5 symbols.
- Vulkan and Apple RT can execute the any-hit row contract by reusing their
  existing hit-count paths and projecting `hit_count > 0`.
- `visibility_rows` is a bounded standard-library line-of-sight helper built
  on finite observer-target any-hit rays.
- `reduce_rows` is a Python standard-library helper over emitted rows.

## What v0.9.5 Must Not Claim

- broad any-hit speedup across all engines
- native early-exit any-hit for Vulkan or Apple RT
- Apple RT hardware acceleration for DB or graph workloads
- AMD GPU validation for HIPRT
- HIPRT CPU fallback
- native RT backend acceleration for `reduce_rows`
- a DBMS, graph database, renderer, ANN system, or general application
  framework

## Evidence

The final release gate is recorded in:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal641_v0_9_5_pre_release_test_report_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal642_v0_9_5_pre_release_doc_refresh_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal643_v0_9_5_pre_release_flow_audit_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal644_v0_9_5_reduce_rows_standard_library_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal641_644_claude_final_release_gate_review_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal641_644_gemini_flash_final_release_gate_review_2026-04-19.md`
