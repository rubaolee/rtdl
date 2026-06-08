# Goal3915 Scale Runner RayJoin Nested Timing Visibility

Date: 2026-06-08

## Purpose

Goal3912 propagates nested RayJoin LSI/overlay subprobe timings into the representative RayJoin payload. Goal3915 confirms that the existing scale runner payload timing collector sees those nested fields, so a future full 10-app A5000 packet can sample them without another runner change.

## Change

The Goal3901 payload-timing unit test now includes a representative RayJoin `cases[*].subprobe_wrapper_phase_timing_sec` object and asserts that `_payload_timing_summary(...)` captures timing scalar paths such as:

- `$.cases[0].subprobe_wrapper_phase_timing_sec.shared_load_case_sec`
- `$.cases[0].subprobe_wrapper_phase_timing_sec.rtdl_optix_call_sec`

No production code changed.

## Validation

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3901_scale_runner_payload_timing_summary_test tests.goal3912_rayjoin_representative_subprobe_timing_propagation_test
```

Expected result: all tests pass.
