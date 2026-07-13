# Goal5458 - Generic Mutable AABB CPU Contract

Date: 2026-07-10

## Result

Implemented public app-neutral APIs:

```text
MutableAabbIndex2D
prepare_mutable_aabb_index_2d
MUTABLE_AABB_INDEX_2D_CONTRACT
```

The execution model is explicitly:

```text
atomic_snapshot_rebuild
native_incremental_mutation = false
```

## Contract

- stable explicit IDs or monotonic automatic IDs;
- update/delete require active IDs;
- deleted IDs cannot be reused until `clear` resets the lifecycle;
- batch validation precedes rebuild;
- a new prepared snapshot is built before state swap;
- failed validation or failed rebuild leaves old revision and rows unchanged;
- clear creates a valid empty state;
- closed sessions and malformed query IDs fail closed;
- CPU and OptiX are the only current backends.

## Non-LibRTS Consumer

`tests/goal5458_generic_mutable_aabb_index_contract_test.py` uses the API as a
dynamic obstacle/contact broadphase. It moves, deletes, and inserts obstacles
while preserving stable IDs. The core module contains no LibRTS, author, paper,
or Ray Multicast identity.

## Validation

```text
Goal5457 + Goal5458 tests = 9 OK
```

## Boundary

This establishes generic mutation semantics using snapshot rebuild. It does not
claim native incremental GAS refit, author mutation performance parity, paper
mutation figures, or full LibRTS reproduction. Embree is not part of the route.

## Exit Label

```text
goal5458_generic_mutable_aabb_cpu_contract_complete__review_pending
```
