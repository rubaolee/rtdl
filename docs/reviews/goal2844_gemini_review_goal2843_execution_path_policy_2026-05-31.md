# Goal2844 Gemini Review: Goal2843 v2.5 Execution-Path Policy (2026-05-31)

## Files Inspected:
- `src/rtdsl/v2_5_execution_path_policy.py`
- `src/rtdsl/__init__.py`
- `scripts/goal2348_rtnn_v2_2_external_runner.py`
- `tests/goal2843_v2_5_execution_path_policy_test.py`
- `docs/reports/goal2843_v2_5_execution_path_policy_2026-05-31.md`
- `docs/reports/goal2841_rtnn_same_stream_scale_probe_2026-05-31.md`
- `docs/reports/goal2841_rtnn_same_stream_scale_pod/goal2841_summary.json`

## Questions & Answers:

### 1. Does Goal2843 correctly encode the Goal2841 lesson that direct native graph replay is preferred when no partner continuation is needed?
Yes. The `plan_v2_5_fixed_radius_aggregate_execution_path` function explicitly recommends `V2_5_FIXED_RADIUS_AGGREGATE_DIRECT_GRAPH_MODE` when `requires_partner_continuation` is `False`. The policy's internal reasons and test assertions (`tests/goal2843_v2_5_execution_path_policy_test.py`) confirm this preference, citing Goal2841's measurement that direct native graph replay is the fastest measured path when a partner continuation is not required.

### 2. Does it correctly recommend same-stream only when partner continuation/device-resident entrypoint metadata is required?
Yes. The policy recommends `V2_5_FIXED_RADIUS_AGGREGATE_SAME_STREAM_CUPY_MODE` when `requires_partner_continuation` is `True`, explicitly stating that "A partner continuation is required, so same-stream ordering and entrypoint metadata matter." This aligns with Goal2841's finding that the same-stream path is for traceability and partner integration, despite being slower.

### 3. Does the runner attach `execution_path_plan` without changing existing execution semantics?
Yes. The `scripts/goal2348_rtnn_v2_2_external_runner.py` script, specifically in the `run_rtdl_batched_3d_neighbors` function, calls `rt.plan_v2_5_fixed_radius_aggregate_execution_path` and includes the resulting `execution_path_plan` in its output. The policy itself, as confirmed by its tests, ensures that `hidden_auto_dispatch_allowed` is `False` and `explicit_result_mode_required` is `True`, indicating no hidden changes to execution semantics. The policy only provides guidance, not automated dispatch.

### 4. Does the policy avoid hidden smart dispatch and keep explicit result-mode choice?
Yes. The `src/rtdsl/v2_5_execution_path_policy.py` explicitly sets `hidden_auto_dispatch_allowed: False` and `auto_select_same_stream_for_speed_allowed: False`. The `explicit_result_mode_required: True` also reinforces that the choice remains explicit. The test `test_policy_validates_and_keeps_claims_blocked` and `test_direct_graph_is_recommended_without_partner_continuation` in `tests/goal2843_v2_5_execution_path_policy_test.py` also verify this behavior.

### 5. Does the report avoid public speedup, RT-core speedup, whole-app speedup, true zero-copy, arbitrary partner, or v2.5 release-readiness claims?
Yes. The `src/rtdsl/v2_5_execution_path_policy.py` defines `V2_5_EXECUTION_PATH_POLICY_CLAIM_BOUNDARY` which explicitly lists all these claims as unauthorized. The `validate_v2_5_execution_path_policy` function and its corresponding test `test_policy_validates_and_keeps_claims_blocked` assert that these flags remain `False`. The `docs/reports/goal2843_v2_5_execution_path_policy_2026-05-31.md` report also reiterates this boundary.

## Verdict:
`accept-with-boundary`

Goal2843 successfully implements a policy that clarifies execution path choices based on Goal2841's findings, without introducing hidden dispatches or making unauthorized performance claims. The policy explicitly guides users to prefer direct native graph replay when no partner continuation is needed and to use same-stream only when partner continuation is required, acknowledging the performance trade-off. The associated tests, runner integration, and reporting align with these intentions and boundaries.
