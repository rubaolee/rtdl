# Goal1465 v1.5.3 Reduced-Copy External Review Request

## Request

Review the v1.5.3 reduced-copy contract, typed host input buffer, native typed
host envelope, and wrapper-level copy-count measurement. Decide whether the
evidence is accurately bounded as a reduced-copy candidate path without
claiming true zero-copy, public speedup, whole-app speedup, stable primitive
promotion, or release readiness.

## Files To Review

- Contract and implementation:
  `src/rtdsl/v1_5_3_reduced_copy.py`
  `src/rtdsl/__init__.py`
- Tests:
  `tests/goal1461_v1_5_3_reduced_copy_contract_test.py`
  `tests/goal1462_v1_5_3_typed_host_input_buffer_test.py`
  `tests/goal1463_v1_5_3_typed_host_native_envelope_test.py`
  `tests/goal1464_v1_5_3_typed_host_input_measurement_test.py`
- Reports:
  `docs/reports/goal1461_v1_5_3_reduced_copy_contract_2026-05-07.md`
  `docs/reports/goal1462_v1_5_3_typed_host_input_buffer_2026-05-07.md`
  `docs/reports/goal1463_v1_5_3_typed_host_native_envelope_2026-05-07.md`
  `docs/reports/goal1464_v1_5_3_typed_host_input_measurement_2026-05-07.md`

## Current Evidence

- Typed contiguous host input-buffer path is present.
- Native envelope can pass explicit typed input and caller-owned host output
  buffers to a native collect-k symbol.
- Wrapper-level copy-count measurement records:
  baseline input materialization count = iterations;
  typed input materialization count = 1;
  timing fields are diagnostic only.
- Contract still lists backend parity where claimed and external AI review as
  pending before public claims.

## Boundary To Check

The package must preserve:

- No true zero-copy wording.
- No public speedup wording.
- No whole-app claims.
- No stable primitive promotion.
- No partner tensor handoff claim.
- No release action.

## Review Question

Answer with `ACCEPT`, `ACCEPT_WITH_NOTES`, or `REJECT`.

If rejecting, identify the exact blocker. If accepting, confirm whether this is
safe as internal reduced-copy candidate evidence only.
