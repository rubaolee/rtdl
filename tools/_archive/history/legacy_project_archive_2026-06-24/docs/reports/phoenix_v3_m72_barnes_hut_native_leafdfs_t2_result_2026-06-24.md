# Phoenix V3 M72 Barnes-Hut Native Fused Trunk Result

Date: 2026-06-24
Status: focused engineering result, not release authorization
Scope: Phoenix V3 only; no V4, no embedding, no C ABI, no all-app run

## Objective

Hit the named Set-A blocker instead of process work:

`set_a_barnes_hut_app_geomean_0_844x`

The required experiment was to route the Barnes-Hut aggregate-tree fused
weighted-vector path through the productized prepared-session runner, keep
intermediate force/vector state device-resident, and measure whether the
`0.844x` scorecard blocker moved on the same RT hardware.

## Implementation

The new front-door mode is:

`native_fused_vector_sum_cuda_device`

It routes through:

`run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session`

The generic native primitive is:

`generic_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_v1`

Native implementation work:

- Added executable native CUDA device-resident fused aggregate-tree traversal
  and vector/count accumulation behind the existing OptiX backend library
  symbols.
- Added `target_leaf_dfs` to the prepared native handle and changed subtree
  containment in the fused kernel from member-list scanning to DFS-interval
  membership.
- Kept claim boundaries strict: this is CUDA device-resident V3 evidence, not
  RT-core evidence. It does not call `optixTrace`, so RT-core speedup wording is
  still unauthorized.

## POD Evidence

Hardware:

`NVIDIA RTX 4000 Ada Generation, driver 550.127.05`

Evidence directory:

`docs/rebuild/v3/evidence/phoenix_v3_m72_barnes_hut_native_leafdfs_t2_20260624_101218/`

Summary file:

`docs/rebuild/v3/evidence/phoenix_v3_m72_barnes_hut_native_leafdfs_t2_20260624_101218/summary.json`

Run shape:

- body counts: `32768`, `65536`, `131072`
- repeat: `11`
- warmup: `3`
- baseline: `prepared_execution_fused_vector_sum_numba_cuda`
- candidate: `native_fused_vector_sum_cuda_device`

## Result

The trunk now executes and the blocker moved, but not enough for release.

- Native-vs-Numba runner geomean: `1.0650085688429665x`
- Projected scorecard value from `0.844x`: `0.8988672321034636x`
- Moved toward parity: `true`
- Crossed `0.98x` watch parity: `false`
- Crossed `1.00x` parity: `false`

Per scale:

| body_count | native_vs_numba | projected_from_0.844 | moved |
|---:|---:|---:|:---|
| 32768 | 1.0969955717741604x | 0.9258642625773914x | yes |
| 65536 | 1.1208920592538585x | 0.9460328980102566x | yes |
| 131072 | 0.9824051695846687x | 0.8291499631294604x | no |

Correctness checks in the evidence:

- contribution-row counts matched baseline at every measured scale
- force checksum differences stayed around floating-point roundoff scale
- `runtime_executed: true`
- `runtime_trunk_executes_end_to_end: true`
- `internal_device_residency_between_rtdl_phases: true`
- `hot_path_host_materialization: false`
- `rt_core_speedup_claim_authorized: false`

## Decision

This is real V3 trunk progress, not a release result.

The blocker moved from a projected `0.844x` to `0.899x` geomean, so the trunk
has a performance source. But it remains below the parity gates, and the largest
scale still regresses slightly versus the Numba CUDA trunk. V3 is still
`redo_required`; no all-app run, release, public speedup wording, broad
V3-over-V2 claim, RT-core claim, true-zero-copy claim, V4 work, embedding, or C
ABI work is authorized.

## Next Technical Work

Do not open a process/review loop here. The next engineering step should stay on
the blocker path:

1. Profile the native fused kernel at `131072` bodies, where the new kernel loses
   (`0.9824051695846687x` versus Numba).
2. Apply only generic aggregate-tree/runtime optimizations. Allowed examples:
   stack/register pressure reduction, launch shape tuning, tree-node layout
   tightening, source-id mapping removal for same-order source/target batches,
   and warm JIT/cubin cache discipline.
3. Rerun the same focused scorecard rows. If it reaches parity, proceed to the
   second blocker under the same runner discipline. If it cannot reach parity
   after generic runtime fixes, record that Barnes-Hut moved but does not clear
   the V3 high-performance bar.

## Goal-Level Decision Self-Audit

1. Was I foolish? Partly corrected. The foolish path would have been to present
   the first native implementation as success despite a `0.078x` geomean. I did
   not do that; the measured bottleneck forced a generic kernel fix.
2. What actions would make this foolish? Calling `1.065x` geomean or projected
   `0.899x` release-quality would be foolish. Claiming RT-core acceleration would
   be false because this path does not use `optixTrace`.
3. Is there another path that avoids being stuck? Yes: keep the next work bound
   to the named blocker and only apply generic runtime optimizations, or move to
   the next blocker after an explicit consensus decision.
4. Can we try a different path that truly solves the problem? Yes. The next
   possible different path is a real OptiX traversal implementation, but that
   must remain within V3 internal residency and must not become V4 embedding or
   public RT-core wording without evidence and review.
