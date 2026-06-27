# Phoenix V3 Third Set-A Family Consensus: Hausdorff Threshold Summary

Date: 2026-06-22
Status: `choose_hausdorff_not_release`

## Decision

Codex and Kepler agree that the third focused Set-A runtime-trunk probe should
be the Hausdorff threshold-summary route.

This is an engineering direction only. It does not authorize V3 release, an
all-app rerun, public speedup wording, broad V3-over-V2 wording, true
zero-copy wording, whole-Hausdorff wording, or V4/external-buffer wording.

## Why Hausdorff

Hausdorff's existing evidence is narrower than Triangle's largest synthetic
speedup, but its mechanism is the cleaner Phoenix V3 trunk target:

- a reusable prepared fixed-radius threshold-summary primitive;
- repeated prepared queries with phase accounting;
- a clear route into `prepared_execution_session_runner`;
- same-contract Embree comparison already established at the large row.

Triangle remains useful internal evidence, but its accepted row is synthetic,
non-graph stream scoped, and still carries the blocked graph-capture boundary.
Using it next would risk another exception-management loop instead of proving
that the productized runtime trunk generalizes.

## Implementation Gate

The next patch must add an app-name-free helper, such as
`run_fixed_radius_threshold_reached_count_2d_prepared_session`, and the
Hausdorff app must expose a runner-backed mode that calls that helper instead
of its app-local prepared loop.

Required metadata:

- explicit backend and partner;
- `productized_execution_path: prepared_execution_session_runner`;
- both directed legs executed through the runner;
- source/query counts and threshold counts;
- oracle decision parity at the app layer;
- runtime-returned residency/materialization evidence;
- claim flags all false.

## Focused Pod Gate

Only after local tests and pre-pod review pass, run focused same-pod evidence:

- 1,048,576 points per side;
- threshold `0.4`;
- repeat/warmup comparable to the existing repeat=5 evidence;
- productized runner, legacy app-front-door, and same-contract Embree routes;
- hot query, cold-plus-query, and runner-wall numbers travel together;
- oracle parity required;
- no regression versus the legacy app-front-door route.

## Non-Authorization

The following remain false:

```text
release_authorized: false
all_app_rerun_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
whole_hausdorff_speedup_claim_authorized: false
exact_distance_or_witness_claim_authorized: false
true_zero_copy_claim_authorized: false
v4_external_buffer_claim_authorized: false
automatic_partner_selection_authorized: false
app_specific_native_optimization_authorized: false
```

## Pod Resource Estimate

Local implementation and gates: 2-4 focused engineering hours.

Focused pod evidence after review: 0.5-2 pod hours, expected cost about
`$0.13-$0.50` at `$1/4h`.

If runtime metadata does not prove the required productized path or residency
boundary, do not spend pod time. Fix the runtime evidence first.

## Goal-Level Decision Audit

Decision: choose Hausdorff as the third focused Set-A productized runtime-trunk
probe.

1. Was I foolish?

   No for this decision. It selects the route with the cleanest reusable
   runtime-trunk shape instead of chasing the largest isolated row number.

2. If yes, what actions made the decision foolish?

   Not applicable. The foolish path would be choosing Triangle only because
   its synthetic row speedup is larger, then spending time defending its
   boundaries.

3. Was there another path?

   Yes. Triangle could be chosen for a high-signal row, or RTDBSCAN could be
   re-opened. Both are worse immediate trunk probes: Triangle is boundary-heavy
   and RTDBSCAN already reached parity, not material incumbent improvement.

4. Can I now try a different path that actually solves the problem?

   Yes. Build the app-name-free threshold-summary runner helper, route
   Hausdorff through it, and only then run focused pod evidence under explicit
   non-release boundaries.
