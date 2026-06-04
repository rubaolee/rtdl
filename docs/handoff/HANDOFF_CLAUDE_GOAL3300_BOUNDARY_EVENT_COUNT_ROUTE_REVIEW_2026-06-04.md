# Handoff: Goal3300 Boundary-Event Count Route Review

Please perform a read-only external Claude review of the current `main` state for
Goal3300. Write the review to:

`docs/reviews/goal3301_claude_review_goal3300_boundary_event_count_route_2026-06-04.md`

## Context

Current commit under review:

`0da3f427951460634a38f32daffc4873d42e9c73`

Goal3300 wires the new generic boundary-event device-column stream from
Goals3297-3299 into the RayJoin same-slice benchmark as an explicit PIP count
mode:

`boundary_event_point_id_count_device_columns`

This mode runs generic first-boundary-event device columns and a generic grouped
count by `point_id`. It must not be represented as RayJoin PIP positive
membership or paper reproduction. It is a different contract: first
closed-shape boundary event count by point id.

## Files To Inspect

- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py`
- `tests/goal2327_rayjoin_prepared_route_contract_test.py`
- `tests/goal3244_rayjoin_same_slice_repeated_count_runner_test.py`
- `tests/goal3299_boundary_event_grouped_count_continuation_test.py`
- Optional supporting runtime: `src/rtdsl/optix_runtime.py`

## Verification Already Run

On Windows:

`PYTHONPATH=src;. py -3 -m unittest tests.goal3299_boundary_event_grouped_count_continuation_test tests.goal2327_rayjoin_prepared_route_contract_test tests.goal3244_rayjoin_same_slice_repeated_count_runner_test`

Result: `28 tests OK (skipped=1)`.

On the RTX pod after pulling `origin/main`:

`PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_goal3293/build/librtdl_optix.so python -m unittest tests.goal2327_rayjoin_prepared_route_contract_test tests.goal3244_rayjoin_same_slice_repeated_count_runner_test tests.goal3299_boundary_event_grouped_count_continuation_test`

Result: `28 tests OK`.

## Review Questions

1. Does Goal3300 preserve the app-agnostic native-engine boundary?
2. Does the new route correctly disclose that boundary-event grouped count is
   not a PIP positive-membership contract?
3. Does the runner avoid treating the new route as RayJoin paper reproduction
   or `rtdl_beats_rayjoin` evidence?
4. Are the tests strong enough to prevent accidental claim-boundary regression?
5. What should be fixed before we use this route as a v2.8 benchmark data point?

## Required Verdict Format

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Lead with findings by severity. Keep release/speedup/zero-copy claims blocked
unless the evidence genuinely authorizes them.
