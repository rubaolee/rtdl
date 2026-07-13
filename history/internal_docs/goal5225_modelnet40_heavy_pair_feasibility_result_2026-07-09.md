# Goal5225 - ModelNet40 Heavy-Pair Feasibility Result

Date: 2026-07-09

## Verdict

```text
completed_modelnet40_heavy_pair_feasibility__largest10_matched
```

Goal5225 probes whether the ModelNet40 algorithm-aware route can handle the
largest public-OFF pairs in the paper-log unique-pair set. This is the required
step before attempting all 400 unique ModelNet40 pairs.

## Why This Goal Was Needed

Goal5224 proved one selected pair per category:

```text
40 categories
40 selected pairs
40 / 40 matched
```

But the all-unique ModelNet40 set is much larger and much less uniform:

```text
unique pairs = 400
categories   = 40
pairs/category = 10

total_points min    = 2,307
total_points median = 104,654
total_points mean   = 201,893.8
total_points p90    = 444,077
total_points max    = 2,726,286
```

The largest cases are not small variants of the 40-category batch; they include
million-point objects. A direct all-400 run without heavy-pair evidence would be
poorly controlled.

## Implementation

The app-owned ModelNet40 batch runner gained explicit selection strategies:

```text
smallest_unique_pairs_preferring_distinct_categories
smallest_unique_pairs
largest_unique_pairs
all_unique_pairs
```

It also records `total_points` per case and selection min/max point counts.
This is app-owned paper-runner functionality only; it adds no ModelNet40,
X-HD, or Hausdorff paper semantics to RTDL core.

Local/remote validation:

```text
py -m py_compile run_xhd_modelnet40_normalized_batch_gate.py
py -m unittest tests.goal5223_modelnet40_algorithm_aware_comparator_test
Ran 7 tests OK

POD:
python3 -m unittest tests.goal5223_modelnet40_algorithm_aware_comparator_test
Ran 7 tests OK
```

## Evidence Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5225_modelnet40_algorithm_aware_largest1_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5225_modelnet40_algorithm_aware_largest10_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5225_modelnet40_heavy_pair_feasibility_artifacts_2026-07-09.tar.gz
```

## Largest-1 Probe

```text
strategy = largest_unique_pairs
selected_count = 1
case = airplane_0396 -> airplane_0050
total_points = 2,726,286
matched = true
author-vs-paper diff = 0.0
RTDL-vs-author diff = 1.0617538129253923e-07
RTDL route_wall = 9.3215s
RTDL full total = 15.8159s
```

## Largest-10 Probe

```text
strategy = largest_unique_pairs
selected_count = 10
matched_case_count = 10
all_cases_matched = true
total_points range = 942,931 .. 2,726,286
max author-vs-paper diff = 0.0
max RTDL-vs-author diff = 1.0617538129253923e-07
RTDL route_wall sum = 124.0838s
RTDL full total sum = 164.0274s
```

Top largest cases include:

```text
airplane_0396 -> airplane_0050       2,726,286 points
curtain_0001 -> curtain_0130         2,662,782 points
airplane_0061 -> airplane_0395       2,053,952 points
airplane_0130 -> airplane_0396       1,833,665 points
plant_0072 -> plant_0014             1,821,946 points
```

## Interpretation

The largest-pair probes show that the current algorithm-aware ModelNet40 route
does not immediately fail on the heaviest public-OFF cases. It can reproduce
the paper-log HDResult through the author-compatible normalization and
paper-branch Hybrid comparator even at multi-million-point scale.

This makes an all-400 unique-pair run plausible, but it also shows that all-400
is a long-running job that needs controlled execution. The largest-10 route
alone took about two minutes of RTDL route time and about 164 seconds including
the route input/load stages.

## Claim Boundary

Allowed:

```text
The algorithm-aware ModelNet40 route matched the 10 largest unique pairs by
point count, including a 2.7M-point pair.
```

Forbidden:

```text
All 400 unique ModelNet40 pairs are complete.
All 2000 ModelNet40 paper-log records are complete.
Exact paper input byte identity is proved.
ModelNet40 performance reproduction is complete.
Author-vs-RTDL performance ratio or parity is established.
Full X-HD paper reproduction is complete.
```

## Next Step

The next goal should run all 400 unique ModelNet40 pairs, but with explicit
operational controls:

```text
chunked execution
resume or skip-completed behavior
per-case artifact retention
failure capture instead of losing the whole run
summary aggregation after chunks
```

This is now justified by evidence: both the 40-category representative batch
and the largest-10 heavy batch pass.
