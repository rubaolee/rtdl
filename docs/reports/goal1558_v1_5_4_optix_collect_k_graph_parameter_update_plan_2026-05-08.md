# Goal 1558: OptiX COLLECT_K Graph Parameter Update Plan

## Verdict

The next production candidate should use CUDA graph kernel-node parameter update, not capture a fresh graph every merge level.

Goal 1557 proved that the real four-kernel compact-level sequence is graph-replayable and faster in isolation. A production path still needs a way to reuse graph executables when collect-k level parameters change. CUDA 12.8 exposes `cuGraphExecKernelNodeSetParams`, so the next candidate can test graph executable reuse with updated kernel parameters.

## Evidence

- Pod: `root@157.157.221.29 -p 22942`
- SSH key used: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- CUDA header checked: `/usr/local/cuda-12.8/include/cuda.h`
- Current repo commit before this note: `1b7b7f06`

The CUDA 12.8 header maps:

- `cuGraphKernelNodeSetParams` to `cuGraphKernelNodeSetParams_v2`
- `cuGraphExecKernelNodeSetParams` to `cuGraphExecKernelNodeSetParams_v2`

The active `CUDA_KERNEL_NODE_PARAMS` struct includes:

- `CUfunction func`
- `gridDimX`, `gridDimY`, `gridDimZ`
- `blockDimX`, `blockDimY`, `blockDimZ`
- `sharedMemBytes`
- `void **kernelParams`
- `void **extra`

The runtime API needed for executable updates is:

`CUresult CUDAAPI cuGraphExecKernelNodeSetParams(CUgraphExec hGraphExec, CUgraphNode hNode, const CUDA_KERNEL_NODE_PARAMS *nodeParams);`

## Target Block

The production graph candidate should remain scoped to the same Goal 1557 block:

1. `collect_k_bounded_i64_row_width2_final_materialize_level_counts_derived`
2. `collect_k_bounded_i64_row_width2_final_mark_counts_level_counts`
3. `collect_k_bounded_i64_row_width2_final_prefix_offsets_level`
4. `collect_k_bounded_i64_row_width2_final_compact_level_derived`

This block is the right target because its dependencies are device-side and it already matches the accepted current stack:

`RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1 RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1 RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT=1 RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS=1 RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS=1 RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS=1`

## Required Candidate Shape

Add an opt-in runtime flag only after a parameter-update diagnostic passes:

`RTDL_OPTIX_COLLECT_K_LEVEL_GRAPH_REPLAY=1`

The candidate should:

- Capture one graph for the four-kernel compact-level block.
- Extract and retain the four kernel nodes with `cuGraphGetNodes`.
- Before replaying a level, rebuild `CUDA_KERNEL_NODE_PARAMS` for each kernel node.
- Update the executable with `cuGraphExecKernelNodeSetParams`.
- The candidate must fall back to the current direct-launch path if graph update fails, topology is unsupported, or any invariant is uncertain.

## Invariants

The first production candidate should be deliberately narrow:

- Use only the current device-count/device-prefix/derived-descriptor path.
- Require no host-visible dependency inside the captured block.
- Require `total_blocks <= 512`, matching the existing fixed block-count buffers.
- Keep the final two-segment path on the current direct implementation unless separately proven.
- Do not capture tile sorting, tile overflow validation, final host count publication, or carry copies.

## Acceptance Criteria

The candidate is acceptable only if all are true:

- Same candidate rows as the accepted current path.
- Same emitted count.
- Same overflow flag.
- Same profile topology except for explicit graph-replay accounting.
- Same-contract timing beats the accepted Goal 1552 stack on `65537` and `131072` candidates.

If capture plus per-level parameter update preserves parity but does not beat the accepted stack, record it as a negative result and keep the default path unchanged.

## Claim Boundary

This is an implementation plan, not a measured production optimization. It does not change runtime behavior, does not publish a user-visible feature, and does not authorize public speedup wording.
