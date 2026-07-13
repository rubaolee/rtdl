# Call For Review - Goal5194 Payload Current-Best Pruning

Please strictly review Goal5194:

```text
history/internal_docs/goal5194_payload_current_best_pruning_result_2026-07-08.md
```

Relevant implementation:

```text
src/native/optix/rtdl_optix_workloads.cpp
src/rtdsl/partner_continuations.py
tests/goal5194_payload_current_best_pruning_test.py
```

Relevant artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline512_payload_pruning_goal5194_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline512_payload_pruning_rerun_goal5194_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline512_payload_pruning_rerun2_goal5194_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline512_payload_pruning_telemetry_goal5194_graphics_dragon_happy_buddha_2026-07-08.json
```

## Context

Goal5192 showed the current Goal5191 full-public Level-B route was dominated by
native inline-nearest work:

```text
inline_cell_hit_count ~= 12.00M
inline_point_evaluation_count ~= 1.24B
```

Inspection showed that the native any-hit program updated the nearest-state
payload after scanning an inline cell, but later cell classification still used
the original query seed distance. Goal5194 changes cell pruning to use the
payload current best when inline nearest is enabled.

This is intended as generic RTDL nearest-state payload traversal behavior, not
an X-HD-specific primitive.

## Review Questions

1. Does the implementation genuinely use the payload current best to classify
   later cells, rather than only the initial query seed?
2. Is the strict `min_sq > best` dynamic prune correct with respect to
   equal-distance lower-target-id tie-breaks?
3. Does the change remain app-neutral in RTDL core and avoid X-HD / paper /
   author identity in the native primitive?
4. Are the tests sufficient for a bounded structural guard, given that real
   runtime validation happens on POD?
5. Does the POD evidence show the full-public Level-B route still matches the
   author HDResult?
6. Is it fair to treat the first no-telemetry run as a cold/noisy seed outlier
   and use the two warmed no-telemetry reruns for route timing?
7. Are the telemetry work-reduction claims sound:
   `12.00M -> 3.64M` inline cell hits and `1.24B -> 0.40B` inline point evals?
8. Is the timing claim correctly bounded as route-local:
   about `3.70s -> 3.46s`, not an author-vs-RTDL performance ratio?
9. Does the metadata addition
   `inline_nearest_pruning=payload_current_best_min_cell_distance_gt_best`
   correctly describe the native behavior?
10. Should Goal5194 close as `implemented_review_pending` with verdict
    `payload_current_best_pruning_approved`, or are amendments required?

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
10. ...
```
