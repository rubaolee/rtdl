# Goal1629 v1.6.x OptiX Collect-K Large-Count Guardrail

## Verdict

`large_count_guardrail_recorded`

The attempted post-Goal1628 larger-count probe should not be continued as a
performance benchmark. Current row-width-2 OptiX tiled collect-k support is
bounded at `candidate_count <= 131072`, corresponding to at most 64 tiles with
the 2048-row CUB tile-sort path. Counts above that boundary are expected to fall
back to `dynamic_row_width_single_thread_fallback`, which is not the optimized
tiled merge path that Goal1627 improves.

## Evidence

- Source guard: `src/native/optix/rtdl_optix_api.cpp` enables
  `row_width2_bounded_multi_tile_sort_merge` only when
  `row_width == 2 && candidate_count > 4096 && candidate_count <= 131072`.
- Workspace/descriptor shape: the current tiled path allocates per-level tile,
  merge, and pair-offset metadata slots sized for `64` entries.
- Preflight model: `scripts/goal1508_v1_5_4_optix_collect_k_tiled_preflight.py`
  accepts Goal1506 profile candidates only when the expected native path is
  `row_width2_bounded_multi_tile_sort_merge`.
- Pod observation: on the A4500 pod, `candidate_count=196609` with
  `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`, `repeats=1`, and a 60-second
  timeout produced no profile record before timeout. This is consistent with
  falling outside the optimized tiled path, not with a defer-merge-sync
  regression.

## Interpretation

Goal1627's deferred merge-sync diagnostic is currently meaningful only inside
the existing optimized tiled path. Larger counts require a separate engineering
track to expand the native tiled design beyond 64 tiles. That is a different
problem from the merge-sync host-barrier optimization.

The next large-count implementation work should start by changing the native
workspace/descriptor strategy, not by rerunning the current Goal1506 profiler at
larger counts. A safe extension would need explicit bounds, dynamic or enlarged
descriptor storage, tests for more than 64 tiles, and RTX evidence.

## Next Work

1. Keep Goal1627 focused on the current `<=131072` optimized tiled path.
2. Treat `>131072` row-width-2 collect-k as a new scale-extension task.
3. Before any more large-count pod runs, add or design the native support needed
   for more than 64 tiles.

## Claim Boundary

This report is an internal guardrail for v1.6.x performance work only. It does
not authorize public speedup wording, true zero-copy wording, stable
`COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, whole-application speedup
claims, release tags, or release action.
