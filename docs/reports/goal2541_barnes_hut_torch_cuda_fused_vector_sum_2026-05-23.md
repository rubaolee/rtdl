# Goal2541 Barnes-Hut Torch/CUDA Fused Vector-Sum Prototype

Date: 2026-05-23

## Scope

This goal implements and validates the first partner-resident fused execution
prototype for the Barnes-Hut benchmark's generic core contract:

`generic_aggregate_frontier_weighted_vector_sum_2d_v1`

Implementation:

`scripts/goal2541_barnes_hut_torch_cuda_fused_vector_sum.py`

The script uses `torch.utils.cpp_extension.load_inline` to compile a CUDA
kernel that operates over prepared generic arrays:

- source point coordinates and masses;
- aggregate-tree node center, half-size, and mass arrays;
- packed member-index arrays;
- packed child-index arrays;
- per-node member and child offsets.

The kernel runs one CUDA thread per source, traverses the prepared aggregate
tree, applies the same opening predicate, and writes per-source vector sums and
counters.

## Claim Boundary

This is a Torch/CUDA partner prototype. It is not OptiX. It is not public speedup evidence. It is not:

- OptiX RT traversal;
- authors-code timing;
- RT-BarnesHut paper reproduction;
- public speedup evidence;
- native RTDL engine ABI.

The native engine remains app-name-free. The prototype targets the generic
fused vector-sum contract and records `native_engine_app_specific=false`.

## Pod Environment

Pod:

`ssh root@203.57.40.169 -p 10297 -i ~/.ssh/id_ed25519_rtdl_codex`

Relevant environment:

- GPU: NVIDIA RTX A5000
- Torch: `2.8.0+cu128`
- CUDA toolkit: `/usr/local/cuda-12.8`
- `ninja-build` installed for Torch extension compilation

## Correctness Evidence

The CUDA prototype was checked against the Python fused reference for 2,048,
8,192, and 32,768 bodies.

Artifacts:

- `docs/reports/goal2541_barnes_hut_torch_cuda_fused_vector_sum_pod_2048_2026-05-23.json`
- `docs/reports/goal2541_barnes_hut_torch_cuda_fused_vector_sum_pod_8192_2026-05-23.json`
- `docs/reports/goal2541_barnes_hut_torch_cuda_fused_vector_sum_pod_32768_2026-05-23.json`

For all three sizes:

- `visited_node_total` delta: `0`
- `contribution_row_count` delta: `0`
- checksum deltas: floating-point-ordering noise only

Largest recorded checksum deltas:

- 32,768 bodies `force_x`: `6.04e-10`
- 32,768 bodies `force_y`: `3.78e-10`

## Diagnostic Performance

All timings below are diagnostic engineering measurements only.

Torch/CUDA resident-kernel timings on RTX A5000:

| Bodies | Contribution rows | Visited nodes | Resident kernel min (ms) |
|---:|---:|---:|---:|
| 2,048 | 258,495 | 85,512 | 1.67 |
| 8,192 | 1,188,963 | 509,600 | 7.12 |
| 32,768 | 5,695,980 | 2,711,968 | 37.35 |

Same-contract C++ CPU baseline on the same pod:

| Bodies | Threads | Force time (ms) |
|---:|---:|---:|
| 8,192 | 16 | 6.01 |
| 32,768 | 16 | 58.29 |

Interpretation:

- At 8,192 bodies, the first CUDA prototype is near but still slower than the
  16-thread C++ baseline.
- At 32,768 bodies, the CUDA prototype is faster than the 16-thread C++
  baseline for the same traversal and contribution counts.
- The result validates partner-resident fused execution as a real direction,
  not just a design document.

## Timing Boundary

The report separates:

- CPU tree preparation;
- Torch extension compilation;
- host-to-device tensor preparation;
- resident CUDA kernel time.

For 32,768 bodies:

- CPU tree preparation: `463.44 ms`
- host-to-device tensor preparation: `310.61 ms`
- resident CUDA kernel min: `37.35 ms`

This means the kernel is promising, but full application performance still
depends on prepared-tree lifetime and device-resident state reuse. A fair future
benchmark must specify whether tree/body arrays are reused across timesteps or
copied for each invocation.

## Engineering Conclusion

Goal2541 turns the Barnes-Hut next target from "native/partner lowering needed"
into a working CUDA partner prototype.

The next useful optimization is not more Python reference work. It is one of:

- reduce CUDA kernel divergence and local-memory stack overhead;
- encode traversal with rope/resume indices rather than an explicit stack;
- keep body and tree tensors resident across repeated timesteps;
- add a stable RTDL partner API wrapper around this kernel shape;
- later, re-target the same contract to OptiX once an OptiX SDK environment is
  available.

The most immediate follow-up should be a resident-state repeated-timestep
benchmark, because that will measure the performance model Barnes-Hut actually
needs: prepare once, update bodies/tree as needed, run many force evaluations.
