# Goal2585 RTNN Benchmark Front Door

Date: 2026-05-24

Status: formal benchmark front door added with strict claim boundary.

## Decision

Promote the existing RTNN campaign to a formal research benchmark app front
door:

```text
examples/v2_0/research_benchmarks/rtnn/
```

Continuous Frechet was demoted to learner/demo status because its current GPU
story does not beat optimized CPU C++ and there is no paper/authors-code target.
RTNN is the benchmark identity because the repository already has generic RTDL
nearest-neighbor contracts, RTNN-shaped 3-D fixed-radius evidence, CuPy
same-contract baseline rows, and optional official RTNN diagnostic rows.

The ANN candidate-quality slice remains a helper submode only. It is included
because it exercises candidate-subset top-k quality and threshold contracts,
not because this benchmark is being reframed as a full ANN app.

## Benchmark Scope

| Slice | Contract | Evidence |
| --- | --- | --- |
| ANN candidate quality | candidate-subset exact top-1 rerank compared with exact full-set top-1 | Goal1983 |
| ANN candidate threshold | prepared 2-D fixed-radius candidate-coverage decision | existing ANN app |
| RTNN ranked summary | exact 3-D fixed-radius bounded ranked-summary row per query | Goal2388 |
| External RTNN diagnostic | public RTNN binary on the same synthetic inputs | Goal2388 optional rows |

## What This Adds To RTDL Design

This benchmark stresses the parts of RTDL that are genuinely shared across
neighbor-search workloads:

- Packed-column input is the serious-performance path.
- Prepared search-side structures are required for repeated query batches.
- Device-side ranked summaries avoid materializing full witness rows when the
  user only needs bounded nearest-neighbor summaries.
- Partner-owned exact top-k can provide a quality reference without turning the
  native engine into an ANN engine.
- Density-aware partitioning remains the next generic improvement for clustered
  data.

## Pod Evidence Summary

Recorded Goal2388 pod: RTX A5000, CUDA 12, OptiX SDK, commit
`7738e6fd30d9eb57869afb7c5b17b5187586392e`.

Same-contract RTDL prepared OptiX versus CuPy all-pairs CUDA-core baseline:

| Distribution | Points | RTDL sec | CuPy sec | CuPy / RTDL |
| --- | ---: | ---: | ---: | ---: |
| uniform | 65,536 | 0.012051 | 26.004428 | 2157.8x |
| clustered | 65,536 | 0.204774 | 22.450877 | 109.6x |
| shell | 65,536 | 0.006513 | 15.335754 | 2354.7x |

RTDL scale rows:

| Distribution | Points | RTDL sec | Emitted rows |
| --- | ---: | ---: | ---: |
| uniform | 262,144 | 0.041202 | 262,144 |
| clustered | 262,144 | 2.705786 | 262,144 |
| shell | 262,144 | 0.193032 | 262,144 |

Official RTNN rows are preserved as diagnostic evidence, not same-contract
wins/losses. The public RTNN binary has a different witness/materialization
pipeline, and one clustered 262k row failed with CUDA allocation failure.

## Claim Boundary

Authorized:

- RTNN is now a research benchmark app with a discoverable front door.
- RTDL has generic prepared 3-D fixed-radius ranked-summary support.
- On the recorded RTX A5000 pod, the RTDL prepared OptiX ranked-summary path is
  much faster than the included CuPy all-pairs CUDA-core baseline for the same
  65k-point ranked-summary contract.
- The native engine remains app-name-free for this benchmark.

Not authorized:

- Full RTNN paper reproduction.
- Claim that RTDL beats official RTNN on the full RTNN paper contract.
- Claim that RTDL provides a native ANN index, graph index, IVF/HNSW/PQ, or
  training/build phase.
- Broad nearest-neighbor speedup wording.
- Public release wording without the required review/consensus gate.

## Next Work

The next useful work is not an app-specific engine path. It is generic
density-aware prepared partitioning and a stronger optimized CUDA-core grid/BVH
baseline if we want a harder non-RT baseline than all-pairs CuPy.
