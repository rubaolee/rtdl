# Call For Review - Goal5244 X-HD Frontier Grid Shape and Grid Point Order

Please strictly review Goal5244.

## Files To Review

Primary result:

```text
history/internal_docs/goal5244_xhd_frontier_grid_shape_and_grid_point_order_result_2026-07-09.md
```

Implementation changes:

```text
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
tests/goal5244_grid_cell_input_stable_order_test.py
```

Key POD artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5244_grid_96x60x72_precompiled_inline1024_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5244_grid_107x60x72_precompiled_inline1024_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5244_grid_128x60x72_precompiled_inline1024_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5244_grid_128x72x72_precompiled_inline1024_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5244_grid_128x80x80_precompiled_inline1024_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5244_grid_128x80x96_precompiled_inline1024_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5244_grid_160x80x96_precompiled_inline1024_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5244_grid_160x96x96_precompiled_inline1024_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5244_grid_96x60x72_input_stable_precompiled_inline1024_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5244_grid_96x60x72_point_id_precompiled_inline1024_pod_2026-07-09.json
```

Relevant predecessor:

```text
history/internal_docs/goal5243_xhd_native_seed_phase_timing_and_precompiled_kernel_result_2026-07-09.md
```

## Review Questions

1. Does the grid-shape sweep support the no-go conclusion that `96x60x72`
   remains best among tested shapes?
2. Does the evidence show the tradeoff correctly: finer grids reduce inline
   point evaluations but increase frontier OptiX launch time enough to lose?
3. Are all compared grid-shape runs matched against the author value with the
   same author difference and exact per-source witness condition?
4. Is the new `cell_point_order` option app-neutral and generic rather than
   X-HD-specific?
5. Does `input-stable` preserve correctness?
6. Is the performance effect of `input-stable` properly bounded as tiny and
   single-run, not a major speedup?
7. Do the tests adequately verify the new point-order behavior and fail-closed
   path?
8. Does the report avoid unauthorized claims: full X-HD paper reproduction,
   exact paper byte identity, author internal AvgTime parity, Figure
   reproduction, universal grid-shape claim, or major performance win?
9. Is the next-work recommendation correct: stop app-level grid-shape tuning and
   attack the generic frontier/inline-nearest system path?

## Requested Verdict Shape

Please answer with:

```text
Verdict:
  approve_goal5244_grid_shape_no_go_and_input_stable_option
  OR approve_with_required_amendments
  OR block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to review questions:
  1. ...
  ...
  9. ...
```

## Expected Bounded Summary If Approved

Allowed:

```text
Goal5244 shows that after the precompiled seed fix, finer grid shapes do not
improve the Dragon -> scaled AsianDragon route. The current `96x60x72` shape
remains best among tested shapes because finer grids reduce inline point
evaluations but increase the frontier OptiX launch cost. Goal5244 also adds a
generic optional grid-cell point ordering mode, `input-stable`, which preserves
correctness and produced only a tiny single-run improvement. The remaining
dominant cost is still the generic frontier/inline-nearest phase, not app-level
grid-shape tuning.
```

Forbidden:

```text
Goal5244 completes full X-HD paper reproduction.
Goal5244 proves RTDL has author internal AvgTime parity.
Goal5244 finds a universally best grid shape.
Goal5244's input-stable order is a major performance win.
Goal5244 closes the frontier gap.
```
