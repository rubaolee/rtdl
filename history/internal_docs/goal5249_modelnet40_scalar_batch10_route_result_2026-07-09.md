# Goal5249 - ModelNet40 Scalar Route Batch10 Result

Date: 2026-07-09

## Verdict

```text
completed_modelnet40_scalar_batch10_current_route__10_of_10_matched
```

Goal5249 upgrades the ModelNet40 batch harness so it can run the current
Goal5247 scalar route, then runs a 10-category ModelNet40 batch through that
route on the POD.

This closes a practical harness gap: before Goal5249, the batch runner called
the cell-MBR route but did not expose the current scalar route's important
generic switches:

```text
--grid-cell-builder native_cuda
--global-bound-early-break
--grid-cell-point-order
--grid-branch-bound-seed-executor
```

## Implementation

Updated app-owned batch harness:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_modelnet40_normalized_batch_gate.py
```

The harness now forwards:

```text
grid_cell_builder=args.grid_cell_builder
grid_cell_point_order=args.grid_cell_point_order
grid_branch_bound_seed_executor=args.grid_branch_bound_seed_executor
global_bound_early_break=bool(args.global_bound_early_break)
```

and exposes CLI flags:

```text
--grid-cell-builder {numpy,native_cuda}
--grid-cell-point-order {point-id,input-stable}
--grid-branch-bound-seed-executor
--global-bound-early-break
```

This is still app-owned X-HD reproduction harness code. It does not promote
ModelNet40, X-HD, Hausdorff, or paper-specific logic into RTDL core.

## POD Run

Command shape:

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_modelnet40_normalized_batch_gate.py
  --selection-strategy smallest_unique_pairs_preferring_distinct_categories
  --max-pairs 10
  --backend optix
  --grid-shape 96,60,72
  --initial-state local-grid-cell
  --local-grid-seed-executor native_cuda
  --grid-cell-builder native_cuda
  --frontier-inline-nearest
  --global-bound-early-break
  --frontier-row-order native
  --author-float32-normalization
  --tolerance 1e-6
```

Evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5249_modelnet40_scalar_batch10_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5249_modelnet40_scalar_batch10_artifacts_2026-07-09.tar.gz
```

## Result

```text
selected_count = 10
matched_case_count = 10
failed_case_count = 0
all_cases_matched = true
```

Selected categories:

```text
glass_box, cone, bowl, door, wardrobe, cup, range_hood, stool, bottle, lamp
```

Point-count range:

```text
min total points = 2,307
max total points = 32,493
```

This is a category-spread smoke batch, not a large-scale stress batch.
Goal5250 separately handles the largest ModelNet40 unique pair.

Correctness envelope:

```text
max author_abs_diff    = 3.139302651167242e-08
median author_abs_diff = 8.794353578700509e-09
tolerance              = 1e-6
```

Performance envelope:

```text
route_wall_sec sum    = 1.4580294042825699
route_wall_sec median = 0.092891626060009
route_wall_sec max    = 0.4323243573307991

total_sec sum         = 2.1115300729870796
total_sec median      = 0.173872459679842
total_sec max         = 0.4413299411535263
```

Author denominators for the same 10 cases:

```text
author process_wall_sec sum    = 4.435897625982761
author process_wall_sec median = 0.42454567179083824

author Running.AvgTime sum ms  = 50.647
author Running.AvgTime median ms = 4.914
```

These timings are denominator-explicit diagnostics only. They are not
authorized as speedup or parity claims.

## Claim Boundary

Allowed:

```text
The current scalar route matches the author paper-branch comparator on a
10-case, 10-category ModelNet40 public-OFF batch under author-float32
normalization.
```

Forbidden:

```text
all ModelNet40 scalar route coverage
exact paper byte-input identity
exact per-source witness output
full X-HD paper reproduction
author internal Running.AvgTime parity
speedup/parity claim
```

## Validation

Local:

```text
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_modelnet40_normalized_batch_gate.py
py -m unittest tests.goal5223_modelnet40_algorithm_aware_comparator_test

Ran 10 tests in 1.472s
OK
```

POD:

```text
wrote /tmp/xhd-goal5249/modelnet40_scalar_batch10_summary_2026-07-09.json
matched= True cases= 10 / 10
```

## Next Step

Send Goal5249 with Goal5250 for strict review. Goal5249 proves the current
scalar route can be used through the batch harness and matches 10 selected
ModelNet40 categories. Goal5250 separately checks the largest unique pair.
