# Goal5253 - ModelNet40 All-400 Exact-Seed Witness Route Result

Date: 2026-07-09

## Verdict

```text
completed_modelnet40_all400_exact_seed_witness_route__400_of_400_matched
```

Goal5253 adds a second ModelNet40 all-400 route:

```text
initial_state = grid-branch-bound
grid_branch_bound_seed_executor = native_cuda
skip_frontier_if_exact_seed = true
```

This route is slower than the Goal5252 scalar global-bound route, but it has a
stronger functional property:

```text
per_source_witness_exact = true for 400 / 400 cases
```

It is therefore the current ModelNet40 "functionally fuller" route, while
Goal5252 remains the faster scalar `HDResult` route.

## Harness Change

The ModelNet40 batch harness now exposes the existing route-gate shortcut:

```text
--skip-frontier-if-exact-seed
```

Files changed:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_modelnet40_normalized_batch_gate.py
tests/goal5223_modelnet40_algorithm_aware_comparator_test.py
```

This is only a harness passthrough. The underlying route capability already
existed in `run_xhd_cell_mbr_frontier_route_gate.py`.

## Why This Was Needed

Goal5252 found that the fast scalar route can require a generic missing-nearest
fallback in a small number of cases:

```text
fallback cases = 5 / 400
largest fallback case = tent_0112.off -> tent_0183.off
largest fallback route_wall_sec = 78.96278008818626
```

A direct tent comparison showed:

```text
current scalar global-bound route:
  matched = true
  per_source_witness_exact = false
  fallback source rows = 1,967
  fallback candidate rows = 31,759,182
  direction_total ~= 79.71s

same route with global-bound disabled:
  matched = true
  per_source_witness_exact = true
  fallback source rows = 1,967
  fallback candidate rows = 31,759,182
  direction_total ~= 79.80s

exact-seed skip route:
  matched = true
  per_source_witness_exact = true
  fallback source rows = 0
  direction_total ~= 0.971s
```

So the tent tail was not primarily a global-bound issue. It was a consequence
of using pairwise fallback for missing nearest witnesses. The exact-seed route
is the correct generic functional fallback for this kind of case.

## Evidence

Downloaded evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5253_modelnet40_all400_exact_seed_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5253_modelnet40_all400_exact_seed_artifacts_2026-07-09.tar.gz
```

The artifact tar includes:

```text
aggregate summary
all 10 chunk summaries
case-level summaries
author rerun JSONs
RTDL route JSONs
tent variant comparison JSONs
batch40 exact-seed comparison JSON
```

Aggregate result:

```text
matched_case_count = 400
failed_case_count = 0
all_cases_matched = true
```

Correctness envelope:

```text
max author_abs_diff    = 6.59728109919655e-08
median author_abs_diff = 7.368051571643441e-09
sum author_abs_diff    = 4.472201816704025e-06
tolerance              = 1e-6
```

Route-internal functional flags:

```text
per_source_witness_exact = true for 400 / 400
exact_seed_frontier_skipped = true for 400 / 400
initial_state = grid-branch-bound for 400 / 400
missing_nearest_fallback_count = 0 for 400 / 400
```

## Performance Envelope

RTDL exact-seed route, all 400 cases:

```text
route_wall_sec sum    = 424.56292333453894
route_wall_sec median = 0.6934860087931156
route_wall_sec max    = 13.780185401439667

total_sec sum         = 621.2066570222378
total_sec median      = 1.0271642990410328
total_sec max         = 15.099454440176487
```

Author rerun denominators for the same 400 cases:

```text
author process_wall_sec sum    = 255.03741998970509
author process_wall_sec median = 0.5205188095569611
author process_wall_sec max    = 3.2167051509022713

author Running.AvgTime sum ms    = 2794.7910000000006
author Running.AvgTime median ms = 5.8
author Running.AvgTime max ms    = 70.595
```

Denominator-separated interpretation:

```text
RTDL exact route sum / author process wall sum = 1.665x slower
RTDL exact total sum / author process wall sum = 2.436x slower

RTDL exact route sum / author internal Running.AvgTime sum = 151.91x slower
RTDL exact total sum / author internal Running.AvgTime sum = 222.27x slower
```

These numbers are intentionally not speedup/parity claims.

## Comparison With Goal5252 Scalar Route

```text
Goal5252 scalar route:
  400 / 400 matched
  per_source_witness_exact = false
  route_wall_sec sum = 145.7630
  route_wall_sec median = 0.0840
  route_wall_sec max = 78.9628
  fallback cases = 5

Goal5253 exact-seed route:
  400 / 400 matched
  per_source_witness_exact = true
  route_wall_sec sum = 424.5629
  route_wall_sec median = 0.6935
  route_wall_sec max = 13.7802
  fallback cases = 0
```

Interpretation:

```text
Goal5252 is the faster scalar HDResult route, but has approximate/aborted
per-source witnesses and a severe fallback tail.

Goal5253 is the stronger functional route, with exact per-source witnesses and
no missing-nearest fallback, but is slower overall.
```

## Claim Boundary

Allowed:

```text
The exact-seed route matched author reruns for all 400 unique ModelNet40 pair
identities and reports per_source_witness_exact=true for all 400 cases.
```

Allowed with caveat:

```text
This is stronger functional evidence than the scalar global-bound route, but it
is not the author's fused X-HD RT-core algorithm and not a performance parity
result.
```

Forbidden:

```text
full X-HD paper reproduction complete
exact paper byte-input identity
Figure 5-11 reproduction
author internal Running.AvgTime parity
speedup/parity claim
author algorithm equivalence
```

## Next Step

Send Goal5253 for strict review.

After review, the project can carry two honest ModelNet40 route labels:

```text
fast scalar route:
  Goal5252
  scalar HDResult coverage
  not exact per-source witnesses

exact witness route:
  Goal5253
  exact per-source witness coverage
  slower but functionally stronger
```

The remaining major work for full X-HD reproduction is:

```text
1. decide which route is the default for which product claim;
2. audit performance against author phases without mixing denominators;
3. continue exact paper dataset / Figure reproduction work beyond ModelNet40;
4. if performance parity is still desired, build a stronger generic traversal
   that narrows the gap to author Running.AvgTime without becoming X-HD-specific.
```
