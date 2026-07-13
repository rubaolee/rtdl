# Call For Review - Goal5195 Intersection Current-Best Pruning

Please strictly review Goal5195:

```text
history/internal_docs/goal5195_intersection_current_best_pruning_result_2026-07-08.md
```

Relevant implementation:

```text
src/native/optix/rtdl_optix_workloads.cpp
src/rtdsl/optix_runtime.py
src/rtdsl/partner_continuations.py
tests/goal5195_intersection_current_best_pruning_test.py
```

Relevant artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline512_intersection_pruning_run1_goal5195_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline512_intersection_pruning_run2_goal5195_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline512_intersection_pruning_run3_goal5195_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline512_intersection_pruning_telemetry_goal5195_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline512_intersection_pruning_final4_goal5195_graphics_dragon_happy_buddha_2026-07-08.json
```

## Context

Goal5194 changed any-hit cell classification to use the updated payload current
best. Goal5195 moves the same dynamic prune earlier into the intersection
program, so irrelevant cells do not call `optixReportIntersection` and do not
invoke any-hit.

This should be reviewed as generic nearest-state traversal behavior, not as an
X-HD-specific shortcut.

## Review Questions

1. Does the intersection program prune against payload current best before
   `optixReportIntersection`?
2. Is the prune safe with lower-target-id tie-breaks because it uses strict
   `min_sq > best` and preserves equal-distance cells?
3. Does the implementation preserve diagnostic pruned-row behavior by requiring
   `emit_pruned_rows == false` for the intersection-stage dynamic prune?
4. Is the implementation correctly narrowed to the inline-nearest +
   no-pruned-rows route, leaving non-inline behavior unchanged?
5. Does the change remain app-neutral in RTDL core and avoid X-HD / paper /
   author identity?
6. Are the tests sufficient as structural guards, given the full runtime
   behavior is validated by POD route gates?
7. Does the POD evidence show the full-public Level-B route still matches the
   author HDResult?
8. Is it fair to exclude the first no-telemetry run from timing comparison due
   to the clearly cold/noisy seed phase and use run2/run3 warmed no-telemetry
   timings?
9. Is the claimed route-local timing delta sound:
   about `3.456s -> 2.6s` route and `1.792s -> 0.93-0.94s`
   frontier/native inline?
10. Is it correct that telemetry point-evaluation counts stay at about `0.40B`
    because the new prune skips cells before any-hit rather than changing point
    scans inside accepted inline cells?
11. Are the claim boundaries correct: no author-vs-RTDL ratio, no exact paper
    dataset reproduction, no full X-HD paper reproduction?
12. Should Goal5195 close as `implemented_review_pending` with verdict
    `intersection_current_best_pruning_approved`, or are amendments required?

## Expected Answer Shape

```text
Verdict: <label>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers:
1. ...
...
12. ...
```
