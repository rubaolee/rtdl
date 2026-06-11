# RTDL Documentation

This directory has three doors:

| Door | Audience | Purpose |
| --- | --- | --- |
| [Learn](learn/README.md) | Learners and app builders | Quick path to run examples, write kernels, choose backends, and understand the current v2.10 boundaries. |
| [Research](research/README.md) | Internal researchers and advanced developers | Architecture notes, backend research, RayJoin/Embree context, future ideas, and design constraints. |
| [Audit](audit/README.md) | Release reviewers and auditors | Process docs, runbooks, release reports, evidence reports, reviews, and archived goal logs. |

Tutorials live at the repository top level in [Tutorials](../tutorials/README.md).
Use docs when you need reference material; use tutorials when you want the
ordered teaching path.

If you are new, start in **Learn**. If you are evaluating design or extending
the system, start in **Research**. If you are checking evidence, consensus, or
project history, start in **Audit**.

Current status: RTDL v2.10 is the active source-tree Python+partner+RTDL
app-portfolio surface on this branch. It keeps source-tree usage, preserves the
no-broad-speedup/no-package-install boundary, and provides current partner-choice
guidance, primitive discovery, prepared execution, and the 10-app benchmark
adequacy matrix.

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
3. [Current Tutorial Track](../tutorials/current/README.md)
4. [Quick Tutorial](quick_tutorial.md)
5. [App And Example Quickstart](app_example_quickstart.md)
6. [Application Catalog](application_catalog.md)
7. [Feature Guide](rtdl_feature_guide.md)
8. [Capability Boundaries](capability_boundaries.md)
9. [Current Architecture](current_architecture.md)
10. [Performance Model](performance_model.md)
11. [IR And Lowering](rtdl/ir_and_lowering.md)

## Current Reference Pages

| Topic | Page |
| --- | --- |
| App engine support | [App Engine Support Matrix](app_engine_support_matrix.md) |
| Backend maturity | [Backend Maturity](backend_maturity.md) |
| Feature support | [Engine Feature Support Contract](features/engine_support_matrix.md) |
| Partner acceleration | [Partner Acceleration Boundaries](partner_acceleration_boundaries.md) |
| Current support matrix | [Current Support Matrix](current_main_support_matrix.md) |
| Runtime overhead | [Runtime Overhead Architecture](runtime_overhead_architecture.md) |
| Public map | [Public Documentation Map](public_documentation_map.md) |
| Release Reports | [Release Reports](release_reports/) |
| Current benchmark adequacy | [Goal3786 v2.10 Benchmark Adequacy](reports/goal3786_current_benchmark_adequacy_after_hiprt_closeout_2026-06-07.md) |
| History Index | [History Index](history/README.md) |

## Directory Map

| Directory | What belongs there |
| --- | --- |
| `learn/` | Human learning route and curated current-doc links. |
| `features/` | Current feature homes and engine support contract. |
| `rtdl/` | DSL, IR, programming model, and workload reference docs. |
| `research/` | Advanced design, RayJoin/Embree context, technical app notes, proposals, and future research notes. |
| `audit/` | Process docs, directive snapshots, and runbooks for reviewers. |
| `release_reports/` | Release evidence and archived release records. |
| `reports/` | Detailed benchmark, implementation, and audit reports. |
| `reviews/` | External AI and human-style review records. |
| `handoff/` | Handoff files used for external review and continuation. |
| `history/` | Archived docs, release archive entry points, root-level logs, version notes, and preserved project history. |

## Rule

Current learner docs should explain one coherent v2.10 surface. Previous release
evidence is preserved for review in history and release-report paths, but it
should not interrupt the normal learning path.
