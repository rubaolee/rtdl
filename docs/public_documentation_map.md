# RTDL Public Documentation Map

This page maps the current documentation by audience. It is intentionally
simple: learners should not have to walk through logs, release history, or
research notes to write their first RTDL program.

## Current User Doors

| Audience | Door | Use it for |
| --- | --- | --- |
| Learner / user / app builder | [Learn](learn/README.md) | Tutorials, examples, current API, current backend boundaries. |
| User choosing features | [Features](features/README.md) | Current primitive families and support boundaries. |
| User reading language details | [RTDL Reference](rtdl/README.md) | Programming model, DSL reference, IR, lowering, and workload guide. |

## Read By Question

| If you care about... | Read first | Then read |
| --- | --- | --- |
| What RTDL is | [Project Front Page](../README.md) | [Learn](learn/README.md) |
| First program | [Current Tutorial Track](../tutorials/current/README.md) | [Quick Tutorial](quick_tutorial.md), [Examples Index](../examples/README.md) |
| Workload recipes | [App And Example Quickstart](app_example_quickstart.md) | [Workload Cookbook](rtdl/workload_cookbook.md), [Features Index](features/README.md) |
| Apps and examples | [App And Example Quickstart](app_example_quickstart.md) | [Application Catalog](application_catalog.md), [Examples Index](../examples/README.md) |
| Architecture | [Current Architecture](current_architecture.md) | [Capability Boundaries](capability_boundaries.md) |
| Programming model | [ITRE App Programming Model](rtdl/itre_app_model.md) | [Programming Guide](rtdl/programming_guide.md), [DSL Reference](rtdl/dsl_reference.md) |
| IR and lowering | [IR And Lowering](rtdl/ir_and_lowering.md) | `src/rtdsl/ir.py`, `src/rtdsl/lowering.py` |
| Performance | [Performance Model](performance_model.md) | [App Engine Support Matrix](app_engine_support_matrix.md), [Partner Acceleration Boundaries](partner_acceleration_boundaries.md) |
| Current release evidence | [RTDL v2.14 Release Package](release_reports/v2_14/README.md) | [Benchmark Evidence Index](learn/benchmark_evidence_index.md), [RayJoin Reproduction Packet](release_reports/v2_14/rayjoin_reproduction_packet.md) |
| Archive context | [History](../history/README.md) | Old release reports, internal reviews, handoffs, and research notes |

## Public Doc Layers

| Layer | Purpose | Primary pages |
| --- | --- | --- |
| Front page | Short project promise and current boundary | [Project Front Page](../README.md), [Docs Index](README.md) |
| Tutorials | Teach the kernel shape and first app runs | [Tutorials](../tutorials/README.md), [Current Tutorial Track](../tutorials/current/README.md), [Quick Tutorial](quick_tutorial.md) |
| Apps and examples | Show what each app does and where RTDL fits | [App And Example Quickstart](app_example_quickstart.md), [Application Catalog](application_catalog.md) |
| Architecture and language | Explain runtime, IR, lowering, and app model | [Current Architecture](current_architecture.md), [ITRE App Programming Model](rtdl/itre_app_model.md), [IR And Lowering](rtdl/ir_and_lowering.md), [DSL Reference](rtdl/dsl_reference.md) |
| Performance and boundaries | Explain how to interpret backend results | [Performance Model](performance_model.md), [Capability Boundaries](capability_boundaries.md), [Partner Acceleration Boundaries](partner_acceleration_boundaries.md) |
| Archive | Preserve old evidence and project chronology | [History](../history/README.md) |

## Current User Message

RTDL lets a Python application describe RT-shaped query work once, then run the
supported kernel through the appropriate backend. Python remains the app and
control layer. RTDL owns the kernel contract, traversal/refinement shape, and
backend bridge for supported primitive paths.

The current learner surface is the v2.14 released source-tree surface.

- Python+partner+RTDL is the current source-tree programming model;
- CuPy is the mature CUDA-array continuation partner and Numba is the measured
  custom CUDA-style continuation lane;
- native engines remain app-agnostic;
- release claims stay inside the completed evidence and consensus boundary.

If a page does not help a learner answer "how do I write and run a current RTDL
program?", it belongs under the top-level `history/` archive rather than the
beginner path.
