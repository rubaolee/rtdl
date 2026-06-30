# Goal2780 - Top-K Adapter over Triton Grouped Top-K

Date: 2026-05-31

## Purpose

Goal2780 is the first benchmark-adapter wiring step after the v2.5 generic
primitive surface was broadened by Goals2776-2779.

It updates `top_k_nearest_points_2d_partner_columns(..., partner="triton")` so
the ranked nearest-neighbor adapter uses the generic v2.5 continuation
operation:

`grouped_topk_f64`

This keeps the native engine app-agnostic. The adapter still owns the app-side
point-distance materialization and query/candidate layout; the v2.5 continuation
only ranks generic `(group_id, item_id, score)` rows.

## What Changed

- `partner="triton"` now materializes squared-distance rows as:
  - `group_ids`: query row index
  - `item_ids`: candidate point id
  - `scores`: squared distance
- It then calls `run_triton_partner_continuation("grouped_topk_f64", ...)`.
- The output is mapped back to the existing public adapter columns:
  - `query_ids`
  - `neighbor_ids`
  - `distances`
  - `neighbor_rank`
- The existing `partner="torch"` branch was also repaired for CUDA execution:
  CUDA Torch cannot advanced-index `uint32` tensors, so query and candidate ids
  are normalized to `int64` for the ranked output path.

## Boundary

This is an adapter-level v2.5 preview, not an RT-core speedup claim and not a
public performance promotion. Its status remains `preview_not_promoted`.

The pod evidence proves:

- same-contract correctness against the Torch branch;
- deterministic distance-then-candidate-id tie break;
- the adapter can consume the generic `grouped_topk_f64` continuation.

The pod evidence also shows the current Triton grouped-top-k algorithm is much
slower than the Torch same-contract branch for this dense exact top-k adapter.
That is useful negative evidence: for RTNN-style app promotion, the v2.5 planner
must either keep Torch/CuPy as the selected app partner for this dense ranking
phase or replace the current iterative Triton preview with a better tiled/top-k
selection kernel before claiming performance.

## Pod Evidence

Pod: `69.30.85.171:22167`

GPU: NVIDIA RTX A5000

Torch: `2.8.0+cu128`

Artifact:
`docs/reports/goal2780_pod_artifacts/goal2780_topk_adapter_triton_pod_69_30_85_171_2026-05-31.json`

| Query Count | Candidate Count | k | Triton Sec | Torch Sec | Triton/Torch | Correct |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2 | 3 | 2 | 0.022616 | 0.000478 | 47.28x slower | yes |
| 256 | 512 | 8 | 0.078513 | 0.000520 | 150.90x slower | yes |
| 512 | 1024 | 8 | 0.079224 | 0.000552 | 143.50x slower | yes |

All rows matched Torch on query ids, neighbor ids, neighbor ranks, and distances
with zero recorded max absolute error.

## Validation

Local Windows:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal2780_topk_adapter_triton_grouped_topk_test.Goal2780TopKAdapterTritonGroupedTopKTest.test_adapter_source_routes_triton_through_generic_grouped_topk

Ran 1 test in 0.002s
OK
```

Local CUDA-gated test skipped as expected on Windows without executable Torch
CUDA:

```text
Ran 1 test in 0.001s
OK (skipped=1)
```

Pod:

```text
PYTHONPATH=src:. timeout 180 python3 -m unittest \
  tests.goal2780_topk_adapter_triton_grouped_topk_test.Goal2780TopKAdapterTritonGroupedTopKTest.test_triton_topk_adapter_matches_same_contract_torch_reference_when_cuda_available

Ran 1 test in 2.744s
OK
```

Clean pod artifact command:

```text
timeout 240 python3 goal2780_pod_run.py
status: pass
```

## Decision

Goal2780 is accepted as adapter wiring and negative performance evidence.

It does not promote `grouped_topk_f64` as the RTNN performance path. It does
make the design more traceable: the top-k adapter now has a real v2.5 generic
primitive route, and the benchmark planner has concrete evidence that the
current dense Triton top-k preview is correctness-ready but not performance-ready.
