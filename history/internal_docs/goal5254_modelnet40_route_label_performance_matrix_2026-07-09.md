# Goal5254 - ModelNet40 Route-Label Performance Matrix

Date: 2026-07-09

## Verdict

```text
completed_modelnet40_route_label_performance_matrix__two_routes_two_claims
```

Goal5254 builds a denominator-explicit performance matrix for the two current
ModelNet40 all-400 routes:

```text
Goal5252 fast scalar route
Goal5253 exact-witness route
```

The purpose is to stop mixing two different route labels:

```text
fastest scalar HDResult route != exact per-source witness route
```

## Reproducible Artifact

New script:

```text
Paper-reproduction-apps/x-hd-paper/scripts/summarize_modelnet40_route_matrix.py
```

Generated matrix:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5254_modelnet40_route_label_performance_matrix_2026-07-09.json
```

Inputs:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5252_modelnet40_all400_scalar_route_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5253_modelnet40_all400_exact_seed_summary_2026-07-09.json
```

The matrix requires identical case sets. It verified:

```text
case_count = 400
case_sets_identical = true
```

## Route Labels

### Route A - Fast Scalar HDResult Route

Source:

```text
Goal5252
```

Contract:

```text
matches scalar author HDResult for all 400 unique ModelNet40 pair identities
per-source witnesses may be approximate
missing-nearest fallback may be used
```

Key facts:

```text
matched_case_count = 400 / 400
per_source_witness_exact = false
fallback cases = 5 / 400
```

### Route B - Exact-Witness Route

Source:

```text
Goal5253
```

Contract:

```text
matches scalar author HDResult for all 400 unique ModelNet40 pair identities
per-source witnesses exact for all 400 cases
no missing-nearest fallback
```

Key facts:

```text
matched_case_count = 400 / 400
per_source_witness_exact = true for 400 / 400
missing_nearest_fallback_count = 0 for 400 / 400
```

## Performance Matrix

All values below are for the same 400 unique ModelNet40 pair identities.

### RTDL Route Wall Time

```text
fast scalar route:
  sum    = 145.7630049586296s
  median = 0.08398602157831192s
  p95    = 0.6801847975701094s
  max    = 78.96278008818626s

exact-witness route:
  sum    = 424.56292333453894s
  median = 0.6934860087931156s
  p95    = 3.2292991522699594s
  max    = 13.780185401439667s
```

### RTDL Total Wall Time

```text
fast scalar route:
  sum    = 341.9941695705056s
  median = 0.3934122584760189s
  p95    = 2.216995434463024s
  max    = 79.32846986502409s

exact-witness route:
  sum    = 621.2066570222378s
  median = 1.0271642990410328s
  p95    = 4.3879532102495435s
  max    = 15.099454440176487s
```

### Author Denominators

Author process wall:

```text
sum    = 255.1015196442604s
median = 0.5192502588033676s
p95    = 1.306925006583333s
max    = 3.234994299709797s
```

Author internal `Running.AvgTime`:

```text
sum    = 2730.118ms
median = 5.8145ms
p95    = 11.7193ms
max    = 64.1ms
```

## Denominator-Separated Ratios

Against author process wall, sum-level:

```text
fast scalar route / author process wall = 0.571x
fast scalar total / author process wall = 1.341x

exact route / author process wall = 1.664x slower
exact total / author process wall = 2.435x slower
```

Against author internal `Running.AvgTime`, sum-level:

```text
fast scalar route / author AvgTime = 53.39x slower
exact route / author AvgTime = 155.51x slower
```

These are not parity claims. They are denominator-separated comparisons.

## Paired Case Ratios

Median paired ratio against author process wall:

```text
fast scalar route / author process wall = 0.1345x
exact route / author process wall = 1.1869x slower
```

Median paired ratio against author internal `Running.AvgTime`:

```text
fast scalar route / author AvgTime = 12.48x slower
exact route / author AvgTime = 107.25x slower
```

Median route-to-route ratio:

```text
exact route / fast scalar route = 6.599x slower
```

## Outliers

Fast scalar route worst case:

```text
tent_0112.off -> tent_0183.off
route_wall_sec = 78.96278008818626
```

This is the Goal5252 missing-nearest fallback tail.

Exact-witness route worst cases:

```text
flower_pot_0042.off -> flower_pot_0110.off route_wall_sec = 13.780185401439667
airplane_0130.off -> airplane_0396.off     route_wall_sec = 10.771588280797005
airplane_0384.off -> airplane_0569.off     route_wall_sec = 8.936780087649822
```

Exact-witness route has a much larger median, but a smaller max than the scalar
route because it avoids the scalar route's pairwise fallback tail.

## Interpretation

The project should carry two route labels:

```text
fast scalar route:
  use when the required observable is author HDResult only
  strongest performance number among current RTDL routes
  not exact per-source witnesses

exact-witness route:
  use when function completeness requires exact nearest witnesses
  slower
  no missing-nearest fallback
```

This distinction is necessary for the final X-HD reproduction report. Saying
"RTDL performance" without the route label is now ambiguous and should be
rejected in review.

## Claim Boundary

Allowed:

```text
Goal5254 provides a denominator-explicit performance matrix for two current
ModelNet40 all-400 RTDL route labels.
```

Forbidden:

```text
author internal Running.AvgTime parity
author RT-core algorithm equivalence
full X-HD paper reproduction complete
exact paper byte-input identity
Figure 5-11 reproduction
single unqualified RTDL speed number
```

## Next Step

Send Goal5254 for strict review.

If accepted, subsequent reports must cite route labels explicitly:

```text
Goal5252 fast scalar route
Goal5253 exact-witness route
```

The next technical choices are:

```text
1. Attack scalar fallback tail to make the fast route robust.
2. Optimize exact-witness route if exact witnesses are required for final parity.
3. Continue exact paper dataset and Figure reproduction work.
```
