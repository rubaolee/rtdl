# Call For Review: Goal5181 Full Public Subset Scaling Gate

Date: 2026-07-08

## Requested Verdict

```text
approve_goal5181_full_public_subset_scaling_gate
```

## Files Under Review

```text
history/internal_docs/goal5181_full_public_subset_scaling_gate_result_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_subset_scaling_gate_goal5181_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_feasibility_gate_goal5180_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_priority_input_scale_profile_goal5179_graphics_dragon_happy_buddha_2026-07-08.json
tests/goal5181_xhd_full_public_subset_scaling_gate_test.py
Paper-reproduction-apps/x-hd-paper/data/manifest.json
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

## Context

Goal5180 proved that a 16-row deterministic source subset can run through the
scalable route against the full public HappyBuddha target and match an exact
subset oracle. Goal5181 extends that into a subset-scaling matrix:

```text
source limits: 16, 64, 128
target: full public HappyBuddha, 543652 points
source: public Dragon, 437645 points
```

This is still Level B same-source representative evidence. It is not exact
paper dataset reproduction because author input bytes/hashes or deterministic
conversion provenance are absent.

## Evidence Summary

Artifact:

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

Results:

```text
all_matched: true

source_limit=16:
  route_abs_diff: 0.0
  frontier rows: 58518
  route wall: 4.970943000167608 s

source_limit=64:
  route_abs_diff: 0.0
  frontier rows: 306165
  route wall: 5.090343900024891 s

source_limit=128:
  route_abs_diff: 0.0
  frontier rows: 526006
  route wall: 8.563488100189716 s
```

Capacity planning:

```text
max_observed_frontier_rows: 526006
source_limit_for_max_rows: 128
suggested_next_explicit_row_capacity: 789009
```

The capacity is a planning suggestion for a future POD/OptiX gate, not proof of
native fail-closed capacity behavior.

## Authorized Claims

The reviewer is asked to approve only these claims:

```text
Goal5181 runs bounded source-subset scaling against the full public target.
The 16/64/128 source subsets all match exact subset oracles.
The old pairwise materialized exact route remains disallowed.
The artifact provides frontier row counts useful for the next POD/OptiX
capacity gate.
```

## Forbidden Claims

Goal5181 does not authorize:

```text
all-source full public route completion;
native/POD fail-closed row-capacity validation;
author-vs-RTDL performance ratio;
Figure 5 reproduction;
exact paper dataset reproduction;
full X-HD paper reproduction;
author performance parity.
```

## Validation Reported

```text
py -m unittest tests.goal5181_xhd_full_public_subset_scaling_gate_test

Ran 2 tests in 7.631s
OK
```

JSON validation was also run on the Goal5181 artifact.

## Review Questions

1. Does Goal5181 correctly extend Goal5180 from a single subset to a bounded
   scaling matrix?
2. Do all three bounded subsets (`16`, `64`, `128`) match exact subset oracles
   with `route_abs_diff=0.0`?
3. Does the script avoid full pairwise row materialization?
4. Is the exact subset oracle still bounded enough to be a legitimate
   correctness check for this scaling goal?
5. Does the capacity suggestion (`789009`) follow from observed frontier rows
   without overclaiming native/POD capacity validation?
6. Does the report correctly identify local NumPy frontier row production as
   the next reason to move to POD/OptiX rather than a paper-performance result?
7. Are the claim boundaries clear enough to prevent all-source, performance,
   Figure 5, exact dataset, or full paper reproduction claims?
8. Is Goal5182's proposed POD/OptiX bounded capacity gate the right next step?
9. Are the tests sufficient for this matrix/planning goal?
10. Should Goal5181 remain implemented / review pending until this external
    review approves it?

## Expected Answer Shape

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to Q1-Q10:
```
