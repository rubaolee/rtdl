# Call For Review: Goal5179 X-HD Priority Input Scale Profile

Date: 2026-07-08

## Requested Verdict

```text
approve_goal5179_priority_input_scale_profile__no_route_run
```

## Files Under Review

```text
history/internal_docs/goal5179_priority_input_scale_profile_result_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/scripts/profile_xhd_priority_input_scale.py
Paper-reproduction-apps/x-hd-paper/results/xhd_priority_input_scale_profile_goal5179_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_priority_input_bridge_goal5178_graphics_dragon_happy_buddha_2026-07-08.json
tests/goal5179_xhd_priority_input_scale_profile_test.py
Paper-reproduction-apps/x-hd-paper/data/manifest.json
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

## Context

Goal5178 bridged the paper-branch `graphics_dragon_happy_buddha` priority subset
to local public Stanford full-resolution PLY files:

```text
dragon.ply:        437645 vertices
happy_buddha.ply:  543652 vertices
```

This is a strong Level B same-source candidate because public Stanford file
vertex counts match the author paper-branch logs, and source/extracted file
SHA256 values are recorded. It is not Level C exact paper dataset identity,
because author input bytes/hashes or deterministic conversion provenance are
still absent.

Goal5179 profiles this full public candidate before attempting any route run.

## Evidence Summary

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_priority_input_scale_profile_goal5179_graphics_dragon_happy_buddha_2026-07-08.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.priority_input_scale_profile.v1
```

Status:

```text
graphics_dragon_happy_buddha_full_public_candidate_profiled__no_route_run
```

Key scale result:

```text
point pairs: 237926579540
float32 distance matrix bytes: 951706318160
float64 distance matrix bytes: 1903412636320
16-byte candidate rows: 3806825272640 bytes
24-byte candidate rows: 5710237908960 bytes
32-byte candidate rows: 7613650545280 bytes
pairwise_exact_route_allowed: false
```

The profiler streams ASCII PLY vertices. It does not materialize an `N x M`
pair matrix or candidate row table.

Grid occupancy evidence is recorded for `8^3`, `16^3`, and `32^3` grids for
both public Stanford files. The artifact also records route feasibility flags:

```text
do_not_run_naive_pairwise_exact: true
requires_scalable_route: true
```

Recommended next gate:

```text
bounded full-public-candidate feasibility gate with fail-closed row capacities
and phase counters, not a performance ratio
```

## Authorized Claims

The reviewer is asked to approve only these claims:

```text
Goal5179 profiles the full public Stanford Dragon/HappyBuddha Level B candidate.
The old materialized pairwise exact route is infeasible at this scale.
The next step must use a scalable seeded/frontier/inline-nearest route.
Grid occupancy and pairwise-size evidence are sufficient to choose a bounded,
fail-closed feasibility gate.
```

## Forbidden Claims

Goal5179 does not authorize:

```text
route execution on the full public candidate;
author-vs-RTDL performance ratio;
Figure 5 reproduction;
exact paper dataset reproduction;
full X-HD paper reproduction;
author parity or speedup;
promotion from Level B same-source candidate to Level C exact paper dataset.
```

## Validation Reported

```text
py -m unittest tests.goal5179_xhd_priority_input_scale_profile_test tests.goal5178_xhd_priority_input_bridge_test

Ran 2 tests in 0.117s
OK
```

The result report also records JSON validation for the Goal5179 artifact and
manifest. On this Windows setup, `py` may print:

```text
Could not find platform independent libraries <prefix>
```

The command exits successfully despite that environment noise.

## Review Questions

1. Does the script stream PLY vertices and avoid materializing an `N x M`
   pairwise matrix or candidate row table?
2. Does the pairwise estimate correctly show that the old materialized exact
   route is infeasible for 437645 x 543652 points?
3. Are grid occupancy profiles for `8^3`, `16^3`, and `32^3` sufficient for
   planning a bounded, fail-closed scalable route gate?
4. Does the report correctly keep this at Level B same-source candidate status
   rather than Level C exact paper dataset reproduction?
5. Are the claim boundaries clear enough to prevent route/performance/figure
   claims from being inferred?
6. Is Goal5180's proposed next gate correct: bounded full-public-candidate
   feasibility with fail-closed row capacities and phase counters, not a
   performance ratio?
7. Are the tests sufficient for a profiling/planning goal?
8. Should Goal5179 be closed as implemented / review-pending until external
   review approves it, with no upgrade to full paper reproduction status?

## Expected Answer Shape

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to Q1-Q8:
```
