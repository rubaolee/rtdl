# Goal1464 v1.5.3 Typed Host Input Measurement

## Verdict

Added wrapper-level copy-count measurement for the v1.5.3 typed host input
buffer path. This records that the baseline path materializes ctypes input each
call, while the typed-host path prepares one input buffer and reuses it across
calls.

## Scope

- Baseline path: Python wrapper materializes ctypes input rows each call.
- Typed path: one typed contiguous host input buffer reused across calls.
- Output path: caller-owned prepared host output buffer.
- Measurement: input materialization count delta plus diagnostic timing.

## Boundary

The timing fields are diagnostic only. This is not a public speedup claim, not
true zero-copy, not whole-app evidence, not stable primitive promotion, and not
partner tensor handoff evidence, and not a release action.

## Validation

Run:

```bash
PYTHONPATH=src:. python -m unittest tests.goal1464_v1_5_3_typed_host_input_measurement_test
```
