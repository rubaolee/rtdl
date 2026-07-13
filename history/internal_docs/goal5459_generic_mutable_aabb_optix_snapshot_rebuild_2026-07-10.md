# Goal5459 - Generic Mutable AABB OptiX Snapshot-Rebuild Gate

Date: 2026-07-10

## Result

The public app-neutral `MutableAabbIndex2D` contract now has functional Linux
OptiX evidence. A single mutable index was queried across this sequence:

```text
initial       -> [(900, 10), (900, 20)]
update id 20  -> [(900, 10)]
delete id 10  -> []
insert id 30  -> [(900, 30)]
clear         -> count 0
```

Every mutation built a new prepared OptiX AABB snapshot before swapping it into
the public mutable handle. Stable public IDs survived rebuilds and were mapped
back from prepared row positions correctly.

## Environment

```text
host: lx1
GPU: NVIDIA GeForce GTX 1070
backend: OptiX
evidence use: functional only
```

The evidence is stored in:

```text
history/internal_docs/goal5459_generic_mutable_aabb_optix_snapshot_rebuild_linux.json
```

## Validation

```text
local Goal5457-5459 suite: 11 OK, skipped=2 (Windows has no OptiX runtime)
Linux Goal5458-5459 suite: 8 OK
Linux structured gate: matched=true
```

The gate records `execution_model=atomic_snapshot_rebuild`,
`native_incremental_mutation=false`, revision progression, active IDs, and the
exact rows at every revision.

## System Boundary

This is a generic mutable AABB index capability. It contains no LibRTS identity,
paper operation names, or author-specific update rules. It is exercised by a
non-LibRTS dynamic-obstacle consumer in Goal5458.

This result does not claim:

- native incremental GAS update/refit;
- mutation performance improvement or parity;
- LibRTS paper mutation reproduction;
- an Embree backend.

## Exit Label

```text
goal5459_generic_mutable_aabb_optix_snapshot_rebuild_matched__review_pending
```
