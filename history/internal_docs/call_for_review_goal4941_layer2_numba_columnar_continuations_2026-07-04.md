# Call For Review: Goal4941 Layer 2 Numba Columnar Continuations

Please review Goal4941.

## Files

- Completion report: `history/internal_docs/goal4941_layer2_numba_columnar_continuations_2026-07-04.md`
- POD artifact: `history/internal_docs/goal4941_pod_artifacts/layer2_numba_continuations_smoke.json`
- Implementation:
  - `src/rtdsl/partner_continuation_protocol.py`
  - `src/rtdsl/numba_partner_continuation.py`
  - `src/rtdsl/__init__.py`
- Tests:
  - `tests/goal4941_layer2_numba_columnar_continuations_test.py`

## Requested Verdict

Choose one:

- `approve_goal4941_layer2_generic_numba_continuations`
- `redo_goal4941_due_to_genericity_or_execution_gap`
- `reject_goal4941_as_duplicate_or_wrong_layer`

## Review Questions

1. Did Goal4941 correctly reuse the existing v2.5 Numba partner-continuation
   mechanism rather than creating a parallel partner API?
2. Are the three operations app-neutral, or do they smuggle RayJoin/overlay
   semantics into RTDL core?
3. Does the history audit correctly identify that similar app-layer helpers
   existed before, especially Goal4897/4899, and that Goal4941 promotes only the
   generic numeric shape?
4. Does the POD evidence prove real CUDA execution for the new operations?
5. Is it correct that no RayJoin speedup or public performance claim is
   authorized by this goal?
6. Is the stated next step correct: Layer 1 device-column row-buffer carrier
   before claiming hot-path speedup?

## Boundaries

Do not authorize:

- V3/V4 release claims;
- RayJoin speedup claims;
- treating app-local upload/download use as device-resident hot-path proof;
- adding RayJoin output-chain semantics to RTDL core;
- continuing Layer 3 Python host-columnar writer micro-patches.
