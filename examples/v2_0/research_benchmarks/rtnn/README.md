# RTNN Neighbor-Search Benchmark

This directory is the formal front door for the existing RTNN benchmark
campaign. It wraps the RTNN scripts and evidence into the research-benchmark
tree.

The older ANN candidate-quality example is exposed only as a helper submode
because it shares top-k quality and candidate-threshold contracts. It is not
the benchmark identity.

The target paper family is RTNN-style hardware ray-tracing neighbor search. The
public RTNN implementation is treated as an optional diagnostic baseline because
its materialization pipeline is not the same as RTDL's ranked-summary contract.

## What This Benchmark Owns

| Contract | RTDL surface | Boundary |
| --- | --- | --- |
| ANN candidate quality | 2-D candidate-subset top-1 rerank and exact full-set comparison | not an ANN index or training phase |
| ANN candidate threshold | prepared fixed-radius candidate-coverage decision | not nearest-neighbor ranking |
| RTNN-shaped ranked summary | prepared 3-D fixed-radius bounded ranked-summary rows | not full RTNN paper reproduction |

## Local Commands

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py --mode scope
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py --mode ann_cpu_quality --copies 1
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py --mode rtnn_known_results
```

## GPU Evidence

The promoted benchmark reuses the completed Goal2388 pod evidence:

- RTDL prepared OptiX ranked-summary rows.
- CuPy CUDA-core all-pairs baseline for the same ranked-summary contract.
- Optional official RTNN rows on the same RTX A5000 pod.

The important boundary is that the RTDL-vs-CuPy rows are same-contract; the
official RTNN rows are diagnostic unless a future goal proves output-contract
equivalence.

## Engine Boundary

No ANN-specific or RTNN-specific native ABI is added. The native engine sees
generic fixed-radius neighbor, ranked-summary, prepared-search, and partner
top-k contracts. Candidate selection, approximation policy, external-code
adaptation, and paper-comparison interpretation stay in Python and reports.
