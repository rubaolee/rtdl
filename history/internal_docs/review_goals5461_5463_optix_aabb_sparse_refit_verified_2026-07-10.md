# Review - Goals5461-5463 OptiX AABB Sparse Refit Verified

Date: 2026-07-10

## Verdict

```text
approve_goals5461_5462_generic_optix_aabb_native_sparse_refit
```

Goals5461-5463 may close. The two required amendments from the first review are
verified as complete.

## Required Amendments Verification

### RA-1 - Speedup Values

Closed. Call-for-review Q10 now reports the evidence-backed historical values:

```text
4,096 boxes:  12.62x
65,536 boxes: 15.63x
```

The post-amendment rerun (`14.69x` / `16.96x`) is correctly labeled as a
no-regression confirmation rather than being substituted as a more favorable
headline.

### RA-2 - Rollback Recovery And Fail-Closed Behavior

Closed with behavior-level Linux/OptiX hardware tests, not only source-string
checks.

`primary_after_device_and_gas_update` injects failure after candidate records,
AABBs, and GAS update succeed. The test verifies revision remains zero, the old
location still returns stable ID 77, the new location returns no row, and a
later ordinary sparse refit succeeds.

`primary_and_rollback_after_restore_write` also fails rollback. The prepared
handle becomes invalid; later point rows, range rows, count, and refit calls all
fail closed while Python host metadata remains unchanged.

Linux GTX 1070 verification rebuilt the native OptiX library and passed:

```text
Ran 15 tests
OK
```

## Blocking Findings

None.

## Required Amendments

None.

## Non-Blocking Boundary

The transactional guarantee covers the two tested failure boundaries. It does
not establish arbitrary CUDA driver, process-crash, or power-loss recovery.
Keep that limitation attached to future summaries.

## Final Status

```text
Goals5461-5463 = externally reviewed and approved
```
