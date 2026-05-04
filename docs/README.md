# RTDL Documentation

This directory contains current public docs plus preserved release and audit
history. If you are new to RTDL, do not browse everything here first. Start with
the live path below, then branch into tutorials, apps, architecture, IR, or
performance.

The current released version is `v0.9.8`; current released version: `v0.9.8`.

## New User Path

Use this page as a router, not as a history archive. Read these in order for
the current public story:

1. [Project Front Page](../README.md)
2. [Public Documentation Map](public_documentation_map.md)
3. [Current Architecture](current_architecture.md)
4. [Feature Guide](rtdl_feature_guide.md)
5. [Capability Boundaries](capability_boundaries.md)
6. [Quick Tutorial](quick_tutorial.md)
7. [RTDL Tutorials](tutorials/README.md)
8. [App And Example Quickstart](app_example_quickstart.md)
9. [Application Catalog](application_catalog.md)
10. [v1.0 App Acceleration Inventory](v1_0_app_acceleration_inventory.md)
11. [IR And Lowering](rtdl/ir_and_lowering.md)
12. [Performance Model](performance_model.md)
13. [v1.0 RTX App Status](v1_0_rtx_app_status.md)
14. [RTDL Current Main Support Matrix](current_main_support_matrix.md)
15. [v0.9.8 Support Matrix](release_reports/v0_9_8/support_matrix.md)

Older release packages remain linked below for auditability, but they are not
the recommended first path for a new user.

That is the intended public reading path.

## Public Surfaces

| Surface | What to read | What it should answer |
| --- | --- | --- |
| Front page | [Project Front Page](../README.md), [Public Documentation Map](public_documentation_map.md) | What RTDL is, what the current release is, and what not to overclaim. |
| Tutorials | [Quick Tutorial](quick_tutorial.md), [RTDL Tutorials](tutorials/README.md) | How to run a first kernel and learn the authoring shape. |
| Apps and examples | [App And Example Quickstart](app_example_quickstart.md), [Application Catalog](application_catalog.md), [v1.0 App Acceleration Inventory](v1_0_app_acceleration_inventory.md) | Which apps exist, what RTDL accelerates, and which app phases remain outside. |
| Architecture/model/IR/performance | [Current Architecture](current_architecture.md), [ITRE App Programming Model](rtdl/itre_app_model.md), [IR And Lowering](rtdl/ir_and_lowering.md), [Performance Model](performance_model.md) | How the runtime is structured, how lowering works, and how to read evidence. |

## Evaluate RTDL In Ten Minutes

If your question is "does RTDL make my ray-tracing-style workload easier to
write?", use this path:

1. Read [Current Architecture](current_architecture.md) for the user contract.
2. Run [Quick Tutorial](quick_tutorial.md).
3. Choose one runnable app from [App And Example Quickstart](app_example_quickstart.md).
4. Check [v1.0 App Acceleration Inventory](v1_0_app_acceleration_inventory.md)
   before interpreting app performance.
5. Check [Performance Model](performance_model.md) before writing any speedup
   wording.

The public promise is authoring-burden reduction: RTDL hides backend-specific
traversal and result plumbing behind one kernel shape while preserving bounded,
audited release claims.

## Main Routes

| Goal | Start here | Then read |
| --- | --- | --- |
| Front page and project promise | [Project Front Page](../README.md) | [Public Documentation Map](public_documentation_map.md), [Feature Guide](rtdl_feature_guide.md) |
| Tutorials | [Quick Tutorial](quick_tutorial.md) | [RTDL Tutorials](tutorials/README.md), [Feature Quickstart Cookbook](tutorials/feature_quickstart_cookbook.md) |
| Apps and examples | [App And Example Quickstart](app_example_quickstart.md) | [Application Catalog](application_catalog.md), [Release-Facing Examples](release_facing_examples.md), [v0.8 App Building](tutorials/v0_8_app_building.md), [Examples Index](../examples/README.md) |
| Architecture | [Current Architecture](current_architecture.md) | [Capability Boundaries](capability_boundaries.md), [Backend Maturity](backend_maturity.md) |
| Programming model | [ITRE App Programming Model](rtdl/itre_app_model.md) | [Programming Guide](rtdl/programming_guide.md), [Workload Cookbook](rtdl/workload_cookbook.md) |
| IR and lowering | [IR And Lowering](rtdl/ir_and_lowering.md) | [DSL Reference](rtdl/dsl_reference.md), `src/rtdsl/ir.py`, `src/rtdsl/lowering.py` |
| Performance | [Performance Model](performance_model.md) | [v1.0 RTX App Status](v1_0_rtx_app_status.md), [App Engine Support Matrix](app_engine_support_matrix.md) |
| Backend contract | [RTDL Current Main Support Matrix](current_main_support_matrix.md) | [Engine Feature Support Contract](features/engine_support_matrix.md), [Backend Maturity](backend_maturity.md) |

