# RTDL Documentation

This is the current user documentation for RTDL. Start here if you want to
learn what RTDL is, run examples, write kernels, choose a backend, or interpret
performance results.

Project history and audit trails are intentionally separated from this entry
path. If you need history, use [History Index](history/README.md).

## New User Path

Read these in order:

1. [Project Front Page](../README.md)
2. [Quick Tutorial](quick_tutorial.md)
3. [Tutorial Ladder](tutorials/README.md)
4. [App And Example Quickstart](app_example_quickstart.md)
5. [Application Catalog](application_catalog.md)
6. [Feature Guide](rtdl_feature_guide.md)
7. [Capability Boundaries](capability_boundaries.md)
8. [Current Architecture](current_architecture.md)
9. [Performance Model](performance_model.md)
10. [Public Documentation Map](public_documentation_map.md)
11. [IR And Lowering](rtdl/ir_and_lowering.md)

## Read By Task

| Task | Start here | Then read |
| --- | --- | --- |
| Run the first example | [Quick Tutorial](quick_tutorial.md) | [Hello World Tutorial](tutorials/hello_world.md) |
| Learn the kernel shape | [Quick Tutorial](quick_tutorial.md) | [Programming Guide](rtdl/programming_guide.md), [DSL Reference](rtdl/dsl_reference.md) |
| Pick an app demo | [App And Example Quickstart](app_example_quickstart.md) | [Application Catalog](application_catalog.md), [Examples Index](../examples/README.md) |
| Understand features | [Feature Guide](rtdl_feature_guide.md) | [Feature Quickstart Cookbook](tutorials/feature_quickstart_cookbook.md), [Features Index](features/README.md) |
| Choose a backend | [Capability Boundaries](capability_boundaries.md) | [Backend Maturity](backend_maturity.md), [App Engine Support Matrix](app_engine_support_matrix.md) |
| Understand the architecture | [Current Architecture](current_architecture.md) | [IR And Lowering](rtdl/ir_and_lowering.md), [ITRE App Programming Model](rtdl/itre_app_model.md), [v1.8 / v2.0 Python Partner RTDL Gate](release_reports/v1_8_v2_0_python_partner_rtdl_gate.md) |
| Interpret benchmark results | [Performance Model](performance_model.md) | [Current Support Matrix](current_main_support_matrix.md), [Release Reports](release_reports/) |
| Try the partner preview path | [Python Partner Any-Hit](tutorials/partner_anyhit.md) | [v1.8 / v2.0 Python Partner RTDL Gate](release_reports/v1_8_v2_0_python_partner_rtdl_gate.md) |

## What RTDL Promises

RTDL helps you express RT-shaped query kernels once and run them through
supported backends without hand-maintaining separate backend implementations.

The public authoring pattern is:

```text
input -> traverse -> refine -> emit
```

Python remains the application layer. RTDL owns the supported kernel contract,
runtime dispatch, and backend bridge for RT-shaped primitive work.

The current roadmap keeps `v1.8` focused on finished Python+RTDL and `v2.0`
focused on finished Python+partner+RTDL. The partner preview is protocol first,
with PyTorch as the primary reference partner and CuPy as the lightweight
conformance partner, while the RTDL engine remains app-agnostic.

The current released version is `v1.8`: the first source-tree Python+RTDL
language release with the tracked native release surface migrated to an
app-agnostic engine contract. Treat packaging/install support, broad public
speedup wording, and finished partner-framework readiness as future work unless
a later authorized release packet says otherwise.

The current Python+partner path is a preview, not v2.0. v2.0 remains blocked
until true zero-copy, direct device-pointer handoff, broad RT-core evidence,
whole-application evidence, arbitrary PyTorch/CuPy acceleration boundaries, and
package-install/source-tree scope are resolved by reviewed evidence.

## v1.8 Learner Rule

If you are learning RTDL from GitHub, keep this split in mind:

```text
Python writes the application.
RTDL expresses the RT-shaped kernel.
Native backends execute generic engine contracts.
```

Examples may have app names because they are Python applications. Native engine
symbols and architecture claims must stay app-agnostic. This is the main design
lesson behind the v1.8 release chain.

## What RTDL Does Not Promise

- RTDL is not a renderer.
- RTDL is not a full database system, graph engine, robotics planner, or physics engine.
- Selecting `--backend optix` is not automatically a public speedup claim.
- GPU speedups are workload-specific; short runs may be dominated by launch,
  packing, Python orchestration, or result processing.
- Whole-application performance depends on the Python code and continuation
  work around the RTDL kernel.

## Backend Setup

Start with the portable Python reference backend:

```bash
PYTHONPATH=src:. python examples/rtdl_hello_world_backends.py --backend cpu_python_reference
```

Optional native backend build commands:

```bash
make build-embree
make build-optix
make build-vulkan
make build-hiprt HIPRT_PREFIX=/path/to/hiprtSdk
make build-apple-rt
```

Backend support depends on host OS, installed SDKs, drivers, and the selected
feature. Use [Capability Boundaries](capability_boundaries.md) and
[App Engine Support Matrix](app_engine_support_matrix.md) before publishing
backend-specific claims.

## Performance Evidence

Use benchmark reports as evidence, not as blanket promises. The safest wording
is specific: name the app, backend, hardware, command shape, and exact artifact.

Current release performance evidence lives in:

- [Performance Model](performance_model.md)
- [v1.8 Python+RTDL Gap Audit](reports/goal1737_v1_8_python_rtdl_gap_audit_2026-05-12.md)
- [v1.8 Public Docs Boundary Alignment](reports/goal1740_v1_8_public_docs_boundary_alignment_2026-05-12.md)
- [Dual-GPU Performance Release Report](reports/goal1662_v1_6_11_dual_gpu_perf_release_report_2026-05-10.md)
- [Benchmark And Audit Reports](reports/)
- [Release Reports](release_reports/)

## History And Audit Trail

The current docs are for users. Historical project evolution, release packages,
review records, and goal archives live here:

- [History Index](history/README.md)
- [Complete History Map](../history/COMPLETE_HISTORY.md)
- [Release Reports](release_reports/)
- [Benchmark And Audit Reports](reports/)

Keep history links out of the beginner path unless the reader is explicitly
looking for evidence or project evolution.
