# RTDL Documentation

This directory is the RTDL 3.0 reference surface. V3 is the active project
front door; v2.14 reports remain available as historical comparison material.

| Door | Audience | Purpose |
| --- | --- | --- |
| [V3](v3/README.md) | Users, evaluators, and contributors | Canonical lowering, semantic contracts, nine-app qualification, and installation. |
| [Learn](learn/README.md) | Learners and app builders | Existing source-tree examples and foundational programming material. |
| [Features](features/README.md) | Users choosing primitives | Current feature families and support boundaries. |
| [RTDL Reference](rtdl/README.md) | Users who need language details | Programming model, DSL reference, IR, lowering, and workload guide. |

Tutorials live at the repository top level in [Tutorials](../tutorials/README.md).
Use docs when you need reference material; use tutorials when you want the
ordered teaching path.

If you are new, start in **V3**. If you are looking for old evidence,
internal reviews, or exploratory work, use the top-level [History](../history/README.md)
archive instead of this current docs directory.

Current status: RTDL 3.0 provides compiler-owned canonical lowering from typed
semantic statements to verified NVIDIA OptiX providers. Nine applications are
functionally qualified with exact-output checks and behavioral traversal
receipts. Performance evidence remains scoped and mixed; the release does not
turn those rows into a universal speedup claim. Start with the
[V3 overview](v3/README.md).

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
2. [V3 Overview](v3/README.md)
3. [V3 Canonical Lowering Tutorial](../tutorials/v3_canonical_lowering.md)
4. [V3 Architecture](v3/architecture.md)
5. [V3 Correctness and Extension](v3/correctness_and_extension.md)
6. [Tutorials](../tutorials/README.md)
7. [Current Tutorial Track](../tutorials/current/README.md)
8. [Current Claim Boundaries](learn/current_claim_boundaries.md)
9. [RTDL Programming Surfaces](learn/programming_surfaces.md)
10. [Versioning Glossary](versioning.md)
11. [Source-Tree Doctor](learn/source_tree_doctor.md)
12. [Quick Tutorial](quick_tutorial.md)
13. [App And Example Quickstart](app_example_quickstart.md)
14. [Application Catalog](application_catalog.md)
15. [Feature Guide](rtdl_feature_guide.md)
16. [Capability Boundaries](capability_boundaries.md)
17. [Performance Model](performance_model.md)
18. [Benchmark Evidence Index](learn/benchmark_evidence_index.md)
19. [RT-Core Evidence Matrix](learn/rt_core_evidence_matrix.md)
20. [IR And Lowering](rtdl/ir_and_lowering.md)

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
| Current release | [RTDL V3](v3/README.md) |
| Legacy v2.14 release package | [RTDL v2.14 Release Package](release_reports/v2_14/README.md) |
| RayJoin bounded reproduction | [RayJoin Section 5.7 Bounded Reproduction](release_reports/v2_14/rayjoin_section57_bounded_reproduction.md) |
| Current benchmark evidence | [Benchmark Evidence Index](learn/benchmark_evidence_index.md) |
| Archived project history | [History](../history/README.md) |

## Directory Map

| Directory | What belongs there |
| --- | --- |
| `learn/` | Human learning route and curated current-doc links. |
| `features/` | Current feature homes and engine support contract. |
| `rtdl/` | DSL, IR, programming model, and workload reference docs. |
| `v3/` | Current V3 architecture, correctness, support, and release documentation. |
| `release_reports/v2_14/` | Preserved v2.14 release material. |
| `assets/` | Images and media used by current docs. |
| `../history/` | Old release reports, internal audits, reviews, handoffs, research notes, and archived records. |

## Rule

Current learner docs should explain one coherent v2.14 surface. Previous release
evidence is preserved under `history/`, but it should not interrupt the normal
learning path.
