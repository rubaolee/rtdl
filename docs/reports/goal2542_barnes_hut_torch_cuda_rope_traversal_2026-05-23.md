# Goal2542 Barnes-Hut Torch/CUDA Resume-Index Rope Traversal

Date: 2026-05-23

## Scope

Goal2542 replaces the first Torch/CUDA fused vector-sum prototype's explicit
per-thread traversal stack with DFS `resume_index` traversal.

Implementation:

`scripts/goal2542_barnes_hut_torch_cuda_rope_vector_sum.py`

Contract:

`generic_aggregate_frontier_weighted_vector_sum_2d_v1`

This is still a Torch/CUDA partner prototype, not OptiX and not public speedup
evidence.

## Design

The previous Goal2541 kernel used:

- one CUDA thread per source;
- local-memory stack per thread;
- child push/pop traversal.

The Goal2542 kernel uses:

- one CUDA thread per source;
- DFS-ordered aggregate-tree arrays;
- `node_resume_index` as an autorope-like continuation pointer;
- first-child descent for non-accepted internal nodes;
- resume-index skip after accepted aggregate nodes and leaves.

This keeps the same semantics while avoiding the explicit stack and its
overflow/size policy.

## Pod Evidence

Pod:

`ssh root@203.57.40.169 -p 10297 -i ~/.ssh/id_ed25519_rtdl_codex`

Artifacts:

- `docs/reports/goal2542_barnes_hut_torch_cuda_rope_vector_sum_pod_8192_2026-05-23.json`
- `docs/reports/goal2542_barnes_hut_torch_cuda_rope_vector_sum_pod_32768_2026-05-23.json`

Correctness:

- `visited_node_total` delta: `0`
- `contribution_row_count` delta: `0`
- checksum deltas: floating-point-ordering noise only

## Diagnostic Timing

All timings are resident CUDA kernel times on the RTX A5000 pod. They are
diagnostic engineering evidence only.

| Bodies | Stack kernel min (ms) | Rope kernel min (ms) | Observation |
|---:|---:|---:|---|
| 8,192 | 7.12 | 7.03 | small improvement |
| 32,768 | 37.35 | 37.04 | small improvement |

The rope traversal is correct and slightly faster, but the improvement is
modest. That means the dominant costs are likely:

- divergence from source-dependent opening decisions;
- member-scan cost for `contains_source`;
- exact-leaf contribution loops;
- one-thread-per-source occupancy limits;
- memory access patterns over packed member arrays.

## Engineering Conclusion

Resume-index traversal is worth keeping because it simplifies the kernel and
removes stack sizing from the ABI. It is not, by itself, the major performance
breakthrough.

The next optimization should target the actual hot spots:

- replace per-node linear `contains_source` scans with a source-cell or range
  containment test;
- split aggregate-accepted work from exact-leaf work if divergence dominates;
- assign warps or blocks to high-work sources instead of one thread per source;
- preserve tree/body tensors across repeated timesteps and benchmark only the
  resident kernel path.

## Claim Boundary

This goal authorizes only bounded internal statements:

- RTDL has a correct Torch/CUDA resume-index rope prototype for the generic
  fused vector-sum contract.
- The rope prototype is slightly faster than the explicit-stack prototype on
  the tested RTX A5000 pod.
- The result supports future partner/native lowering work.

This goal does not authorize:

- public speedup wording;
- OptiX performance claims;
- authors-code comparisons;
- paper reproduction claims.
