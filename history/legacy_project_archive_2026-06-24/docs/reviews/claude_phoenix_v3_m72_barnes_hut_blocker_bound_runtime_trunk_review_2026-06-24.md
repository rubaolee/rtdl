# External Review: Phoenix V3 M72 Barnes-Hut Blocker-Bound Runtime Trunk

Date: 2026-06-24

Reviewer: Claude Code CLI

Scope: M72 local wiring only; specifically the generic aggregate-tree
fused-vector-sum helper, the Barnes-Hut front-door adapter, and the two test
suites.

Verdict: `accept_with_required_amendments_before_focused_pod`

## Summary Judgment

The generic helper is well-designed and app-agnostic. The scorecard binding is
precise and propagates correctly. The `win_source` classification is honest.
The generic helper behavioral tests are solid. The front-door adapter
text-search tests confirm the binding exists in source but do not verify the
dispatch path at the behavioral level.

The route is plausible and correctly targeted at the #1 Set-A blocker, but two
amendments are required before a focused Barnes-Hut POD run can be authorized.

## Answers

### Q1: Does the generic helper remain app-agnostic?

Yes, with one labeling caution.

`run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session` accepts
`scorecard_binding` and `win_source` as caller-supplied parameters. The helper
body contains no Barnes-Hut domain concept. The wiring test confirms this by
asserting that `barnes` is absent from the helper source slice.

Caution: `win_source` defaults to `partner_continuation`. Validation rejects
unknown values, but a wrong valid value would still pass. This is a discipline
risk for future callers, not a current blocker.

### Q2: Does the Barnes-Hut front-door adapter bind the exact Set-A blocker row?

Yes.

The adapter supplies all required binding fields plus `target` and `role`. The
`id` matches `set_a_barnes_hut_app_geomean_0_844x`, `current_value` is `0.844`,
and `route_kind` is `trunk_fix_candidate`.

The `phoenix_v3_m72` payload re-surfaces each binding field and explicitly sets:

- `pod_authorized: false`
- `release_authorized: false`
- `all_app_authorized: false`

### Q3: Is `win_source="partner_continuation"` honest?

Yes, as stated.

The `m43_reuse_scope` field records that M72 reuses prepared-runner discipline
but not the M43 CuPy grouped-reduction kernel. The path attributes possible
movement to device-resident Numba CUDA continuation through the prepared runner,
not to a kernel-level rewrite.

The classification still requires POD evidence.

### Q4: Are metadata fields sufficient to attribute movement to the runtime trunk?

Partially. One gap must be resolved in the POD packet.

The metadata supports attribution through:

- `runtime_executed`
- `runtime_trunk_executes_end_to_end`
- host materialization flags
- `win_source`
- `m43_reuse_scope`
- phase accounting
- CUDA event timing when available

Gap: the runner metadata does not identify the exact incumbent baseline route
that produced the `0.844x` scorecard value. The POD packet must name the
incumbent baseline route and reproduce the comparison in the same session.

### Q5: Is local coverage strong enough to authorize one focused Barnes-Hut POD?

Not yet.

The generic helper is covered behaviorally. The current front-door adapter tests
are static source checks and syntax checks. They do not prove that the benchmark
app dispatches mode `prepared_execution_fused_vector_sum_numba_cuda` to
`_prepared_execution_fused_vector_sum_numba_cuda_payload`.

That dispatch gap must be closed before focused POD authorization.

### Q6: If authorized, what constraints must the run packet enforce?

The run packet must:

- name the incumbent baseline explicitly;
- run incumbent and M72 in the same POD session;
- use the same body count, theta, bucket size, max depth, warmup, and repeat
  counts as the controlling scorecard row where possible;
- record `kernel_event_median_sec` separately from `call_wall_median_sec`;
- record `runtime_executed`, scorecard binding, phase accounting, and
  `win_source`;
- report the outcome categorically as moved, partial improvement, unchanged, or
  regressed.

### Q7: If not authorized, what must be fixed first?

Two amendments are required.

## Required Amendments

### Amendment 1: Code

Add a CPU-side behavioral dispatch test proving that benchmark mode
`prepared_execution_fused_vector_sum_numba_cuda` invokes
`_prepared_execution_fused_vector_sum_numba_cuda_payload`.

The test can monkeypatch the payload function and does not need GPU execution.

### Amendment 2: Documentation

Before POD execution, add an incumbent route declaration naming:

- the benchmark app mode string for the baseline;
- the git commit or report reference where the `0.844x` row was measured;
- body count;
- theta;
- bucket size;
- max depth;
- warmup and repeat parameters.

Without this, post-run attribution is ambiguous.

## Non-Authorization

This review does not authorize:

- V3 release;
- all-app benchmarking;
- public speedup wording;
- broad V3-over-V2 claims;
- V4 work;
- embedding;
- external zero-copy claims;
- treating local unit tests as performance evidence;
- treating `release_path_candidate: true` as release or POD authorization.

The only possible positive authorization after the amendments is one focused
Barnes-Hut blocker POD run under the constraints above.
