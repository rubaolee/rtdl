# Call For Review: RayJoin Performance Gap Plan

Date: 2026-07-04

Review target:

- `history/internal_docs/rayjoin_performance_gap_problem_efforts_challenges_plan_2026-07-04.md`
- `history/internal_docs/goal4952_post_4951_performance_decision_report_2026-07-04.md`
- `history/internal_docs/goal4951_compiled_path_split_rayjoin_gate_2026-07-04.md`
- `history/internal_docs/goal4950_layer1_2_closure_and_next_step_decision_2026-07-04.md`

Requested verdict:

`approve_rayjoin_performance_gap_plan_authorize_goal4953`

or, if blocked:

`block_rayjoin_performance_gap_plan_until_amended`

## Context

The owner asked for a detailed summary of:

1. the performance problem we need to solve;
2. the effort already spent;
3. the measured effects of those efforts;
4. the remaining challenges;
5. the parsed next work plan.

The packet argues that:

- RTDL has correct bounded RayJoin reproduction;
- RTDL is still much slower than the author's C++/CUDA/OptiX implementation;
- recent Layer 1/2 and CPU/Numba Layer 3 experiments were useful but did not
  produce a performance win;
- the only next authorized work should be Goal4953, a fine-grained measurement
  of the current fastest plain writer.

## Review Questions

1. Does the report correctly identify the current performance problem without
   hiding the fact that RTDL remains much slower than the author implementation?

2. Does it accurately summarize the outcomes of Goals 4947-4952?

3. Does it correctly explain why the recent efforts did not yield a speedup,
   especially:
   - Layer 1/2 proved connection but not RayJoin performance;
   - current Numba helpers were slower;
   - CPU/Numba compiled path-split was correct but slower;
   - PIP traversal and final file write are not the current bottlenecks?

4. Does the report avoid overclaiming that all Layer 3 or data-flow fusion work
   is impossible?

5. Does it preserve the core red line that RTDL core must not contain RayJoin
   paper text-output semantics?

6. Is the parsed work plan correct:
   - Goal4953 = measurement only;
   - Goal4954+ open only if Goal4953 proves a recoverable generic writer cost;
   - no native/device writer implementation is authorized yet?

7. Are the Goal4953 measurement categories complete enough to decide whether
   native/device writer work is justified?

8. Should the packet be approved with verdict:

   `approve_rayjoin_performance_gap_plan_authorize_goal4953`

## Non-Authorization Boundary

Approval of this packet authorizes only Goal4953 measurement.

It does not authorize:

- native writer implementation;
- device writer implementation;
- another CPU/Numba materializer attempt;
- public API exposure;
- performance claims;
- RayJoin text output format in RTDL core;
- data-flow fusion/compiler implementation.
