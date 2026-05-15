# ITRE App Programming Model

ITRE is the current RTDL programming model:

1. **Input**: declare the data that enters the RTDL kernel.
2. **Traverse**: map expensive search or candidate generation to a
   ray-tracing-style traversal.
3. **Refine**: apply the rule that turns broad candidates into valid rows.
4. **Emit**: return rows, summaries, or partner-owned columns.

This page is v2.0-facing and avoids older release chronology. For older
version history, use
[Legacy Learner Doc Version Notes](../history/legacy_learner_doc_version_notes.md).

## The Honest Claim

RTDL does not claim that ITRE alone is a complete application language.

RTDL does claim that ITRE is a useful kernel model for the expensive
query/traversal part of apps that can be decomposed into:

- structured inputs;
- candidate search or intersection traversal;
- bounded refinement;
- row or column emission;
- Python-side orchestration and reduction.

The intended app shape is:

```text
Python prepares data
  -> RTDL ITRE kernel emits rows or partner-owned columns
  -> Python or a partner framework reduces results into the app answer
```

## What RTDL Owns

RTDL owns the heavy query kernel:

- typed kernel inputs;
- probe/build roles;
- traversal intent;
- backend dispatch;
- candidate generation;
- refinement semantics inside the bounded workload contract;
- emitted row schema or partner-owned output contract.

## What Python Owns

Python owns the app:

- loading and shaping domain data;
- building fixtures, trees, graphs, tables, or pose batches;
- multi-step orchestration;
- app control flow and iteration;
- reductions that are not RTDL primitives;
- visualization and file output;
- comparison against app-level or external baselines.

## What Partners Own

In the v2.0-facing path, partner frameworks can own input and output columns:

- NumPy for host/CPU arrays;
- PyTorch for the reference GPU partner path;
- CuPy for lightweight GPU conformance and RawKernel-friendly continuations.

RTDL does not optimize arbitrary partner programs. It runs the supported RTDL
primitive and hands results back through the documented contract.

## App Mapping

| App shape | ITRE-covered core | App/partner-owned continuation |
| --- | --- | --- |
| Hausdorff distance | nearest-candidate rows or threshold summaries | exact distance policy, witness reporting |
| ANN candidate search | candidate-subset KNN/radius rows | index choice, recall metrics, full-set comparison |
| Outlier detection | fixed-radius density rows/counts | threshold policy and labeling |
| DBSCAN clustering | fixed-radius core counts/flags | cluster expansion |
| Robot collision screening | ray/triangle any-hit pose flags/counts | pose generation and planner decisions |
| Barnes-Hut force approximation | body/node candidate discovery | opening rule and force-vector reduction |
| Segment/polygon any-hit | candidate or exact witness columns | downstream app-specific geometry handling |
| Database analytics | bounded columnar scan/group summaries | dashboard policy and reporting |
| Graph analytics | frontier/edge and triangle-style rows | graph-system policy and presentation |

## Pressure Points

When an app needs more than rows, choose a better output contract instead of
moving app logic into the native engine:

- compact count columns;
- boolean flags;
- threshold summaries;
- bounded candidate summaries;
- streaming exact witness columns;
- partner-owned arrays for downstream PyTorch/CuPy work.

That is the v2.0 lesson: keep the engine generic, but give Python and partner
frameworks efficient output shapes.