## Current Boundary

v1.0 is a foundation release line. It proves that RTDL can express real
app-shaped ray-tracing workloads from Python, connect them to multiple backend
surfaces, and document where performance claims are valid. It is not the final
engine architecture.

Important public-claim rules:

- `--backend optix` is not by itself a public NVIDIA RT-core speedup claim.
- Public speedups require reviewed evidence for the exact prepared/native
  sub-path being described.
- Goal748 supersedes pre-fix robot OptiX evidence because it fixed a short-ray
  OptiX correctness issue; use post-fix Goal748 or later robot evidence.
- Whole-app outputs may include Python continuation work such as ranking,
  clustering, force reduction, SQL-style output assembly, or graph reductions.
- v1.5 should replace app-specific native continuations with reviewed generic
  primitives.
- v2.0 is the broader end-to-end performance target.

Current released feature terms you will see in the docs include
`ray_triangle_any_hit`, `visibility_rows`, and `reduce_rows`. OptiX, Embree,
and HIPRT have released native early-exit any-hit coverage. Vulkan and Apple RT
also have released bounded paths, but backend support varies by predicate and
platform. `reduce_rows` is not a native backend reduction claim unless a
specific backend path says so.

## Environment Facts

- Run examples from the repository root.
- Use `PYTHONPATH=src:. python ...` on Bash/zsh.
- Use `set PYTHONPATH=src;.` before `python ...` on Windows `cmd.exe`.
- Use `$env:PYTHONPATH = "src;."` before `python ...` on Windows PowerShell.
- Python `3.10+` is the expected floor.

## Release Packages

Use these for audit trails and exact release boundaries:

- [v0.9.8 Release Package](release_reports/v0_9_8/README.md)
- [v0.9.8 Release Statement](release_reports/v0_9_8/release_statement.md)
- [v0.9.8 Support Matrix](release_reports/v0_9_8/support_matrix.md)
- [v0.9.8 Audit Report](release_reports/v0_9_8/audit_report.md)
- [v0.9.5 Release Package](release_reports/v0_9_5/README.md)
- RTDL v0.8 Release Package: [v0.8 Release Package](release_reports/v0_8/README.md) (`docs/release_reports/v0_8/README.md`)
- [RTDL v0.8 Release Statement](release_reports/v0_8/release_statement.md)
- RTDL v0.8 Support Matrix: [v0.8 Support Matrix](release_reports/v0_8/support_matrix.md)
- [v0.7 Release Package](release_reports/v0_7/README.md)
- [Older Release Packages](release_reports/)
- [Complete History Map](../history/COMPLETE_HISTORY.md)
- [Hausdorff Linux Performance Evidence](reports/goal507_hausdorff_linux_perf_report_2026-04-17.md)

## Compact Historical State

The current `main` carries the released bounded `v0.7.0` DB line and released
  `v0.8.0` app-building examples:

This is the released `v0.8.0` app-building layer, not a new backend or language
contract.

- Hausdorff distance app using `knn_rows(k=1)`.
- ANN candidate search app using `knn_rows(k=1)`.
- outlier detection and DBSCAN clustering apps using fixed-radius neighbor
  rows plus Python thresholding or cluster expansion.
- robot collision screening app using `ray_triangle_any_hit`.
- Barnes-Hut force approximation app using `fixed_radius_neighbors`.

The v0.8 app-building tutorial records future language pressure without
    claiming new backend or language internals.

Goal524 characterizes ANN candidate, outlier, and DBSCAN proximity apps. SciPy
was not installed in that gate, so the result is not an external-baseline
speedup claim.

## Demo

- [Short 4K demo URL](https://youtu.be/d3yJB7AmCLM)
- Primary visual demo: `examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py`

## Maintainer And History Material

Use these only when you need deeper history, review trails, or process detail:

- [AI Collaboration Workflow](ai_collaboration_workflow.md)
- [Audit Flow](audit_flow.md)
- [Historical Reports](reports/)
- [Historical Docs Tree](history/)
- [Archive Index](archive/README.md)
- [Engineering Handoffs](engineering/handoffs/V0_4_FINAL_RELEASE_HANDOFF_HUB.md)

Detailed goal/progress records belong in `docs/reports/`, not in this landing
page.
