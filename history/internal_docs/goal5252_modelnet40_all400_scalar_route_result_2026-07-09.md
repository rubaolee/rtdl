# Goal5252 - ModelNet40 All-400 Scalar Route Result

Date: 2026-07-09

## Verdict

```text
completed_modelnet40_all400_unique_pair_scalar_hdresult_route__400_of_400_matched
```

Goal5252 extends the current X-HD scalar `HDResult` route from selected
ModelNet40 samples to all 400 unique ModelNet40 pair identities represented in
the paper-branch log index.

This is a correctness milestone, not a performance-parity claim.

## Scope

Dataset / workload:

```text
selection_strategy = all_unique_pairs
selected unique pairs = 400
categories = 40
pairs per category = 10
point-count range = 2,307 to 2,726,286 total points
total points across 400 cases = 80,757,525
```

Route switches:

```text
backend = optix
grid_shape = 96,60,72
initial_state = local-grid-cell
local_grid_seed_executor = native_cuda
grid_cell_builder = native_cuda
frontier_inline_nearest = true
global_bound_early_break = true
frontier_row_order = native
author_float32_normalization = true
tolerance = 1e-6
```

Validation target:

```text
author rerun on public ModelNet40 OFF inputs after author-style float32
normalization
```

This is still not proof of exact paper byte-input identity.

## Evidence

Downloaded evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5252_modelnet40_all400_scalar_route_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5252_modelnet40_all400_scalar_route_full_artifacts_2026-07-09.tar.gz
```

The full artifact tar includes:

```text
aggregate summary
all chunk summaries
case-level summaries
author rerun JSONs
RTDL route JSONs
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

## Fixes Required During Goal5252

Goal5252 was not just a clean batch run. It exposed two correctness/safety
issues in the current scalar route.

### 1. Global-Bound Publish Safety

This was fixed in Goal5251 before the all-400 run:

```text
src/native/optix/rtdl_optix_workloads.cpp
if (kind == 2) {
    optixSetPayload_6(2u);
}
```

Meaning:

```text
do not publish a global scalar bound from a query that emitted deferred frontier rows
```

Without this fix, the ModelNet40 batch40 run failed on:

```text
chair_0162.off -> chair_0131.off
pre-fix abs diff = 0.0009493921217607892
```

### 2. Missing-Nearest Fallback

The all-400 run then exposed a second issue in chunk 3:

```text
door_0032.off -> door_0028.off
door_0016.off -> door_0122.off
```

The route could receive a complete frontier state that still had no nearest
witness for a small number of source rows. The failure was explicit:

```text
complete frontier state is missing nearest witnesses for source rows [...]
```

The route now fills such missing source rows with an app-neutral generic
fallback:

```text
generic_pairwise_l2_distance_candidate_rows -> generic_nearest_witness_columns
```

This fallback is a correctness safety net. It is not a performance route.

Fallback distribution in the all-400 evidence:

```text
fallback cases = 5 / 400
fallback source rows total = 1,988
fallback candidate rows total = 31,961,946
max fallback source rows in one case = 1,967
max fallback candidate rows in one case = 31,759,182
```

Fallback cases:

```text
door_0032.off -> door_0028.off       fallback rows = 6
door_0016.off -> door_0122.off       fallback rows = 6
tent_0112.off -> tent_0183.off       fallback rows = 1,967
wardrobe_0073.off -> wardrobe_0050.off fallback rows = 3
wardrobe_0063.off -> wardrobe_0073.off fallback rows = 6
```

The tent case is a major performance outlier and should be treated as the next
algorithmic target if performance work continues.

## Performance Envelope

RTDL current scalar route, all 400 cases:

```text
route_wall_sec sum    = 145.7630049586296
route_wall_sec median = 0.08398602157831192
route_wall_sec max    = 78.96278008818626

total_sec sum         = 341.9941695705056
total_sec median      = 0.3934122584760189
total_sec max         = 79.32846986502409
```

Author rerun denominators for the same 400 cases:

```text
author process_wall_sec sum    = 255.1015196442604
author process_wall_sec median = 0.5192502588033676
author process_wall_sec max    = 3.234994299709797

author Running.AvgTime sum ms    = 2730.118000000002
author Running.AvgTime median ms = 5.814500000000001
author Running.AvgTime max ms    = 64.1
```

Denominator-separated interpretation:

```text
RTDL route sum / author process wall sum = 0.571x
RTDL total sum / author process wall sum = 1.340x

RTDL route sum / author internal Running.AvgTime sum = 53.39x slower
RTDL total sum / author internal Running.AvgTime sum = 125.27x slower
```

These are not parity claims. They show that the current route is competitive
against author process-level wall time on many small cases, but it is still far
from the author's internal algorithm timing, and it has a severe fallback
outlier.

## Outliers

Worst route time:

```text
tent_0112.off -> tent_0183.off
route_wall_sec = 78.96278008818626
total_sec      = 79.32846986502409
fallback source rows = 1,967
fallback candidate rows = 31,759,182
```

Without the five fallback cases:

```text
non-fallback cases = 395
non-fallback route_wall_sec sum = 66.28839184343815
non-fallback route_wall_sec median = 0.08464935421943665
non-fallback route_wall_sec max = 3.018681950867176
```

Thus the median route is stable, but the fallback safety path creates a large
tail. That tail is the next performance mountain.

## Claim Boundary

Allowed:

```text
The fixed current scalar HDResult route matched author reruns for all 400 unique
ModelNet40 pair identities represented in the paper-branch log index.
```

Allowed with caveat:

```text
If the Goal5230 duplicate mapping is accepted, this gives scalar HDResult value
coverage for the ModelNet40 paper-log records via their 400 unique pair
identities. This still does not prove exact paper byte-input identity.
```

Forbidden:

```text
full X-HD paper reproduction complete
exact paper byte-input identity
exact per-source witnesses
author internal Running.AvgTime parity
Figure 5-11 reproduction
all X-HD datasets reproduced
X-HD RT-core algorithm parity
performance speedup/parity headline
```

Critical caveat:

```text
per_source_witness_exact = false for the scalar global-bound route
```

The route is scalar `HDResult` exact against the tested author reruns. It is not
an exact witness-producing route.

## Next Step

Send Goal5252 for strict review.

If accepted, the next technical target is not "more selected ModelNet40 cases";
the all-400 scalar correctness coverage is already done. The next choices are:

```text
1. Attack the fallback tail, especially tent_0112 -> tent_0183.
2. Convert the scalar route into an exact per-source witness route, if witness
   output becomes a requirement.
3. Return to dataset provenance / Figure reproduction blockers beyond ModelNet40.
4. Run a fairer author/RTDL performance-matrix review with explicit denominators.
```
