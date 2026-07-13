# Call For Review - Goal5191 Inline Nearest Threshold And Empty-Frontier Fast Path

Please strictly review Goal5191.

## Files Under Review

Implementation:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
tests/goal5191_inline_frontier_fastpath_test.py
```

Result report:

```text
history/internal_docs/goal5191_inline_nearest_threshold_and_empty_frontier_fastpath_result_2026-07-08.md
```

Evidence artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_goal5189_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline128_goal5191_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline256_goal5191_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline512_goal5191_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline512_fastpath_goal5191_final_graphics_dragon_happy_buddha_2026-07-08.json
```

## Context

Goal5189 made the local-grid seed the fastest full-public Level-B route, but
it increased frontier/continuation work:

```text
route ~= 5.98s
frontier rows = 7,590,188
nearest continuation ~= 2.03s
```

Goal5190 tried a tighter grid branch-bound seed. It reduced frontier rows but
made seed time too expensive:

```text
route ~= 7.71s
seed ~= 4.60s
frontier rows = 1,811,625
```

Goal5191 therefore attacks the expanded generic frontier/continuation path
instead of inventing an X-HD-specific primitive.

## What Changed

1. Measured a threshold sweep for existing generic native inline-nearest:

```text
max_inline_points = 64, 128, 256, 512
```

2. Added an app-runner empty-frontier fast path:

```text
_nearest_from_complete_frontier_state(...)
```

This path is used only when the generic native frontier collector returns
`row_count == 0`, meaning inline-nearest state has already resolved every query.
It fails closed unless source ids match, all nearest item ids are non-negative,
and all nearest distances are finite.

3. Added audit fields:

```text
max_inline_points
complete_frontier_state_passthrough
```

## Key Result

Full public Stanford Dragon/HappyBuddha Level-B route:

```text
source points = 437,645
target points = 543,652
backend = optix
initial_state = local-grid-cell
frontier_inline_nearest = true
max_inline_points = 512
```

Final Goal5191 result:

```text
matched = true
rtdl_route_distance = 0.12572988629271128
author_abs_diff = 2.3848857610975216e-09
route_wall = 3.647909864783287s
total = 6.382600784301758s
frontier_rows = 0
complete_frontier_state_passthrough = true
continuation_candidate_distance_evaluations = 0
```

Threshold sweep:

| Route | max_inline_points | matched | frontier rows | route wall | continuation |
|---|---:|---:|---:|---:|---:|
| Goal5189 local-grid baseline | 64 | true | 7,590,188 | 5.982s | 2.031s |
| Goal5191 inline128 | 128 | true | 3,647,552 | 4.970s | 1.147s |
| Goal5191 inline256 | 256 | true | 505,884 | 4.027s | 0.337s |
| Goal5191 inline512 | 512 | true | 0 | 3.723s | 0.155s |
| Goal5191 inline512 + fast path | 512 | true | 0 | 3.648s | 0.016s |

## Review Questions

1. Does the threshold sweep fairly compare the same Level-B full-public
   Dragon/HappyBuddha route under the same author-only comparator?
2. Is the `max_inline_points=512` interpretation correct: native inline-nearest
   consumes all frontier work (`frontier_rows=0`) and the remaining route cost
   is native collector plus seed, not Python continuation?
3. Is `_nearest_from_complete_frontier_state(...)` safe and fail-closed?
   Specifically, does it reject incomplete nearest state rather than silently
   treating an empty row table as success?
4. Is the empty-frontier fast path appropriately kept as app-route
   orchestration rather than a new RTDL core primitive?
5. Do the tests sufficiently cover complete state, missing witness, source-id
   mismatch, and app-neutral helper wording?
6. Does the final artifact expose enough audit fields
   (`max_inline_points`, `complete_frontier_state_passthrough`,
   `nearest_executor`, `frontier_rows`) to prevent hidden regime changes?
7. Does the report avoid overclaiming author performance parity, exact paper
   dataset reproduction, full paper reproduction, or Figure reproduction?
8. Is the next-bottleneck conclusion correct: after Goal5191, continuing to
   attack Python continuation is stale because `frontier_rows=0`; future route
   work must target generic native inline-nearest collector cost or local-grid
   seed cost?

## Requested Verdict Labels

If approved:

```text
approve_goal5191_inline_nearest_threshold_and_empty_frontier_fastpath
```

If blocked, please use a specific label:

```text
block_goal5191_due_to_unsafe_empty_frontier_passthrough
block_goal5191_due_to_unfair_threshold_comparison
block_goal5191_due_to_claim_boundary_overreach
block_goal5191_due_to_insufficient_genericity_or_test_coverage
```
