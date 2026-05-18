# RTDL Feature Guide

This is the high-level feature guide for the v2.0-facing RTDL surface. It is
for learners, users, and reviewers who want the current shape without release
archaeology. Older version notes live in
[Learner Doc Version Notes](history/learner_doc_version_notes.md).

## Practical Promise

RTDL helps Python users express RT-shaped query work once and run it through
supported backends without hand-maintaining separate traversal implementations.
The main productivity pattern is:

```text
Python app -> RTDL kernel -> backend primitive -> rows or partner-owned columns
```

This is not an automatic speedup promise. Performance wording must cite exact
evidence.

## Current Feature Surface

| Feature family | Current learner meaning |
| --- | --- |
| Kernel shape | `input -> traverse -> refine -> emit` |
| Geometry rows | segment intersections, point/polygon containment, ray/triangle rows |
| Hit outputs | any-hit flags, hit counts, bounded witness columns |
| Neighbor rows | fixed-radius rows, nearest-neighbor rows, bounded KNN-style rows |
| Compact summaries | counts, sums, min/max-style summaries where documented |
| Columnar partner path | NumPy/PyTorch/CuPy-owned inputs and outputs for supported primitives |
| Backend dispatch | CPU reference, native CPU/oracle, Embree, OptiX, and bounded proof surfaces where documented |
| IR/lowering | `CompiledKernel` to `RTExecutionPlan` for the supported language shape |

## v2.0 Partner Features

The v2.0-facing partner lane is about moving supported RTDL primitive inputs and
outputs through partner-owned columns:

- NumPy for CPU/host partner paths;
- PyTorch as the reference GPU framework partner;
- CuPy as a lightweight GPU conformance and RawKernel-friendly partner.

The partner path can support fast app-level continuations when the user stays in
partner-owned arrays. It does not make RTDL a general tensor compiler.

## Output Contracts

Use the smallest output contract that answers the app question:

| Need | Prefer |
| --- | --- |
| yes/no per item | flag columns |
| counts | compact count columns |
| threshold decisions | scalar or compact threshold summaries |
| candidate reduction | bounded candidate-summary columns |
| exact witnesses | streaming witness columns |
| human inspection | Python row dictionaries, accepting materialization cost |

The streaming witness-column contract is the current v2.0 answer to large
segment/polygon witness output. It preserves exact witness IDs without forcing a
huge Python dictionary table.

## What Users Build With These Features

The examples demonstrate:

- visibility and blocker tests;
- service coverage and hotspot screening;
- facility assignment and nearest-neighbor screening;
- road hazard and segment/polygon summaries;
- Hausdorff and Frechet-style candidate discovery;
- ANN candidate reranking surfaces;
- DBSCAN/outlier core-count surfaces;
- robot collision screening;
- bounded DB-style summaries;
- graph analytics rows;
- Barnes-Hut candidate discovery.

That list is a teaching catalog, not the fixed capacity of the language.

## Read Next

- [Quick Tutorial](quick_tutorial.md)
- [Application Catalog](application_catalog.md)
- [RTDL Language Docs](rtdl/README.md)
- [Partner Acceleration Boundaries](partner_acceleration_boundaries.md)
- [v2.0 Release Package](release_reports/v2_0/README.md)
