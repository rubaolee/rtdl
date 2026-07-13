# Call For Review: Goal4950 Layer 1/2 Closure And Next-Step Decision

Date: 2026-07-04

Please review:

- `history/internal_docs/goal4950_layer1_2_closure_and_next_step_decision_2026-07-04.md`
- supporting record: `history/internal_docs/goal4949_rayjoin_hot_path_remeasure_2026-07-04.md`
- supporting record: `history/internal_docs/goal4924_columnar_reprojection_sort_probe_result_2026-07-03.md`

## Context

Layer 1/2 was meant to remove Python/host-boundary cost by exposing generic native device columns through a generic row-buffer and handing them to Numba/CuPy style continuations.

Goals 4942-4948 proved the connector and a non-RayJoin genericity gate.

Goal4949 then tested a real RayJoin Section 5.7 public-sample workload and found that the existing Numba app-layer helper is slower, not faster.

A prior direct reprojection/sort probe (Goal4924) already tested the plausible numeric Layer 2 target; it remained byte-equal but failed its hard performance bars.

## Requested Verdict Label

Use one of:

- `approve_goal4950_close_layer1_2_move_to_layer3`
- `approve_with_required_amendments`
- `fail_redo_goal4950`

## Review Questions

1. Does the report correctly distinguish Layer 1/2 capability success from RayJoin performance success?
2. Does Goal4949 justify rejecting the current Numba overlay helper as a performance path?
3. Does Goal4924 justify not repeating another reprojection/sort micro-optimization goal without a new algorithmic idea?
4. Is the recommendation to move to Layer 3 writer/output assembly the correct next step?
5. Does the report preserve the genericity boundary: compiled generic output assembly may be RTDL infrastructure, but RayJoin text output format must remain app-owned?
6. Does the report avoid broad RTDL / RayJoin speedup claims?
7. Should Goal4950 close with label `completed_layer1_2_capability_success__rayjoin_perf_no_go__move_to_layer3_writer_design`?

## Non-Authorization

This review should not authorize:

- app-specific RayJoin output code inside RTDL core;
- broad performance claims;
- more Layer 2 demo connector work;
- promoting the current Numba writer helper.
