# RTDL v1.0 Release Statement

Status: released as `v1.0`.

The current released version is `v1.0`.

The proposed release statement is:

> RTDL `v1.0` is the app-shaped RTDL proof release. It shows that a
> Python-facing ray-tracing DSL can express real non-rendering traversal
> workloads, run them through audited backend surfaces, and document exactly
> where bounded performance claims are valid. It is a foundation release for
> the v1.5 primitive cleanup and v2.0 end-to-end performance architecture.

## What This Release May Claim

- RTDL can express the current app/example set through a Python-facing
  traversal-oriented model.
- The v1.0 inventory records `18` app rows and distinguishes accelerated
  sub-paths from Python or app-specific continuation work.
- The current NVIDIA RTX public wording surface has `12` reviewed bounded
  sub-path rows.
- Reviewed RTX wording is limited to the exact prepared/native sub-paths named
  in `docs/v1_0_rtx_app_status.md`.
- Vulkan, HIPRT, and Apple RT have selected proof surfaces, but they are not
  expanded into new v1.0 public speedup promotions.
- v1.0 intentionally accepts app-specific native continuations as proof
  machinery; v1.5 should replace those with generic primitives.

## What This Release Must Not Claim

- broad speedup across all RTDL apps;
- whole-app speedup unless a future release explicitly reviews that whole-app
  contract;
- public speedup wording for blocked or not-reviewed rows;
- that every `--backend optix` run proves NVIDIA RT-core speedup;
- that v1.0 has already removed app-specific engine customization;
- that v1.0 is the final v2.0 performance architecture.

## Evidence Pointers

- `/Users/rl2025/rtdl_python_only/docs/v1_0_app_acceleration_inventory.md`
- `/Users/rl2025/rtdl_python_only/docs/v1_0_rtx_app_status.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/performance_model.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal1246_two_ai_front_page_diet_consensus_2026-05-04.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal1247_two_ai_quick_tutorial_final_polish_consensus_2026-05-04.md`
