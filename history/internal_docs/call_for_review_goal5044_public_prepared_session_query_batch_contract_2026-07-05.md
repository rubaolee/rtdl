# Call For Review - Goal5044 Public Prepared Session / Query-Batch Contract

Date: 2026-07-05

Please review:

```text
history/internal_docs/goal5044_public_prepared_session_query_batch_contract_2026-07-05.md
```

Code/test changes:

```text
src/rtdsl/prepared_session_residency.py
src/rtdsl/__init__.py
tests/goal5044_public_prepared_geometry_session_contract_test.py
```

Requested verdict labels:

```text
approve_goal5044_public_prepared_session_query_batch_contract
revise_goal5044_before_goal5045
fail_goal5044_replay_or_app_specific_boundary_violation
```

## Context

Goal5044 is part of v2.14.4.  v2.14.4 is not another RayJoin app optimization pass.  It is the effort to formalize the generic RTDL API capabilities proven during the RayJoin v2.14.3 work.

Goal5043 exposed a public `DeviceColumnBuffer` wrapper.  Goal5044 should expose the matching prepared-base/query-batch lifecycle contract.

## Review Questions

1. Does `PreparedGeometrySession` reuse/wrap the existing prepared-session residency substrate rather than inventing a parallel fifth session surface?
2. Are the four regime labels explicit and preserved?

```text
cold_cli_one_shot
warm_process_fresh
prepared_base_distinct_query_batch
prepared_replay_same_input_diagnostic
```

3. Does the implementation prevent same-input replay from being labeled as query-many?
4. Does `require_distinct=True` fail closed when a query fingerprint repeats?
5. Does `run_metadata(...)` expose phase timing fields and device-residency metadata without claiming execution or performance?
6. Are public claim-boundary flags still false for speedup, true zero-copy, automatic partner selection, and app-specific native logic?
7. Does the new public API avoid adding RayJoin-specific primitive names, output-chain semantics, or native shortcuts?
8. Are the tests sufficient for the contract shape and the replay/query-many guard?
9. Is the documented verification honest about the old Goal3873/3877 report-path failures being historical documentation path noise, not a prepared-session runtime failure?
10. Should Goal5044 close as:

```text
completed_public_prepared_session_query_batch_contract
```

and authorize Goal5045?

## Non-Authorization Boundary

Approval of Goal5044 does not authorize:

- a new performance headline;
- query-many claims without distinct query batches;
- replay-only speedup wording;
- true-zero-copy wording;
- a public `device_group_by`;
- claiming that all old RayJoin-named core/native symbols have been renamed.
