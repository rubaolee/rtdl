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
| Understand the architecture | [Current Architecture](current_architecture.md) | [IR And Lowering](rtdl/ir_and_lowering.md), [ITRE App Programming Model](rtdl/itre_app_model.md), [v2.0 Pre-Release Candidate](release_reports/v2_0_pre_release_candidate.md) |
| Interpret benchmark results | [Performance Model](performance_model.md) | [Current Support Matrix](current_main_support_matrix.md), [Release Reports](release_reports/) |
| Try the partner pre-release candidate path | [Python Partner Any-Hit](tutorials/partner_anyhit.md) | [Partner Acceleration Boundaries](partner_acceleration_boundaries.md), [OptiX Partner Zero-Copy Any-Hit Preview](tutorials/partner_optix_zero_copy_anyhit.md), [v2.0 Pre-Release Candidate](release_reports/v2_0_pre_release_candidate.md) |

## What RTDL Promises

RTDL helps you express RT-shaped query kernels once and run them through
supported backends without hand-maintaining separate backend implementations.

The public authoring pattern is:

```text
input -> traverse -> refine -> emit
```

Python remains the application layer. RTDL owns the supported kernel contract,
runtime dispatch, and backend bridge for RT-shaped primitive work.

The current learner path is v2.0-facing: Python applications call RTDL kernels,
and supported partner paths use NumPy, PyTorch, or CuPy owned columns while the
native engine remains app-agnostic.

v2.0 is a pre-release candidate, not a final release. Treat packaging/install
support and broad public speedup wording as future work unless a later
authorized release packet says otherwise.

The current Python+partner path is a v2.0 pre-release candidate, not a final
release. The current evidence packet has reviewed OptiX/RT timing for all
16 current comparison rows under documented contracts, and the old
`segment_polygon_anyhit_rows` mixed row is superseded by a streaming exact
witness-column contract. Final release remains blocked by the 3-AI consensus
redline while the fresh Claude-family review is unavailable. Use
[Partner Acceleration Boundaries](partner_acceleration_boundaries.md) and
[v2.0 Pre-Release Candidate](release_reports/v2_0_pre_release_candidate.md)
for the current positive and negative rule around partner-owned columns.

## Learner Rule

If you are learning RTDL from GitHub, keep this split in mind:

```text
Python writes the application.
RTDL expresses the RT-shaped kernel.
Native backends execute generic engine contracts.
```

Examples may have app names because they are Python applications. Native engine
symbols and architecture claims must stay app-agnostic. This is the main design
lesson behind the current v2.0-facing design.

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
- [v2.0 Pre-Release Candidate](release_reports/v2_0_pre_release_candidate.md)
- [Benchmark And Audit Reports](reports/)
- [Benchmark And Audit Reports](reports/)
- [Release Reports](release_reports/)

## History And Audit Trail

The current docs are for users. Historical project evolution, release packages,
review records, and goal archives live here:

- [History Index](history/README.md)
- [Legacy Learner Doc Version Notes](history/legacy_learner_doc_version_notes.md)
- [Complete History Map](../history/COMPLETE_HISTORY.md)
- [Release Reports](release_reports/)
- [Benchmark And Audit Reports](reports/)

Keep history links out of the beginner path unless the reader is explicitly
looking for evidence or project evolution.
