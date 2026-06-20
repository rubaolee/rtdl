# RTDL Documentation

This directory has three doors:

| Door | Audience | Purpose |
| --- | --- | --- |
| [Learn](learn/README.md) | Learners and app builders | Quick path to run examples, write kernels, choose backends, and understand the current V4.0.0 boundaries. |
| [Research](research/README.md) | Internal researchers and advanced developers | Architecture notes, backend research, RayJoin/Embree context, future ideas, and design constraints. |
| [Audit](audit/README.md) | Release reviewers and auditors | Current process docs, current release package, evidence reports, reviews, and history pointers. |

Tutorials live at the repository top level in [Tutorials](../tutorials/README.md).
Use docs when you need reference material; use tutorials when you want the
ordered teaching path.

If you are new, start in **Learn**. If you are evaluating design or extending
the system, start in **Research**. If you are checking evidence, consensus, or
project history, start in **Audit**.

Current status: RTDL V4.0.0 is the active source-tree release on this branch.
It publishes the Python GPU RT-core operator lane for one evidence-backed
fixed-radius CUDA device-array route, while keeping source-tree usage and
bounded wording. Public performance wording remains row-scoped and
evidence-bound; the V4 route is not a broad RT-core speedup claim. Package,
PyPI, wheel, stable SDK, generated binding, public true-zero-copy, async, and
full framework-surface wording remain blocked.
For the short canonical wording, read
[Current Claim Boundaries](learn/current_claim_boundaries.md).

Short model:

```text
Python writes the application.
RTDL expresses the RT-shaped kernel.
Native backends execute generic engine contracts.
```

This is the same idea as "Python App, Generic Engine": the Python layer handles
app policy and runtime engine selection, while native runtime symbols stay
generic.

## Fast Learner Path

Read these in order:

1. [Project Front Page](../README.md)
2. [Tutorials](../tutorials/README.md)
3. [V4.0 Tutorial Track](../tutorials/v4_0/README.md)
4. [Current Claim Boundaries](learn/current_claim_boundaries.md)
5. [RTDL Programming Surfaces](learn/programming_surfaces.md)
6. [Versioning Glossary](versioning.md)
7. [Source-Tree Doctor](learn/source_tree_doctor.md)
8. [Quick Tutorial](quick_tutorial.md)
9. [App And Example Quickstart](app_example_quickstart.md)
10. [Application Catalog](application_catalog.md)
11. [Feature Guide](rtdl_feature_guide.md)
12. [Capability Boundaries](capability_boundaries.md)
13. [Current Architecture](current_architecture.md)
14. [Performance Model](performance_model.md)
15. [Benchmark Evidence Index](learn/benchmark_evidence_index.md)
16. [RT-Core Evidence Matrix](learn/rt_core_evidence_matrix.md)
17. [IR And Lowering](rtdl/ir_and_lowering.md)

## Current Reference Pages

| Topic | Page |
| --- | --- |
| App engine support | [App Engine Support Matrix](app_engine_support_matrix.md) |
| Backend maturity | [Backend Maturity](backend_maturity.md) |
| Feature support | [Engine Feature Support Contract](features/engine_support_matrix.md) |
| Source-tree setup | [Source-Tree Doctor](learn/source_tree_doctor.md) |
| Claim boundary short form | [Current Claim Boundaries](learn/current_claim_boundaries.md) |
| Programming surfaces | [RTDL Programming Surfaces](learn/programming_surfaces.md) |
| Version identity | [RTDL Versioning Glossary](versioning.md) |
| Partner acceleration | [Partner Acceleration Boundaries](partner_acceleration_boundaries.md) |
| Current support matrix | [Current Support Matrix](current_main_support_matrix.md) |
| Runtime overhead | [Runtime Overhead Architecture](runtime_overhead_architecture.md) |
| Benchmark evidence | [Benchmark Evidence Index](learn/benchmark_evidence_index.md) |
| RT-core evidence interpretation | [RT-Core Evidence Matrix](learn/rt_core_evidence_matrix.md) |
| Public map | [Public Documentation Map](public_documentation_map.md) |
| Current release reports | [Current Release Reports](release_reports/) |
| Current release package | [RTDL V4.0.0 Release Package](release_reports/v4_0_0/README.md) |
| Previous V3 release package | [RTDL v3.0.2 Release Package](release_reports/v3_0_2/README.md) |
| Current benchmark evidence | [Benchmark Evidence Index](learn/benchmark_evidence_index.md) |
| History Index | [History Index](history/README.md) |

## Directory Map

| Directory | What belongs there |
| --- | --- |
| `learn/` | Human learning route and curated current-doc links. |
| `features/` | Current feature homes and engine support contract. |
| `rtdl/` | DSL, IR, programming model, and workload reference docs. |
| `research/` | Advanced design, RayJoin/Embree context, technical app notes, proposals, and future research notes. |
| `audit/` | Process docs, directive snapshots, and runbooks for reviewers. |
| `release_reports/` | Current release package only; previous release packets live under `history/release_reports/`. |
| `reports/` | Detailed benchmark, implementation, and audit reports. |
| `reviews/` | External AI and human-style review records. |
| `handoff/` | Handoff files used for external review and continuation. |
| `history/` | Archived docs, release archive entry points, root-level logs, version notes, and preserved project history. |

## Rule

Current learner docs should explain one coherent V4.0.0 surface. Previous release
evidence is preserved for review in history, but it should not interrupt the
normal learning path.
