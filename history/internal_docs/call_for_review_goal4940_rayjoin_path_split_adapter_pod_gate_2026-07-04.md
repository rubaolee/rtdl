# Call For Review: Goal4940 RayJoin Path-Split Adapter POD Gate

Please review Goal4940.

## Files

- Completion report: `history/internal_docs/goal4940_rayjoin_path_split_adapter_pod_gate_2026-07-04.md`
- POD artifacts:
  - `history/internal_docs/goal4940_pod_artifacts/summary.json`
  - `history/internal_docs/goal4940_pod_artifacts/section57_overlay_plain.json`
  - `history/internal_docs/goal4940_pod_artifacts/section57_overlay_path_split.json`
- Generic API from prior goal: `src/rtdsl/output_assembly.py`
- Goal4939 tests: `tests/goal4939_grouped_path_split_records_test.py`

## Requested Verdict

Choose one:

- `approve_goal4940_byte_equal_but_not_faster_stop`
- `redo_goal4940_due_to_missing_evidence`
- `reject_goal4940_interpretation`

## Review Questions

1. Does the evidence prove the generic path-split adapter preserved byte-for-byte correctness on the RayJoin public sample?
2. Does the evidence prove it missed the same-run writer performance gate?
3. Is the interpretation correct that the host-columnar Python path-split/materializer is semantically right but too slow?
4. Is it correct to revert the experimental app wiring and retain only the generic Goal4939 API plus reports/artifacts?
5. Is it correct that no RayJoin speedup or public performance claim is authorized?
6. Is the next implementation, if any, a compiled/native generic path-split materializer rather than more app-adapter micro-patching?

## Boundaries

Do not authorize:

- keeping the slower RayJoin app route;
- RayJoin-specific output semantics in RTDL core;
- public speedup claims;
- another micro-patch around the same host-columnar app adapter.
