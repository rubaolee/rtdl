# RTDL Public Documentation Map

This page maps the current documentation by audience. It is intentionally
simple: learners should not have to walk through logs, release history, or
research notes to write their first RTDL program.

## Three Doors

| Audience | Door | Use it for |
| --- | --- | --- |
| Learner / user / app builder | [Learn](learn/README.md) | Tutorials, examples, current API, current backend boundaries. |
| Internal researcher / advanced developer | [Research](research/README.md) | Architecture, backend design, RayJoin/Embree context, future ideas. |
| Release reviewer / auditor | [Audit](audit/README.md) | Release evidence, reports, reviews, handoffs, process docs, archived logs. |

## Read By Question

| If you care about... | Read first | Then read |
| --- | --- | --- |
| What RTDL is | [Project Front Page](../README.md) | [Learn](learn/README.md) |
| First program | [Quick Tutorial](quick_tutorial.md) | [Tutorial Ladder](tutorials/README.md), [Hello World](tutorials/hello_world.md) |
| Workload recipes | [Feature Quickstart Cookbook](tutorials/feature_quickstart_cookbook.md) | [Workload Cookbook](rtdl/workload_cookbook.md), [Features Index](features/README.md) |
| Apps and examples | [App And Example Quickstart](app_example_quickstart.md) | [Application Catalog](application_catalog.md), [Examples Index](../examples/README.md) |
| Architecture | [Current Architecture](current_architecture.md) | [Research](research/README.md), [Capability Boundaries](capability_boundaries.md) |
| Programming model | [ITRE App Programming Model](rtdl/itre_app_model.md) | [Programming Guide](rtdl/programming_guide.md), [DSL Reference](rtdl/dsl_reference.md) |
| IR and lowering | [IR And Lowering](rtdl/ir_and_lowering.md) | `src/rtdsl/ir.py`, `src/rtdsl/lowering.py` |
| Performance | [Performance Model](performance_model.md) | [App Engine Support Matrix](app_engine_support_matrix.md), [Partner Acceleration Boundaries](partner_acceleration_boundaries.md) |
| Partner release gate | [Partner Roadmap Gate](release_reports/v1_8_v2_0_python_partner_rtdl_gate.md) | [Audit](audit/README.md) |
| Release evidence | [Audit](audit/README.md) | [Release Reports](release_reports/), [Benchmark And Audit Reports](reports/) |
| Archive context | [Version Archive Notes](history/version_archive_notes.md) | [Root Archive](history/root_archive/), [API/Internal Archive](history/api_internal_archive/) |

## Public Doc Layers

| Layer | Purpose | Primary pages |
| --- | --- | --- |
| Front page | Short project promise and current boundary | [Project Front Page](../README.md), [Docs Index](README.md) |
| Tutorials | Teach the kernel shape and first app runs | [Quick Tutorial](quick_tutorial.md), [Tutorial Ladder](tutorials/README.md), [Feature Quickstart Cookbook](tutorials/feature_quickstart_cookbook.md) |
| Apps and examples | Show what each app does and where RTDL fits | [App And Example Quickstart](app_example_quickstart.md), [Application Catalog](application_catalog.md) |
| Architecture and language | Explain runtime, IR, lowering, and app model | [Current Architecture](current_architecture.md), [ITRE App Programming Model](rtdl/itre_app_model.md), [IR And Lowering](rtdl/ir_and_lowering.md), [DSL Reference](rtdl/dsl_reference.md) |
| Performance and boundaries | Explain how to interpret backend results | [Performance Model](performance_model.md), [Capability Boundaries](capability_boundaries.md), [Partner Acceleration Boundaries](partner_acceleration_boundaries.md) |
| Research | Preserve advanced design and source context | [Research](research/README.md) |
| Audit | Preserve evidence and project chronology | [Audit](audit/README.md) |

## Current User Message

RTDL lets a Python application describe RT-shaped query work once, then run the
supported kernel through the appropriate backend. Python remains the app and
control layer. RTDL owns the kernel contract, traversal/refinement shape, and
backend bridge for supported primitive paths.

The current learner surface is the v2.0 release. The current released version is
`v2.0`.

- Python+partner+RTDL is the released source-tree Python+partner+RTDL surface;
- PyTorch is the reference partner and CuPy is the lightweight conformance
  partner;
- native engines remain app-agnostic;
- release claims stay inside the completed 3-AI consensus boundary.

If a page does not help a learner answer "how do I write and run a current RTDL
program?", it belongs in Research or Audit rather than the beginner path.
