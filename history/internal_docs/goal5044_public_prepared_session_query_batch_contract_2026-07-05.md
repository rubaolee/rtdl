# Goal5044 - Public Prepared Session / Query-Batch Contract

Date: 2026-07-05

Exit label:

```text
completed_public_prepared_session_query_batch_contract
```

## Purpose

Goal5044 turns the v2.14.3 RayJoin-proven prepared-base/query-batch discipline into a public RTDL contract.  The objective is not to add a RayJoin shortcut and not to claim new performance.  The objective is to make the lifecycle visible and generic:

- prepare a base geometry session explicitly;
- prepare query batches explicitly;
- separate cold CLI, warm-process fresh, distinct query-batch, and same-input replay regimes;
- record phase/run metadata without allowing replay-only numbers to become product claims.

This builds on the existing v2.10 prepared-session residency substrate instead of inventing a new session surface.

## Implementation

Modified files:

- `src/rtdsl/prepared_session_residency.py`
- `src/rtdsl/__init__.py`
- `tests/goal5044_public_prepared_geometry_session_contract_test.py`

New public symbols:

```text
PREPARED_GEOMETRY_SESSION_CONTRACT_VERSION
PREPARED_GEOMETRY_SESSION_API_MATURITY
PREPARED_GEOMETRY_SESSION_CLAIM_BOUNDARY
PREPARED_GEOMETRY_SESSION_REGIME_LABELS
PreparedGeometrySession
PreparedQueryBatch
describe_prepared_geometry_session_contract
prepared_geometry_session
validate_prepared_geometry_session_contract
```

The existing v2.10 internal/historical helpers remain available:

```text
RtdlPreparedSessionCacheKey
RtdlPreparedSessionResidencyPolicy
ExplicitPreparedSessionCache
get_or_prepare_explicit_session
make_prepared_session_cache_key
```

Goal5044 does not remove or replace them.  `PreparedGeometrySession` wraps their key/fingerprint discipline and adds the v2.14.4 public lifecycle vocabulary.

## Regime Labels

The public contract exposes exactly four labels:

```text
cold_cli_one_shot
warm_process_fresh
prepared_base_distinct_query_batch
prepared_replay_same_input_diagnostic
```

Important behavior:

- the API derives query-batch identity from explicit query fingerprints;
- a new fingerprint is classified as `prepared_base_distinct_query_batch`;
- repeating a prior fingerprint is classified as `prepared_replay_same_input_diagnostic`;
- callers can pass `require_distinct=True`, in which case same-input replay fails closed instead of being mislabeled as query-many.

This directly encodes the v2.14.3 review lesson: same-input replay is useful diagnostics, but it is not a query-many workload.

## Public Metadata

`PreparedGeometrySession.to_metadata()` reports:

- session id from the existing prepared-session cache-key substrate;
- primitive/backend/partner/device;
- base fingerprint and coordinate-domain fingerprint;
- query-batch counts;
- distinct-query and replay counts;
- phase timing metadata;
- claim-boundary flags.

`PreparedGeometrySession.run_metadata(...)` records:

- the batch metadata;
- output mode;
- phase timings such as `compile_setup_sec`, `per_input_workspace_setup_sec`, and `kernel_run_sec`;
- optional device-residency metadata from the producing route.

It does not execute geometry and does not create performance claims.

## Claim Boundary

All public contract metadata keeps these false:

```text
release_authorized
public_speedup_claim_authorized
true_zero_copy_claim_authorized
automatic_partner_selection_authorized
app_specific_native_engine_logic_allowed
```

The new contract is a public API shape and accounting guard, not a performance result.  It also does not rename the deeper legacy native symbols that still contain RayJoin-era names; that debt remains for Goal5050's boundary report.

## Verification

Command:

```powershell
$env:PYTHONPATH="src"; py -3 -m unittest tests.goal5044_public_prepared_geometry_session_contract_test tests.goal5043_public_device_column_buffer_contract_test
```

Result:

```text
Could not find platform independent libraries <prefix>
............
----------------------------------------------------------------------
Ran 12 tests in 0.005s

OK
```

Prepared-session non-document regression subset:

```powershell
$env:PYTHONPATH="src"; py -3 -m unittest tests.goal3873_prepared_session_residency_contract_test.Goal3873PreparedSessionResidencyContractTest.test_contract_requires_explicit_keys_and_blocks_claims tests.goal3873_prepared_session_residency_contract_test.Goal3873PreparedSessionResidencyContractTest.test_cache_key_is_stable_and_rejects_app_shaped_primitives tests.goal3873_prepared_session_residency_contract_test.Goal3873PreparedSessionResidencyContractTest.test_policy_and_explicit_cache_record_hits_misses_and_invalidation tests.goal3873_prepared_session_residency_contract_test.Goal3873PreparedSessionResidencyContractTest.test_timing_summary_keeps_goal3872_cold_hot_lesson_non_authorizing
```

Result:

```text
Could not find platform independent libraries <prefix>
....
----------------------------------------------------------------------
Ran 4 tests in 0.003s

OK
```

Explicit cache helper non-document regression subset:

```powershell
$env:PYTHONPATH="src"; py -3 -m unittest tests.goal3877_explicit_prepared_session_reuse_helper_test.Goal3877ExplicitPreparedSessionReuseHelperTest.test_get_or_prepare_calls_prepare_once_then_reuses tests.goal3877_explicit_prepared_session_reuse_helper_test.Goal3877ExplicitPreparedSessionReuseHelperTest.test_reuse_result_metadata_is_non_authorizing tests.goal3877_explicit_prepared_session_reuse_helper_test.Goal3877ExplicitPreparedSessionReuseHelperTest.test_policy_key_mismatch_fails_closed tests.goal3877_explicit_prepared_session_reuse_helper_test.Goal3877ExplicitPreparedSessionReuseHelperTest.test_prepare_must_be_callable_on_miss
```

Result:

```text
Could not find platform independent libraries <prefix>
....
----------------------------------------------------------------------
Ran 4 tests in 0.002s

OK
```

Full old Goal3873/3877 modules were not used as the deciding gate because their final tests read historical `docs/reports/...` files that were moved out of the public documentation tree during earlier cleanup.  A full run failed only on those missing historical report paths, not on the prepared-session runtime contract.

## What This Proves

- RTDL now has a public prepared-geometry session/query-batch contract.
- Same-input replay cannot be silently presented as query-many through this API.
- Cold CLI, warm-process fresh, distinct query-batch, and replay are first-class labels.
- The contract reuses the existing prepared-session cache key and explicit cache substrate.
- Public metadata has structured phase fields and claim-boundary flags.

## What This Does Not Prove

- It does not prove a new RayJoin performance number.
- It does not prove true zero-copy.
- It does not prove native prepared-session internals have been renamed away from RayJoin-era terms.
- It does not prove a public `device_group_by`.
- It does not authorize public speedup wording.

## Next Goal

Proceed to Goal5045: public `device_order_by` over the already proven native CUDA lexsort path, while keeping `device_group_by` internal unless a device-resident reduce proof exists.
