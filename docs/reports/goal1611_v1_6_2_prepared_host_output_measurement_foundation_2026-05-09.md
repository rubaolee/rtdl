# Goal1611 v1.6.2 Prepared Host-Output Measurement Foundation

Date: 2026-05-09

## Verdict

Goal1611 starts the `v1.6.2` prepared host-output measurement track.

The deliverable is a local preflight runner that reuses the Goal1610
phase/copy schema and measures the wrapper-level difference between:

- compatibility rows that materialize Python input rows for every call;
- typed contiguous host input plus a prepared caller-owned host output buffer.

This is a local harness and schema preflight, not real Embree/OptiX performance
evidence and not a performance claim.

## Files

- script: `scripts/goal1611_v1_6_2_prepared_host_output_measurement.py`
- test: `tests/goal1611_v1_6_2_prepared_host_output_measurement_test.py`
- default smoke artifact:
  `docs/reports/goal1611_v1_6_2_prepared_host_output_measurement_preflight_2026-05-09.json`

## Measurement Shape

The runner records every Goal1610 phase field and every Goal1610 copy-count
field. Fields that are not observable in the local fake-native preflight remain
`null`.

The local preflight case records:

- `baseline_input_materialization_count`
- `prepared_input_materialization_count`
- `input_materialization_count_delta`
- `prepared_host_output_buffer_reused`
- `prepared_buffer_reuse_count`
- diagnostic elapsed totals and medians

The fake native symbol is deliberate. It lets Windows, macOS, and Linux check
the measurement contract without requiring Embree, OptiX, CUDA, or a paid pod.
Real backend evidence must be collected separately.

## Claim Boundary

Goal1611 does not authorize:

- public speedup wording;
- whole-app speedup wording;
- broad RTX/GPU wording;
- true zero-copy wording;
- stable `COLLECT_K_BOUNDED` promotion;
- partner tensor handoff claims;
- package-install claims;
- release tags or release action.

## Next Step

Use this runner shape for real Embree and OptiX backend runs once suitable
hardware is available. Those runs must keep the same claim boundary until
separate reviewed evidence authorizes narrower wording.
