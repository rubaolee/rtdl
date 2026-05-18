# RTDL Documentation

This directory has three doors:

| Door | Audience | Purpose |
| --- | --- | --- |
| [Learn](learn/README.md) | Learners and app builders | Quick path to run examples, write kernels, choose backends, and understand v2.0 boundaries. |
| [Research](research/README.md) | Internal researchers and advanced developers | Architecture notes, backend research, RayJoin/Embree context, future ideas, and design constraints. |
| [Audit](audit/README.md) | Release reviewers and auditors | Process docs, runbooks, release reports, evidence reports, reviews, and archived goal logs. |

If you are new, start in **Learn**. If you are evaluating design or extending
the system, start in **Research**. If you are checking evidence, consensus, or
project history, start in **Audit**.

Current status: RTDL v2.0 is the released source-tree Python+partner+RTDL
surface. The current released version is `v2.0`. The release evidence includes
streaming exact witness-column contracts for large outputs and 3-AI consensus
from Codex, Claude, and Gemini.

Internal status: v2.1 is an unreleased checkpoint for RayJoin-style first-hit,
Hausdorff benchmark tuning, and app/example readiness cleanup. It is documented
for researchers and auditors in
[Goal2344 Internal v2.1 Closure](reports/goal2344_v2_1_internal_closure_2026-05-18.md),
but it does not replace the v2.0 learner/release surface.

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
2. [Quick Tutorial](quick_tutorial.md)
3. [Tutorial Ladder](tutorials/README.md)
4. [App And Example Quickstart](app_example_quickstart.md)
5. [Application Catalog](application_catalog.md)
6. [Feature Guide](rtdl_feature_guide.md)
7. [Capability Boundaries](capability_boundaries.md)
8. [Current Architecture](current_architecture.md)
9. [Performance Model](performance_model.md)
10. [IR And Lowering](rtdl/ir_and_lowering.md)

## Current Reference Pages

| Topic | Page |
| --- | --- |
| App engine support | [App Engine Support Matrix](app_engine_support_matrix.md) |
| Backend maturity | [Backend Maturity](backend_maturity.md) |
| Feature support | [Engine Feature Support Contract](features/engine_support_matrix.md) |
| Partner acceleration | [Partner Acceleration Boundaries](partner_acceleration_boundaries.md) |
| Partner roadmap gate | [Partner Roadmap Gate](release_reports/v1_8_v2_0_python_partner_rtdl_gate.md) |
| Current support matrix | [Current Support Matrix](current_main_support_matrix.md) |
| Runtime overhead | [Runtime Overhead Architecture](runtime_overhead_architecture.md) |
| Public map | [Public Documentation Map](public_documentation_map.md) |

## Directory Map

| Directory | What belongs there |
| --- | --- |
| `learn/` | Human learning route and curated current-doc links. |
| `tutorials/` | Current v2.0 tutorials and runnable teaching docs. |
| `features/` | Current feature homes and engine support contract. |
| `rtdl/` | DSL, IR, programming model, and workload reference docs. |
| `research/` | Advanced design, RayJoin/Embree context, technical app notes, proposals, and future research notes. |
| `audit/` | Process docs, directive snapshots, and runbooks for reviewers. |
| `release_reports/` | Release packages and release evidence. |
| `reports/` | Detailed benchmark, implementation, and audit reports. |
| `reviews/` | External AI and human-style review records. |
| `handoff/` | Handoff files used for external review and continuation. |
| `history/` | Archived docs, release archive entry points, root-level logs, old version notes, and preserved project history. |

## Rule

Current learner docs should explain one surface: the v2.0 release.
Older context is preserved for review, but it should not interrupt the normal
learning path.
