# Goal5463 - Goals5461-5462 Review Amendment Response

Date: 2026-07-10

## Scope

This amendment responds to the external `approve_with_required_amendments`
review of the generic OptiX AABB sparse-refit milestone. It changes no LibRTS
application semantics and introduces no app-specific native primitive.

## RA-1 - Correct The Stale Speedup Values

The call-for-review Q10 previously contained stale values. It now matches the
committed evidence and the main report:

```text
4,096 boxes:  12.62x
65,536 boxes: 15.63x
```

Exact evidence fields are `12.621501...` and `15.625437...`. These remain
same-host RTDL sparse-refit-versus-RTDL-rebuild diagnostics on one GTX 1070,
not LibRTS paper or author-performance evidence.

## RA-2 - Exercise Recovery And Fail-Closed Behavior

The native prepared AABB handle now has an internal validity state. A rollback
failure poisons the handle. Every 2-D prepared-index query/refit entry point
checks this state and rejects a poisoned handle with:

```text
prepared OptiX AABB index is invalid after failed rollback
```

A private test-only environment variable provides two generic fault modes:

```text
RTDL_OPTIX_TEST_AABB_REFIT_FAULT=primary_after_device_and_gas_update
RTDL_OPTIX_TEST_AABB_REFIT_FAULT=primary_and_rollback_after_restore_write
```

The first mode throws only after candidate packed records, candidate AABBs,
and the candidate OptiX GAS update have succeeded. The rollback path restores
old records and executes an old-GAS update. The hardware test then verifies:

```text
revision remains 0;
old point location still returns stable ID 77;
new point location returns no row;
a later ordinary sparse refit succeeds and advances revision to 1.
```

The second mode also throws after old records are restored but before the old
GAS rollback update. Native code marks the prepared handle invalid. The test
verifies the original mutation raises the explicit rollback error and all later
query/refit calls fail closed. Python host metadata and revision remain
unchanged because native success was never returned.

The fault hook is not a public Python feature. It is inert unless the explicit
test variable is set and contains no LibRTS/paper identity.

## Verification

Windows contract/regression run:

```text
PYTHONPATH=src
Ran 25 tests in 0.093s
OK (skipped=5: OptiX runtime unavailable on Windows)
```

Local Linux hardware run after rebuilding `librtdl_optix.so`:

```text
GPU: NVIDIA GeForce GTX 1070
Ran 15 tests in 0.348s
OK
```

The Linux set includes the two fault-injection behavior tests, immutable
prepare isolation, ordinary mutation/refit behavior, source/ABI contracts, and
committed sparse-refit evidence checks.

The same rebuilt library was also rerun through the original microbenchmark:

```text
4,096 boxes:  refit 1.183ms vs rebuild 17.376ms = 14.69x
65,536 boxes: refit 22.935ms vs rebuild 389.073ms = 16.96x
```

These are a no-regression confirmation, not replacements chosen to make the
headline larger. The original Goal5462 `12.62x` / `15.63x` results remain the
historical evidence addressed by RA-1; both runs remain bounded same-host
diagnostics.

## Claim Boundary

Authorized:

- evidence-backed `12.62x` and `15.63x` same-host RTDL microbenchmarks;
- successful recovery after a fault injected after candidate GAS update;
- visible, persistent fail-closed behavior after injected rollback failure;
- generic stable-ID sparse-slot OptiX refit semantics.

Not authorized:

- arbitrary CUDA/driver/process-failure recovery beyond the tested boundary;
- native incremental Insert/Delete/Clear;
- author-vs-RTDL performance parity;
- LibRTS paper performance or full reproduction;
- paper-hardware claims from the GTX 1070;
- Embree evidence.

## Exit Label

```text
goal5463_goals5461_5462_required_amendments_complete__externally_reviewed
```
