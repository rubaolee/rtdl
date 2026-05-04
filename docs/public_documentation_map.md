# RTDL Public Documentation Map

This page is the current public map for the documentation that should matter to
new users, reviewers, and app builders. It separates front-door material from
historical reports so readers do not have to infer the project story from the
goal archive.

## Read By Question

| If you care about... | Read first | Then read |
| --- | --- | --- |
| Front page and project promise | [Project Front Page](../README.md) | [Feature Guide](rtdl_feature_guide.md), [Capability Boundaries](capability_boundaries.md) |
| Tutorials | [Quick Tutorial](quick_tutorial.md) | [Tutorial Ladder](tutorials/README.md), [Feature Quickstart Cookbook](tutorials/feature_quickstart_cookbook.md) |
| Apps | [v1.0 App Acceleration Inventory](v1_0_app_acceleration_inventory.md) | [Application Catalog](application_catalog.md), [App Engine Support Matrix](app_engine_support_matrix.md) |
| Examples | [App And Example Quickstart](app_example_quickstart.md) | [Release-Facing Examples](release_facing_examples.md), [Examples Index](../examples/README.md), [v0.8 App Building](tutorials/v0_8_app_building.md) |
| Architecture | [Current Architecture](current_architecture.md) | [Capability Boundaries](capability_boundaries.md), [Backend Maturity](backend_maturity.md) |
| Programming model | [ITRE App Programming Model](rtdl/itre_app_model.md) | [Programming Guide](rtdl/programming_guide.md), [Workload Cookbook](rtdl/workload_cookbook.md) |
| IR and lowering | [IR And Lowering](rtdl/ir_and_lowering.md) | [DSL Reference](rtdl/dsl_reference.md), `src/rtdsl/ir.py`, `src/rtdsl/lowering.py` |
| Performance | [Performance Model](performance_model.md) | [v1.0 RTX App Status](v1_0_rtx_app_status.md), [v1.0 App Acceleration Inventory](v1_0_app_acceleration_inventory.md), [Runtime Overhead Architecture](runtime_overhead_architecture.md) |

## Current v1.0 Story

v1.0 is a foundation release line for proving that RTDL can express useful
application-shaped workloads through a Python-hosted ray-tracing DSL. It is not
the final generic architecture. Some app paths currently use app-specific native
continuations so the demos can be useful and measurable.

The honest public message is:

- RTDL can already reduce authoring burden for supported RT-style workloads.
- Some bounded prepared/native sub-paths have reviewed RTX speedup wording.
- Whole-app performance depends on whether non-RT continuation work is native
  or still Python-owned.
- `--backend optix` is not by itself an NVIDIA RT-core speedup claim.
- v1.5 should replace app-specific native continuations with generic reviewed
  traversal-plus-reduction primitives.
- v2.0 is the real broader performance target, where RTDL should interoperate
  cleanly with GPU compute tools for non-RT phases.

## Public Doc Layers

### 1. Front Door

Use the root [README](../README.md) as the compact public landing page. It
should stay short and should link out to detailed docs instead of embedding
goal history.

### 2. Tutorial Path

Use [Quick Tutorial](quick_tutorial.md) and the
[Tutorial Ladder](tutorials/README.md) for first-run learning. Tutorials should
teach how to author and run RTDL programs; they should not be overloaded with
release-audit history.

### 3. Apps And Examples

Use [App And Example Quickstart](app_example_quickstart.md),
[Application Catalog](application_catalog.md),
[v1.0 App Acceleration Inventory](v1_0_app_acceleration_inventory.md), and
[Examples Index](../examples/README.md) to understand supported app demos.
These docs should say what each app does, which part is RT-accelerated, which
part remains Python-owned or app-specific native continuation, and what public
wording is allowed.

### 4. Architecture, Model, And IR

Use [Current Architecture](current_architecture.md) for system shape,
[ITRE App Programming Model](rtdl/itre_app_model.md) for the app model, and
[IR And Lowering](rtdl/ir_and_lowering.md) for the compiler/runtime plan model.
These pages should make clear that current v1.0 lowerings are still partly
workload-specific and that v1.5 must generalize them.

### 5. Performance And Claims

Use [Performance Model](performance_model.md) for how to read performance
evidence. Use [v1.0 RTX App Status](v1_0_rtx_app_status.md) and
[App Engine Support Matrix](app_engine_support_matrix.md) as the authority for
public RTX wording. Performance docs must separate:

- backend ran
- native traversal ran
- RT-core hardware was plausibly required
- same-contract evidence supports public speedup wording
- whole-app speedup is actually authorized

## Historical Material

Historical architecture, goal, release, and review files are preserved for
auditability. They are not the recommended first path for users. Start from
this map, the root README, or `docs/README.md`; only enter `docs/reports/` or
older release packages when you need evidence details.
