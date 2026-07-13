# Goal5046 - device_group_by / Segmented Reduce Public-Readiness Decision

Date: 2026-07-06

Exit label:

```text
completed_internal_only_device_group_by_until_device_resident_reduce
```

## Purpose

Goal5046 decides whether v2.14.4 should expose public `device_group_by`.

The answer is no for v2.14.4.  RTDL has useful grouped/segmented reduction assets, but the current system does not yet have a complete public grouped-reduce contract that proves:

- device-resident input;
- no hidden host `row_values` path;
- generic key/value schema;
- POD execution;
- explicit overflow/fallback behavior;
- no RayJoin/app-specific carrier semantics.

Therefore `device_group_by` remains internal/experimental.  Public v2.14.4 may ship `device_order_by`, but must not imply public grouped reduce.

## Evidence

### 1. Partner-resident columnar native execution is still blocked

`src/rtdsl/columnar_partner.py` still states:

```text
Current OptiX compatibility payload stores host scalar row_values.
Current OptiX exact filtering and grouped count/sum reductions read host row_values.
```

and planning returns:

```text
native_execution_allowed: False
```

This directly blocks a public claim that grouped count/sum over RTDL device columns is already a true device-resident native path.

### 2. Numba segmented assets exist but are not the public device_group_by contract

`src/rtdsl/numba_partner_continuation.py` contains useful primitives:

```text
run_numba_segmented_count_i64
run_numba_segmented_sum_f64
run_numba_segmented_min_f64
run_numba_segmented_max_f64
run_numba_grouped_vector_sum_f64x2
```

These are valuable internal/partner continuation assets.  However, they do not yet constitute a public `device_group_by` API:

- some paths still advertise `host_prefix_sum_used`;
- arg-reduce compaction can use `host_present_group_compaction_used`;
- validation/output compaction semantics differ by operation;
- there is no single public schema tying `DeviceColumnBuffer` input, group-key contract, value columns, overflow/fallback, and result metadata together;
- no Goal5046 POD run proves public grouped reduce as a full device-resident API.

### 3. device_order_by explicitly does not authorize group_by

`describe_device_order_by_contract()` reports:

```text
supports_public_device_group_by: False
device_group_by_public_claim_authorized: False
```

Goal5046 preserves that boundary.

## Implementation

No public `device_group_by` function was added.

Added guard test:

```text
tests/goal5046_device_group_by_public_readiness_decision_test.py
```

The test verifies:

- `rt.device_group_by` is absent;
- `device_group_by` is absent from `rt.__all__`;
- `columnar_partner.py` still documents host `row_values` grouped-reduce blockers;
- Numba grouped assets exist but remain partner/internal assets, not public group-by;
- `device_order_by` still denies public grouped-reduce claims.

## Verification

Command:

```powershell
$env:PYTHONPATH="src"; py -3 -m unittest tests.goal5046_device_group_by_public_readiness_decision_test tests.goal5045_public_device_order_by_contract_test tests.goal5044_public_prepared_geometry_session_contract_test tests.goal5043_public_device_column_buffer_contract_test
```

Result:

```text
Could not find platform independent libraries <prefix>
.....................
----------------------------------------------------------------------
Ran 21 tests in 0.081s

OK
```

## What This Proves

- v2.14.4 does not accidentally publish `device_group_by`.
- The known host-row grouped-reduce blocker is still present and visible.
- Existing Numba grouped/segmented assets are acknowledged but not over-promoted.
- `device_order_by` remains public; `device_group_by` remains internal.

## What This Does Not Prove

- It does not prove public grouped reduce is impossible.
- It does not reject Numba as a partner.
- It does not remove internal grouped/segmented assets.
- It does not prove a POD grouped-reduce performance number.

## Requirements To Promote Later

A future goal may promote public `device_group_by` only after it provides:

1. a generic public input/output schema over `DeviceColumnBuffer`;
2. group-key dtype and layout contract;
3. supported reductions such as count/sum with explicit overflow/fallback behavior;
4. metadata proving no hidden host `row_values` path;
5. POD execution proof;
6. at least one non-RayJoin consumer;
7. tests proving no app-specific carrier/output-chain semantics.

Until then, any RayJoin or app route may use internal grouped assets only with explicit internal/experimental metadata.
