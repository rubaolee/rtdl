# Call For Review: Phoenix V3 M72 Barnes-Hut Blocker-Bound Runtime Trunk

Date: 2026-06-24

Requested verdict labels:

- `accept_m72_local_wiring_authorize_one_focused_barnes_hut_pod_no_release`
- `accept_with_required_amendments_before_focused_pod`
- `revise_before_pod_authorization`
- `block_m72_wrong_route`

## Review Scope

Please critically review the Phoenix V3 M72 local wiring that targets the
Barnes-Hut / aggregate-tree Set-A blocker.

Primary evidence:

- `docs/reports/phoenix_v3_m72_barnes_hut_blocker_bound_runtime_trunk_2026-06-24.md`
- `src/rtdsl/prepared_execution.py`
- `examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py`
- `tests/v3_phoenix_prepared_execution_session_runner_test.py`
- `tests/v3_phoenix_barnes_hut_prepared_execution_runner_wiring_test.py`
- `docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md`
- `docs/reviews/phoenix_v3_revised_m72_plan_target_the_blocker_2026-06-24.md`

Local verification command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test tests.v3_phoenix_barnes_hut_prepared_execution_runner_wiring_test
```

Observed result:

```text
Ran 47 tests in 0.160s
OK
```

## Context

The revised M72 plan says Phoenix V3 must stop accumulating non-blocker runner
evidence and instead aim the runtime trunk at a scorecard-controlling row.

The selected blocker is:

| Field | Value |
| --- | --- |
| Scorecard row id | `set_a_barnes_hut_app_geomean_0_844x` |
| Set | `A` |
| App | `barnes_hut` |
| Metric | `set_a_app_geomean_v3_vs_v2_14` |
| Current value | `0.844x` |
| Route kind | `trunk_fix_candidate` |

The implemented local path binds the Barnes-Hut front-door prepared execution
route to the generic aggregate-tree fused weighted-vector-sum prepared-session
helper. The helper remains app-agnostic and records scorecard binding metadata
only when the caller supplies it.

## Questions For Review

1. Does the generic helper remain app-agnostic, or did M72 accidentally turn it
   into another app-specific Barnes-Hut route?

2. Does the Barnes-Hut front-door adapter bind the exact Set-A blocker row
   clearly enough for the Phoenix V3 scorecard discipline?

3. Is `win_source="partner_continuation"` the correct honest classification for
   this route, given that M72 reuses the M43 prepared-runner discipline but not
   the M43 CuPy grouped-reduction kernel?

4. Are the metadata fields sufficient for the focused POD result to state
   whether Barnes-Hut moved because of the runtime trunk, rather than because of
   unrelated cache hygiene or app-specific route polish?

5. Is the local test coverage strong enough to authorize exactly one focused
   Barnes-Hut POD benchmark?

6. If you do authorize a focused POD run, what exact constraints must be
   enforced in the run packet?

7. If you do not authorize the focused POD run, what must be fixed first?

## Proposed Focused POD Constraints If Authorized

If the review verdict authorizes POD work, authorization should be limited to
one focused Barnes-Hut blocker run:

- same RT hardware;
- same scale and contract as the controlling scorecard row where possible;
- no all-app run;
- no public speedup wording;
- compare against the existing incumbent route used to derive the `0.844x`
  scorecard blocker;
- record `runtime_executed`, scorecard binding, phase accounting, and
  `win_source`;
- report whether the blocker moved, stayed red, or regressed.

## Non-Authorization

This review request does not authorize:

- V3 release;
- all-app benchmarking;
- public speedup wording;
- broad V3-over-V2 claims;
- V4 work;
- embedding;
- external zero-copy claims;
- treating local unit tests as performance evidence.

The only possible positive authorization requested here is:

`one_focused_barnes_hut_pod_run_after_review`
