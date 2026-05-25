# Goal2586 Triangle-Counting Benchmark Boundary

Date: 2026-05-24

Status: revised after boundary correction. Graph analytics is not promoted as a
multi-operation benchmark; only triangle counting is promoted.

## Decision

Promote only triangle counting to a research benchmark app:

```text
examples/v2_0/research_benchmarks/triangle_counting/
```

The broader graph analytics app remains a learner/demo app. A benchmark should
have one clear output contract, one correctness oracle, and one baseline story.
Triangle counting is the right graph benchmark slice because it is easy to
understand, easy to test, and precise enough for future paper/baseline work.
Goal2588 then fixed the concrete paper target as RT-Graph from SIGMETRICS 2025,
using only its triangle-counting portion.

BFS and visibility-edge modes are learner/demo/example surfaces unless a future
goal promotes one of them as its own single-contract benchmark.

## Contracts

| Slice | Contract | Boundary |
| --- | --- | --- |
| RT-Graph-style triangle count one-step | triangle witness rows or compact triangle summary | not BFS, not general graph mining |

## Existing Evidence Boundary

Existing graph reports contain useful learner/demo evidence for BFS,
triangle-count, and visibility-edge modes, including Goal1297 visibility-edge
prepared-scene evidence. That evidence is not used to promote a broad graph
analytics benchmark.

The current benchmark evidence is intentionally modest:

- local CPU correctness through the existing graph triangle-count feature path;
- compact summary output for triangle count;
- explicit exclusion of BFS and visibility edges from the benchmark contract.

No performance wording is authorized yet for triangle counting. The paper/code
target is now RT-Graph, and a local Python preprocessing oracle exists for the
degree/ID-oriented triangle-count contract. A local id-ascending relabeling
adapter also checks that current RTDL CPU triangle matching can preserve the
same count after RT-Graph preprocessing. The remaining reproduction step is to
run the authors `bs_tc` and `rt_tc` triangle-counting programs on the same
preprocessed graph inputs, then compare RTDL `rt_graph_2a1_generic_rt` and
`rt_graph_1a2_generic_rt` OptiX rows against those rows.

## What This Adds To RTDL Design

Triangle counting is useful because it forces a narrower set of generic runtime
questions:

- Should row-output graph kernels expose raw row views before Python dict
  materialization?
- Which summaries belong as generic row-summary adapters rather than
  app-specific continuations?
- How do we preserve a strict boundary between Python graph semantics and
  app-agnostic engine primitives?

## Claim Boundary

Authorized:

- Triangle counting is now a bounded research benchmark app.
- The benchmark has a single graph output contract: triangle witness rows or a
  compact triangle summary.
- The benchmark is app-name-free at the native engine boundary.
- The broader graph analytics app remains available as a learner/demo example.

Not authorized:

- Claiming graph analytics as a multi-operation benchmark.
- Full graph database, shortest path, or distributed graph analytics claims.
- BFS RT-core acceleration claims.
- Triangle-count RT-core acceleration claims.
- Visibility-edge benchmark claims from this goal.
- Whole graph analytics speedup claims.
- Public speedup wording without a fresh same-contract triangle-count
  comparison and the required review/consensus gate.

## Next Work

If we continue this benchmark, the right next gate is not app-specific engine
code. It is a matched same-contract triangle-counting comparison:

1. deterministic RT-Graph preprocessing fixtures and Python oracle;
2. RTDL id-ascending adapter CPU correctness;
3. RTDL RT-2A1 generic ray/triangle `ANY_HIT` mapping correctness;
4. RTDL RT-1A2 generic ray/triangle `HIT_COUNT` mapping correctness;
5. authors-code `bs_tc` and `rt_tc` runs on a CUDA/OptiX pod;
6. RTDL Embree/OptiX rows only if the output contract remains identical;
7. external review before any performance wording.

The immediate target report is
`docs/reports/goal2588_rt_graph_triangle_counting_paper_code_intake_2026-05-24.md`.
