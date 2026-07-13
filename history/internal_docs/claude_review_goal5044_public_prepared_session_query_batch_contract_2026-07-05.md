# Claude Review - Goal5044 Public Prepared Session / Query-Batch Contract

Date: 2026-07-05

Verdict:

```text
approve_goal5044_public_prepared_session_query_batch_contract
```

## Summary

Claude reviewed `goal5044_public_prepared_session_query_batch_contract_2026-07-05.md`, the implementation in `prepared_session_residency.py`, the public exports in `__init__.py`, and the Goal5044 tests.  The implementation was approved as a clean public contract for prepared base sessions and explicit query batches.

## Verified Claims

- `PreparedGeometrySession` wraps the existing prepared-session residency substrate.  Its `cache_key` uses `make_prepared_session_cache_key(...)`, and its `session_id` derives from that key.  The older v2.10 helpers remain untouched.
- `PREPARED_GEOMETRY_SESSION_REGIME_LABELS` contains exactly:

```text
cold_cli_one_shot
warm_process_fresh
prepared_base_distinct_query_batch
prepared_replay_same_input_diagnostic
```

- Same-input replay cannot become query-many.  Repeated query fingerprints become `prepared_replay_same_input_diagnostic`, and `run_metadata(...)` authorizes query-many only for `prepared_base_distinct_query_batch`.
- `require_distinct=True` fails closed on repeated fingerprints.
- `run_metadata(...)` records output, phase timings, and device-residency metadata.  It does not execute geometry or create a performance claim.
- Claim-boundary flags remain false for release, public speedup, true zero-copy, automatic partner selection, app-specific native logic, and replay-only speedup.
- `_validate_no_app_terms(...)` blocks RayJoin and other app-shaped primitive names.  The test explicitly confirms `rayjoin_overlay_fast_path` is rejected.
- The tests cover export/contract validation, cache-key reuse, app-name rejection, distinct-vs-replay classification, `require_distinct` failure, run metadata, owned-session close behavior, invalid timing, and foreign-batch failure.
- The old Goal3873/Goal3877 full-module failures are accurately described as historical `docs/reports/...` path noise.  Each module has one report-reading test that fails after the public-doc cleanup, while the runtime/contract subsets pass.

## Process Caveat

Claude could not execute the suite in its own sandbox because mounted copies of large source files appeared truncated, causing a spurious syntax issue.  Direct source inspection showed the real files were complete and correct.  The report's documented local runs stand:

```text
Ran 12 tests in 0.008s
OK
```

plus the two 4-test prepared-session regression subsets.

## Closeout

Goal5044 may close as:

```text
completed_public_prepared_session_query_batch_contract
```

Next authorized goal:

```text
Goal5045 - Public device_order_by
```
