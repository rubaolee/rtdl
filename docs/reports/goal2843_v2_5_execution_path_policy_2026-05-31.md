# Goal2843: v2.5 Execution-Path Policy

Date: 2026-05-31

Status: implemented, externally reviewed, consensus accepted with boundary

## Purpose

Goal2841 proved an important cost boundary for RTNN-shaped fixed-radius aggregate replay:

- direct native CUDA graph replay is still the faster app-facing path when no partner continuation is needed;
- same-stream graph replay plus a CuPy consumer is correct and traceable, but measured `1.923x` slower on the 65K fixture;
- therefore the runtime must explain the path choice instead of hiding it behind a smart dispatcher.

Goal2843 turns that lesson into machine-readable policy metadata.

## Implementation

New module:

- `src/rtdsl/v2_5_execution_path_policy.py`

New public-but-not-star-exported helpers:

- `plan_v2_5_fixed_radius_aggregate_execution_path(...)`
- `validate_v2_5_execution_path_policy()`

The policy exposes two explicit modes:

| Situation | Recommended result mode | Why |
| --- | --- | --- |
| No partner continuation is needed | `ranked-summary-aggregate-prepared-query-batch-graph-float32` | Direct native graph replay is the fastest measured aggregate path. |
| A partner continuation is required | `ranked-summary-aggregate-prepared-query-batch-graph-same-stream-cupy-float32` | Same-stream ordering and entrypoint metadata matter more than raw aggregate replay speed. |

The app-facing RTNN runner now attaches `execution_path_plan` for both graph modes and records `execution_path_policy_version` in the contract.

## Design Rule

Same-stream is not a magic faster mode. The rule is: same-stream only when partner continuation is required. It is the correct path when the app needs a partner continuation over device-resident primitive payload columns. If the app only needs the final aggregate, direct native graph replay remains preferred.

Goal2843 keeps this rule explicit:

- `hidden_auto_dispatch_allowed: False`
- `explicit_result_mode_required: True`
- `auto_select_same_stream_for_speed_allowed: False`

## Boundary

Goal2843 does not authorize:

- public speedup claims;
- RT-core speedup claims;
- whole-app speedup claims;
- true zero-copy claims;
- v2.5 release readiness.

It only authorizes explain metadata for choosing between two already-existing app-facing graph paths.

Independent review:

- `docs/reviews/goal2844_gemini_review_goal2843_execution_path_policy_2026-05-31.md`

Consensus:

- `docs/reports/goal2844_goal2843_execution_path_policy_consensus_2026-05-31.md`

## Validation

Local validation:

```text
PYTHONPATH=src:. python -m unittest \
  tests.goal2843_v2_5_execution_path_policy_test \
  tests.goal2841_rtnn_same_stream_scale_probe_test \
  tests.goal2839_rtnn_same_stream_runner_mode_test \
  tests.goal2837_fixed_radius_graph_entrypoint_metadata_test \
  tests.goal2835_primitive_payload_entrypoint_metadata_test \
  tests.goal2825_rtnn_cuda_graph_replay_prepared_batch_test \
  tests.goal2821_rtnn_heterogeneous_batched_aggregate_requests_test \
  tests.goal2348_rtnn_v2_2_external_runner_test
```

Pod validation after commit/push from exact `origin/main`:

```text
commit: 8fc3a50cefd9c35400a30c0742e6172ed09eb2de
Ran 52 tests in 0.152s
OK
```

## Codex Verdict

`accept-with-boundary`

Goal2843 is a routing/explain hardening step, not a new performance claim. It prevents users from accidentally reading same-stream as the default fast path while preserving it as the right partner-continuation path.
