# Goal5227 - ModelNet40 All-400 Chunk 0 Checkpoint Result

Date: 2026-07-09

## Verdict

```text
completed_modelnet40_all400_chunk0_checkpoint__25_of_400_matched
```

Goal5227 starts the all-400 unique ModelNet40 run using the operational controls
added in Goal5226. This checkpoint covers the first chunk only.

## Command Shape

The POD run used:

```text
--selection-strategy all_unique_pairs
--max-pairs 400
--chunk-index 0
--chunk-size 25
--skip-completed
--continue-on-error
--goal-label Goal5227
```

The runner wrote:

```text
/tmp/xhd-goal5227/modelnet40_all400/chunk_000_summary.json
/tmp/xhd-goal5227/modelnet40_all400/aggregate_after_chunk_000_summary.json
/tmp/xhd-goal5227/modelnet40_all400/cases/*.json
```

Downloaded local artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5227_modelnet40_all400_chunk000_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5227_modelnet40_all400_aggregate_after_chunk000_summary_2026-07-09.json
```

## Result

```text
selected_count = 25
matched_case_count = 25
failed_case_count = 0
all_cases_matched = true
total_points_min = 33,896
total_points_max = 2,726,286
max RTDL-vs-author HDResult diff = 1.0617538129253923e-07
route_wall_sec sum = 134.63958233594894
chunk elapsed_sec = 200.131474070251
```

The aggregate summary rebuilt from per-case artifacts also reports:

```text
selected_count = 25
matched_case_count = 25
failed_case_count = 0
all_cases_matched = true
```

This validates both:

```text
real chunk execution
aggregate-existing-cases reconstruction
```

on the actual POD all-400 output directory.

## Claim Boundary

Allowed:

```text
The first 25 of the 400 unique ModelNet40 pairs completed and matched under the
algorithm-aware public-OFF normalized route.
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

Continue chunks 1 through 15, then aggregate all case artifacts into a complete
all-400 summary.
