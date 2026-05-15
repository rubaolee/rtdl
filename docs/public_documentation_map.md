# RTDL Public Documentation Map

This page maps the current v2.0-facing documentation for users, reviewers, and
app builders. It keeps the front-door reading path separate from historical
reports and audit records.

## Read By Question

| If you care about... | Read first | Then read |
| --- | --- | --- |
| What RTDL is | [Project Front Page](../README.md) | [Feature Guide](rtdl_feature_guide.md), [Capability Boundaries](capability_boundaries.md) |
| First program | [Quick Tutorial](quick_tutorial.md) | [Tutorial Ladder](tutorials/README.md), [Hello World](tutorials/hello_world.md) |
| Workload recipes | [Feature Quickstart Cookbook](tutorials/feature_quickstart_cookbook.md) | [Workload Cookbook](rtdl/workload_cookbook.md), [Features Index](features/README.md) |
| Apps and examples | [App And Example Quickstart](app_example_quickstart.md) | [Application Catalog](application_catalog.md), [Examples Index](../examples/README.md) |
| Architecture | [Current Architecture](current_architecture.md) | [Capability Boundaries](capability_boundaries.md), [Backend Maturity](backend_maturity.md), [v2.0 Pre-Release Candidate](release_reports/v2_0_pre_release_candidate.md) |
| Programming model | [ITRE App Programming Model](rtdl/itre_app_model.md) | [Programming Guide](rtdl/programming_guide.md), [DSL Reference](rtdl/dsl_reference.md) |
| IR and lowering | [IR And Lowering](rtdl/ir_and_lowering.md) | `src/rtdsl/ir.py`, `src/rtdsl/lowering.py` |
| Performance | [Performance Model](performance_model.md) | [App Engine Support Matrix](app_engine_support_matrix.md), [Partner Acceleration Boundaries](partner_acceleration_boundaries.md) |
| Older releases or audits | [Legacy Learner Doc Version Notes](history/legacy_learner_doc_version_notes.md) | [Release Reports](release_reports/), [Benchmark And Audit Reports](reports/) |

## Public Doc Layers

| Layer | Purpose | Primary pages |
| --- | --- | --- |
| Front page | Short project promise and current boundary | [Project Front Page](../README.md), [Docs Index](README.md) |
| Tutorials | Teach the kernel shape and first app runs | [Quick Tutorial](quick_tutorial.md), [Tutorial Ladder](tutorials/README.md), [Feature Quickstart Cookbook](tutorials/feature_quickstart_cookbook.md) |
| Apps and examples | Show what each app does and where RTDL fits | [App And Example Quickstart](app_example_quickstart.md), [Application Catalog](application_catalog.md) |
| Architecture and language | Explain runtime, IR, lowering, and app model | [Current Architecture](current_architecture.md), [ITRE App Programming Model](rtdl/itre_app_model.md), [IR And Lowering](rtdl/ir_and_lowering.md), [DSL Reference](rtdl/dsl_reference.md) |
| Performance and boundaries | Explain how to interpret backend results | [Performance Model](performance_model.md), [Capability Boundaries](capability_boundaries.md), [Partner Acceleration Boundaries](partner_acceleration_boundaries.md) |
| History and evidence | Preserve project evolution and review records | [Legacy Learner Doc Version Notes](history/legacy_learner_doc_version_notes.md), [Release Reports](release_reports/), [Benchmark And Audit Reports](reports/) |

## Current User Message

RTDL lets a Python application describe RT-shaped query work once, then run the
supported kernel through the appropriate backend. Python remains the app and
control layer. RTDL owns the kernel contract, traversal/refinement shape, and
backend bridge for supported primitive paths.

The current learner surface is v2.0-facing:

- Python+partner+RTDL is the active candidate surface;
- PyTorch is the reference partner and CuPy is the lightweight conformance
  partner;
- native engines remain app-agnostic;
- final release waits for the strict 3-AI consensus redline.

The honest public message is:

- RTDL reduces backend-specific authoring burden for supported RT-style
  workloads.
- Backend support varies by feature and platform.
- `--backend optix` selects an OptiX path; it is not automatically a public
  speedup claim.
- Performance claims should name the exact workload, backend, hardware, command
  shape, output contract, and artifact.
- Whole-application performance depends on the non-RT work around the RTDL
  kernel.

## Learner Design Check

A learner should be able to answer these questions after the front-door docs:

1. How do I run a source-tree example with `PYTHONPATH=src:.`?
2. What does `input -> traverse -> refine -> emit` mean?
3. Which parts of my program stay in Python?
4. Which parts belong to the app-agnostic RTDL engine?
5. How do partner-owned columns fit into the v2.0 candidate surface?
6. Why is `--backend optix` not automatically a speedup claim?

If a page does not help answer one of those questions, it belongs in the
history/evidence layer rather than the beginner path.
