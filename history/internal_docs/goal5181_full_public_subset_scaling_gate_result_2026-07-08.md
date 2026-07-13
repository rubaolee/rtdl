# Goal5181 Full Public Subset Scaling Gate

Date: 2026-07-08

## Verdict

```text
completed_full_public_subset_scaling_gate__implemented_review_pending
```

Goal5181 extends Goal5180 from one bounded source subset to a small scaling
matrix over the full public Stanford Dragon/HappyBuddha Level B candidate.

This is bounded source-subset scaling against the full public target. It is not
an all-source route run, not exact paper dataset reproduction, not figure
reproduction, not full paper reproduction, and not a performance ratio.

## Implementation

New script:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
```

Command:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\run_xhd_full_public_subset_scaling_gate.py \
  --bridge Paper-reproduction-apps\x-hd-paper\results\xhd_priority_input_bridge_goal5178_graphics_dragon_happy_buddha_2026-07-08.json \
  --profile Paper-reproduction-apps\x-hd-paper\results\xhd_priority_input_scale_profile_goal5179_graphics_dragon_happy_buddha_2026-07-08.json \
  --output Paper-reproduction-apps\x-hd-paper\results\xhd_full_public_subset_scaling_gate_goal5181_graphics_dragon_happy_buddha_2026-07-08.json \
  --backend numpy \
  --grid-shape 32,32,32 \
  --source-limits 16,64,128 \
  --source-selection-policy evenly-spaced \
  --translate-each-input-to-min-bound \
  --frontier-nearest-executor auto \
  --frontier-row-order native \
  --max-exact-pair-evaluations 100000000 \
  --tolerance 1e-9
```

## Evidence Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_subset_scaling_gate_goal5181_graphics_dragon_happy_buddha_2026-07-08.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.full_public_subset_scaling_gate.v1
```

Status:

```text
full_public_candidate_bounded_subset_scaling_checked
```

## Inputs

```text
source: Dragon public Stanford full PLY, 437645 points
target: HappyBuddha public Stanford full PLY, 543652 points
preprocessing: translate_each_input_to_min_bound
grid shape: 32 x 32 x 32
backend: numpy
```

The full source and full target are loaded once. Each case selects deterministic
evenly spaced source rows and runs the scalable route against the full target.

## Results

```text
all_matched: true

source_limit=16:
  exact distance: 0.11575949084515705
  RTDL distance:  0.11575949084515705
  route_abs_diff: 0.0
  frontier rows: 58518
  total candidate distance evaluations: 12741
  exact pair evaluations: 8698432
  route wall: 4.970943000167608 s

source_limit=64:
  exact distance: 0.12396673111072988
  RTDL distance:  0.12396673111072988
  route_abs_diff: 0.0
  frontier rows: 306165
  total candidate distance evaluations: 53979
  exact pair evaluations: 34793728
  route wall: 5.090343900024891 s

source_limit=128:
  exact distance: 0.11388050989910435
  RTDL distance:  0.11388050989910435
  route_abs_diff: 0.0
  frontier rows: 526006
  total candidate distance evaluations: 100354
  exact pair evaluations: 69587456
  route wall: 8.563488100189716 s
```

Summary:

```text
max_frontier_row_count: 526006
median_route_wall_sec: 5.090343900024891
max_route_wall_sec: 8.563488100189716
median_exact_subset_reference_sec: 1.3439098000526428
max_exact_subset_reference_sec: 2.379139699973166
```

## Capacity Planning

The artifact records:

```text
max_observed_frontier_rows: 526006
source_limit_for_max_rows: 128
max_observed_rows_per_source: 4109.421875
suggested_next_explicit_row_capacity: 789009
```

The suggested capacity is:

```text
ceil(max_observed_frontier_rows * 1.5)
```

This is only a planning value for the next bounded POD/OptiX gate. It does not
prove native/POD fail-closed capacity behavior.

## Interpretation

Goal5181 proves that the scalable RTDL route remains correct for growing
bounded source subsets against the full public target. It also shows the local
NumPy route is dominated by frontier row production at the larger subset:

```text
source_limit=128 frontier_rows phase: 7.190489700064063 s
source_limit=128 nearest_continuation phase: 0.17732909973710775 s
```

This supports moving the next feasibility gate to POD/OptiX with explicit
fail-closed row capacity rather than continuing to optimize local NumPy
frontier row production.

## What This Proves

Goal5181 proves:

```text
full public target loading works for bounded scaling cases;
16/64/128 deterministic source subsets all match exact subset oracles;
frontier row counts are now available for POD/OptiX capacity planning;
the route still avoids full pairwise row materialization.
```

## What This Does Not Prove

Goal5181 does not prove:

```text
all-source full public Dragon-HappyBuddha route completion;
native/POD fail-closed row-capacity validation;
author-vs-RTDL performance;
Figure 5 reproduction;
exact paper dataset reproduction;
full X-HD paper reproduction.
```

## Validation

Commands:

```text
py -m unittest tests.goal5181_xhd_full_public_subset_scaling_gate_test
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_full_public_subset_scaling_gate_goal5181_graphics_dragon_happy_buddha_2026-07-08.json > $null
```

Result:

```text
Ran 2 tests in 7.631s
OK
```

Known local noise:

```text
Could not find platform independent libraries <prefix>
```

The command exits successfully despite this Windows Python noise.

## Next Recommended Goal

Goal5182 should run the same bounded subset scaling gate on POD/OptiX:

```text
use backend=optix;
start with source_limit=128;
set explicit fail-closed row capacity around 789009 or another reviewed value;
record native frontier phase counters;
do not report performance ratio;
do not claim all-source route completion unless the all-source route actually runs.
```
