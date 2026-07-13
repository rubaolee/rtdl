# Call For Review: Goal5180 Full Public Candidate Feasibility Gate

Date: 2026-07-08

## Requested Verdict

```text
approve_goal5180_full_public_candidate_bounded_subset_feasibility_gate
```

## Files Under Review

```text
history/internal_docs/goal5180_full_public_candidate_feasibility_gate_result_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_feasibility_gate.py
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_feasibility_gate_goal5180_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_priority_input_scale_profile_goal5179_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_priority_input_bridge_goal5178_graphics_dragon_happy_buddha_2026-07-08.json
tests/goal5180_xhd_full_public_feasibility_gate_test.py
Paper-reproduction-apps/x-hd-paper/data/manifest.json
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

## Context

Goal5178 bridged the `graphics_dragon_happy_buddha` priority subset to public
Stanford full-resolution Dragon/HappyBuddha files. Goal5179 showed that the old
pairwise exact route is infeasible:

```text
source points: 437645
target points: 543652
point pairs:   237926579540
16-byte rows:  about 3.8 TB
```

Goal5180 runs the first safe feasibility gate on those full public files. It
loads the full source and full target, selects 16 deterministic source rows,
runs the scalable seeded/frontier/nearest route against the full target, and
compares that route to an exact subset oracle.

## Evidence Summary

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_feasibility_gate_goal5180_graphics_dragon_happy_buddha_2026-07-08.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.full_public_feasibility_gate.v1
```

Status:

```text
full_public_candidate_bounded_subset_route_feasibility_checked
```

Key result:

```text
matched: true
route_abs_diff: 0.0

full source count: 437645
full target count: 543652
source subset size: 16
source subset policy: evenly-spaced
grid shape: 32 x 32 x 32
backend: numpy
```

Exact subset oracle:

```text
distance: 0.11575949084515705
pair evaluations: 8698432
strategy: vectorized per-source exact nearest over full target,
          without pairwise matrix materialization
```

RTDL route:

```text
distance: 0.11575949084515705
frontier_row_count: 58518
grid_cell_count: 6454
initial_cell_mbr_tests: 103264
total_candidate_distance_evaluations: 12741
nearest_executor: numba_parallel
```

Capacity boundary:

```text
this_gate: local_numpy_bounded_subset_no_native_row_capacity
actual_frontier_row_count_recorded: true
next_pod_optix_gate_must_use_fail_closed_row_capacity: true
```

## Authorized Claims

The reviewer is asked to approve only these claims:

```text
Goal5180 loads the full public Level B target and runs a bounded source subset
through the scalable route.

The route matches an exact subset oracle with abs diff 0.0.

The old pairwise materialized exact route remains disallowed.

The next appropriate step is a larger/POD OptiX feasibility gate with explicit
fail-closed row capacity, not a performance-ratio claim.
```

## Forbidden Claims

Goal5180 does not authorize:

```text
all-source full public route completion;
author-vs-RTDL performance ratio;
Figure 5 reproduction;
exact paper dataset reproduction;
full X-HD paper reproduction;
native/POD fail-closed capacity validation;
author performance parity.
```

## Validation Reported

```text
py -m unittest tests.goal5180_xhd_full_public_feasibility_gate_test

Ran 2 tests in 8.796s
OK
```

JSON validation was also run on the Goal5180 artifact. On this Windows setup,
`py` may print:

```text
Could not find platform independent libraries <prefix>
```

The command exits successfully despite that environment noise.

## Review Questions

1. Does Goal5180 correctly build on Goal5179 by avoiding the infeasible full
   pairwise materialized route?
2. Is the bounded source subset route a legitimate next feasibility gate for
   the full public candidate?
3. Does the exact subset oracle avoid materializing an `N x M` matrix while
   still providing a strong correctness check?
4. Does the artifact prove route correctness for the bounded subset against the
   full target (`route_abs_diff=0.0`)?
5. Does the report correctly avoid claiming all-source route completion?
6. Does the capacity boundary correctly state that this local NumPy gate is not
   native/POD fail-closed capacity validation?
7. Are the phase timings framed as diagnostic evidence rather than a
   performance ratio?
8. Is Goal5181's proposed POD/OptiX larger-subset capacity gate the right next
   step?
9. Are the tests sufficient for this bounded feasibility goal?
10. Should Goal5180 be marked implemented / review pending until this external
    review approves it?

## Expected Answer Shape

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to Q1-Q10:
```
