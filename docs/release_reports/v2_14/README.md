# RTDL v2.14 Release Package

Status: current public release package for the v2.14 line. The active version
marker is `v2.14.1`.

RTDL v2.14.1 is the current public version of the project. It presents RTDL as
a Python-hosted language/runtime for expressing RT-shaped spatial, graph, and
analytics queries, with explicit partner continuation when an application needs
custom work after the RTDL primitive. It closes the v2.14 line by adding the
packaged RayJoin paper-reproduction app and Linux-validated public-sample
workflow.

This package is intentionally small. It gives users the current evidence and
wording rules without exposing internal review logs or historical release
churn.

## What Users Should Read

| File | Purpose |
| --- | --- |
| [v2.14.1 Closeout Note](v2_14_1_closeout.md) | What changed in the v2.14.1 closeout and what remains out of scope. |
| [Row-Scoped RT-Core Comparison](public_rt_vs_embree_comparison.md) | Current v2.14 same-contract benchmark rows and their claim boundaries. |
| [RayJoin Reproduction Packet](rayjoin_reproduction_packet.md) | Unified index for the bounded Section 5.2, 5.3, and 5.7 RayJoin reproduction evidence. |
| [RayJoin Section 5.7 Bounded Reproduction](rayjoin_section57_bounded_reproduction.md) | Current bounded RayJoin polygon-overlay reproduction evidence and its exact claim boundary. |
| [Public Wording Boundaries](public_wording_boundaries.md) | Safe wording for docs, papers, talks, and benchmark summaries. |
| [Benchmark Evidence Index](../../learn/benchmark_evidence_index.md) | Where the benchmark apps live and how to interpret their evidence. |
| [Current Claim Boundaries](../../learn/current_claim_boundaries.md) | What v2.14 does and does not claim. |

## Release Boundary

v2.14 supports row-scoped benchmark claims. A row may be used as performance
evidence only when the contract, backend, partner policy, dataset scale, and
baseline are all named.

v2.14 does not claim:

- every benchmark app is faster end to end;
- every RT-shaped program benefits from RT cores;
- arbitrary CuPy or Numba programs are automatically accelerated;
- full paper reproduction for every referenced system;
- archived or internal experimental work as current public API.

Historical materials and internal review records are archived under the
top-level [history](../../../history/README.md) directory.
