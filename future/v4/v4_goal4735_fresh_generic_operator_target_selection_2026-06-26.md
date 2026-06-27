# V4 Goal4735 Fresh Generic Operator Target Selection

Date: 2026-06-26

Status: `target_selected_pending_external_review_debt`

Decision:
`select_barnes_hut_complete_aggregate_weighted_workflow_for_goal4736`

## Purpose

Goal4731 allowed a fresh generic-operator target only after the known measured
blockers were handled:

- Goal4732: RayDB route binding repaired to V2.14 no-regression, not a speed win.
- Goal4733: triangle V4/V3 regression cleared by high-repeat focused rerun.
- Goal4734: RTDBSCAN closed as no-go based on existing Goal4670/4671 evidence.

Goal4735 now chooses one remaining no-route/deferred target for a falsifiable
generic-runtime attempt.

## Candidates

### Spatial RayJoin

Current status:

`closed_no_current_v4_app_route_blocker`

Reason:

- Existing shape-pair subprobe was correct but failed speed-credit bars.
- It is not a complete Spatial RayJoin app route.
- Reopening requires a complete relation-topology V4 route, not a hidden V2/V3
  fallback and not a Spatial-RayJoin-specific native kernel.

Decision:

Do not choose Spatial RayJoin for Goal4735. It remains a valid future target,
but it lacks a complete current app route and would require larger route design
before a fair POD run.

### Barnes-Hut

Current status:

`closed_deferred_subprobe_not_complete_app_route`

Reason to choose:

- Existing aggregate-frontier device-column evidence is real and measured.
- The app already has a frontdoor for a complete aggregate-frontier plus
  weighted-vector workflow:
  `prepared_aggregate_frontier_weighted_vector_optix`.
- The acceptable V4 route is a generic aggregate-frontier/weighted-vector
  workflow with explicit partner continuation; it must not use a
  Barnes-Hut-identity native kernel.
- The next experiment is cheap enough to run now and falsifiable.

Decision:

Select Barnes-Hut for Goal4736.

## Goal4736 Frozen Protocol

Goal4736 will run a focused same-hardware POD validation of the complete
Barnes-Hut aggregate weighted workflow.

Required route shape:

- V2.14 denominator:
  `v2_14_optix_host_frontier_numba_cpu_continuation`
- V3.0.2 control:
  `v3_0_2_device_columns_explicit_partner_continuation`
- V4 current:
  `v4_candidate_runner_explicit_partner_continuation`

Required checks:

- correctness parity on the correctness companion row;
- no host frontier materialization in the V4 hot path;
- no partner migration counted as speed;
- no app-identity native Barnes-Hut kernel;
- no RT-core speedup wording unless the route actually uses RT-core traversal
  for the relevant measured phase;
- old V2/V3 denominators remain visible.

Numerical classification:

| gate | threshold |
|---|---:|
| V4/V2.14 full hot | `>= 1.20x` |
| V4/V2.14 full wall | `>= 1.10x` |
| V4/V3.0.2 full hot | `>= 0.98x` no-regression |
| correctness companion | pass |

If Goal4736 passes, Barnes-Hut may move from deferred/subprobe to a complete
app-level V4 candidate row, with careful wording:

`generic aggregate-frontier device columns plus explicit partner weighted-vector continuation`

It must not be worded as:

- pure RT-core force law speedup;
- native Barnes-Hut kernel;
- app-specific engine logic;
- broad V4-over-all-apps proof.

If Goal4736 fails, Barnes-Hut remains deferred/subprobe and V4 still lacks
enough app-level high-performance evidence for a formal tag.

## Claim Boundary

Goal4735 only selects the target and freezes the next protocol. It does not
authorize:

- final V4 tag;
- public speedup claim;
- Barnes-Hut speedup claim;
- all-benchmark speedup claim;
- app-specific native kernel;
- true-zero-copy wording.

## Goal-Level Decision Audit

1. Was I being foolish?
   No. Selecting Barnes-Hut is based on existing route readiness and a
   falsifiable generic workflow; selecting Spatial RayJoin now would require
   inventing a larger app route first.

2. If yes, what action made the decision foolish?
   The foolish action would be choosing a no-route app just to look ambitious,
   or calling the aggregate-frontier subprobe a complete app result without the
   weighted-vector workflow.

3. Was there another path?
   Yes. Reopen Spatial RayJoin first. That is higher-risk and lacks a complete
   current route, so it should follow only after Barnes-Hut is tested or rejected.

4. Can I now try a different path that actually solves the problem?
   Yes. Goal4736 runs the complete Barnes-Hut workflow under frozen gates.

## Non-Authorization

Goal4735 authorizes no final V4 tag, no public speed claim, no all-benchmark
speedup claim, no app-specific native kernel, no arbitrary callback support, and
no true-zero-copy wording.
