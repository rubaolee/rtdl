# Goal5457 - LibRTS Generic Mutation Contract Audit

Date: 2026-07-10

## Verdict

```text
requires_new_generic_api
```

RTDL can rebuild a prepared AABB index from a changed snapshot, but it does not
currently expose mutable prepared-index semantics. Rebuilding must not be
described as author-equivalent native update/refit.

## Author Semantics

At pinned commit `52509e8...`:

- `Insert` appends envelope batches and assigns implicit stable slot IDs;
- `Update(id, envelope)` updates geometry and refits touched GAS/IAS state;
- `Delete(id)` invalidates a slot and updates touched GAS/IAS state;
- `Clear` removes all geometry and resets the index;
- the author tests verify batch update against a rebuild oracle and delete with
  compact/non-compact configurations.

## RTDL Evidence

Current CPU and OptiX prepared AABB classes are immutable. The OptiX ABI exports
prepare, count, two row collectors, query preparation, and destroy, but no
geometry insert/update/delete/clear/refit symbol. `PreparedAabbIndex2DOptix`
owns a fixed device box buffer and GAS built in its constructor.

Historical `mutation_cpu_reference` changes Python boxes and invokes the CPU
reference again. It is useful oracle logic but is not prepared-state mutation.
Historical same-shape request-update APIs update query/request buffers, not
indexed geometry or acceleration structures.

## Required Generic Design

The first system API should be a transactional mutable AABB front door with:

- stable app-neutral row IDs;
- insert/update/delete/clear batch validation;
- atomic commit: build a new prepared snapshot, swap only on success, then
  close the previous handle;
- fail-closed dirty/closed/unknown-ID/duplicate-ID behavior;
- explicit metadata `execution_model=atomic_snapshot_rebuild`;
- CPU reference and OptiX snapshot-rebuild backends;
- a non-LibRTS dynamic obstacle/contact-broadphase consumer.

This is a semantic bridge, not native incremental update. Native refit is a
separate future architecture goal requiring new native ABI and acceleration
update support.

## Backend Boundary

```text
CPU = reference implementation
OptiX = prepared snapshot rebuild
Embree = excluded from this campaign
HIPRT = inactive
```

## Next Goals

```text
Goal5458 = generic transactional mutable AABB CPU contract + non-LibRTS consumer
Goal5459 = OptiX snapshot-rebuild parity on local Linux
Goal5460 = bounded LibRTS mutation sequence against author semantics
```

No mutation performance claim is authorized in these goals.

## Exit Label

```text
goal5457_requires_new_generic_mutable_aabb_api__review_pending
```
