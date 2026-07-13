# Goal5460 - LibRTS Same-Input Mutation Gate

Date: 2026-07-10

## Objective

Compare the pinned author public mutation API with the generic RTDL mutable AABB
API on one deterministic, discriminating sequence. Close semantic result-count
agreement without conflating two different execution models.

## Author Probe

The app-owned probe calls only the pinned public author API:

```text
SpatialIndex<float, 2>::Init
Insert
Query(Predicate::kIntersects)
Update
Delete
Insert
Clear
```

The probe is stored at:

```text
Paper-reproduction-apps/librts-paper/author_patches/goal5460_author_mutation_probe.cu
```

It does not replace or reimplement author mutation semantics.

## Author Compatibility Finding

The pinned author `updateInstanceAccel()` allocates
`tempUpdateSizeInBytes` but passes the smaller `tempSizeInBytes` to
`optixAccelBuild`. On the local Linux OptiX runtime the first update fails with:

```text
tempBufferSizeInBytes is less than tempUpdateSizeInBytes
OPTIX_ERROR_INVALID_VALUE
```

The disclosed one-line compatibility patch passes the already allocated update
size:

```text
goal5460_fix_instance_update_temp_buffer.patch
```

This corrects the update buffer argument. It does not alter geometry, IDs,
predicates, mutation policy, result collection, or timing code. The comparison
therefore uses a clearly labeled patched-author build rather than silently
claiming an unmodified artifact run.

## Same Sequence

Both implementations receive the same initial boxes, range query, and
operations:

```text
insert ids 0,1; query
update id 1 to a far box; query
delete id 0; query
insert a matching box with automatic id 2; query
clear; query
```

## Result

```text
author patched public API counts = [2, 1, 0, 1, 0]
RTDL OptiX counts                = [2, 1, 0, 1, 0]
author appended ID               = 2
RTDL appended ID                 = 2
matched                          = true
```

Structured evidence:

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5460_same_input_mutation.json
```

## Execution-Model Boundary

The semantic outputs match, but the implementations are deliberately not
described as equivalent:

```text
author: native incremental GAS/IAS update
RTDL:   atomic prepared-snapshot rebuild
```

RTDL now supplies a useful public mutation contract, stable IDs, atomic swap on
successful rebuild, CPU/OptiX support, and a non-LibRTS consumer. It does not yet
supply native incremental mutation/refit.

## Validation

```text
Windows Goal5457-5460 suite: 15 OK, skipped=2 (no local OptiX)
Linux Goal5458-5459 runtime suite: 8 OK
Linux generic OptiX snapshot gate: matched
Linux patched-author mutation probe: matched
Linux combined same-input mutation gate: matched
```

The GTX 1070 evidence is functional only. No timing ratio is reported.

## Claim Boundary

Authorized:

- bounded same-input Insert/Update/Delete/Insert/Clear result-count agreement;
- matching implicit appended ID lifecycle for this sequence;
- generic RTDL mutation semantics through atomic snapshot rebuild.

Not authorized:

- native-incremental RTDL mutation/refit completion;
- mutation performance parity or speedup;
- paper mutation figure reproduction;
- Ray Multicast or PIP reproduction;
- full LibRTS paper reproduction;
- Embree evidence;
- a LibRTS-specific RTDL core primitive.

## Exit Label

```text
goal5460_librts_same_input_mutation_semantics_matched__review_pending
```
