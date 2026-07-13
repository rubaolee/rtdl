# Goals5461-5462 - Generic OptiX AABB Native Sparse Refit

Date: 2026-07-10

## Objective

Replace snapshot rebuild for pure fixed-cardinality AABB updates with a real,
app-neutral OptiX `BUILD_OPERATION_UPDATE` path while preserving failure
rollback. Keep insert, delete, and clear on the already verified atomic
snapshot-rebuild route.

## Implementation

The generic prepared OptiX AABB GAS is now built with:

```text
OPTIX_BUILD_FLAG_ALLOW_RANDOM_VERTEX_ACCESS
OPTIX_BUILD_FLAG_ALLOW_UPDATE
```

New generic native ABI:

```text
rtdl_optix_prepare_mutable_aabb_index_2d
rtdl_optix_refit_prepared_aabb_index_2d
rtdl_optix_refit_prepared_aabb_index_2d_slots
```

Ordinary immutable `prepare_aabb_index_2d(..., backend="optix")` keeps the
original non-update GAS build. Only the mutable front door selects the separate
update-capable prepare symbol, so unrelated immutable query paths do not pay
the update-capable build policy.

The final production path uses sparse slots. Python passes only changed stable
slot IDs and their replacement AABBs. Native code validates unique in-range
slots and stable IDs, updates only those packed-box/AABB records, then refits
the existing GAS.

Failure handling is transactional for the prepared handle: if refit fails,
native code restores the old changed records and refits the old GAS before
rethrowing. A rollback failure is reported explicitly rather than leaving the
handle silently usable.

Goal5463 closes the former rollback test gap with a private, test-only native
fault-injection environment variable. On Linux/OptiX hardware, one mode fails
after candidate device records and the candidate GAS update have both
succeeded, then verifies that rollback restores the old records and old GAS by
querying both the old and new locations. A
second mode also fails rollback after old records are restored; the prepared
handle is then poisoned, and all later query/refit entry points reject it. The
hook is app-neutral, absent from the public Python API, and inactive unless the
explicit test environment variable is set.

## Hybrid Public Contract

```text
pure Update on nonempty OptiX index -> native_sparse_slot_refit_with_rollback
Insert                            -> atomic_snapshot_rebuild
Delete                            -> atomic_snapshot_rebuild
Clear                             -> atomic_snapshot_rebuild
CPU mutations                     -> atomic_snapshot_rebuild
```

This is a generic `MutableAabbIndex2D` capability. No LibRTS identity or paper
operation appears in native or public system symbols.

## Functional Result

Local Linux / NVIDIA GeForce GTX 1070:

```text
native library builds
sparse refit symbol exported
Goal5459 + Goal5461 Linux tests: 6 OK
full nearby Linux mutation tests: 11 OK
LibRTS same-sequence counts: [2,1,0,1,0] matched
mutation models: refit, rebuild, rebuild, rebuild
```

The author still uses its native incremental GAS/IAS design. RTDL now uses
native OptiX refit for pure updates, but not for cardinality-changing mutation.

## Same-Host Generic Microbenchmark

The diagnostic updates one stable slot per iteration and compares RTDL native
sparse refit with RTDL full snapshot preparation on the same process, GPU, box
set, and alternating correctness query.

| boxes | repeats | sparse refit median | rebuild median | speedup |
|---:|---:|---:|---:|---:|
| 4,096 | 11 | 1.44 ms | 18.15 ms | 12.62x |
| 65,536 | 7 | 25.07 ms | 391.67 ms | 15.63x |

All alternating query counts match exactly.

The preceding full-array refit prototype measured only about 1.27x at 4,096
and 1.20x at 65,536 because Python repacked and uploaded every unchanged box.
The sparse ABI removes that avoidable boundary cost; the remaining refit still
legitimately updates the full GAS topology.

Evidence:

```text
history/internal_docs/goal5461_generic_optix_aabb_native_refit_linux.json
history/internal_docs/goal5461_generic_optix_aabb_native_refit_linux_65536.json
history/internal_docs/goal5462_generic_optix_aabb_sparse_refit_linux_4096.json
history/internal_docs/goal5462_generic_optix_aabb_sparse_refit_linux_65536.json
Paper-reproduction-apps/librts-paper/results/librts_goal5461_native_refit_mutation.json
Paper-reproduction-apps/librts-paper/results/librts_goal5462_native_sparse_refit_mutation.json
```

## Claim Boundary

Authorized:

- generic native fixed-cardinality/sparse-slot OptiX AABB refit;
- rollback-protected stable-ID update semantics, including injected post-write
  primary-failure recovery and fail-closed poisoning when rollback also fails;
- same-host RTDL refit-vs-rebuild microbenchmark results above;
- unchanged bounded LibRTS mutation result-count agreement.

Not authorized:

- native incremental Insert/Delete/Clear;
- author-vs-RTDL mutation performance parity;
- LibRTS paper performance, figures, or full reproduction;
- reuse of GTX 1070 timings as paper hardware evidence;
- Embree evidence;
- a LibRTS-specific native primitive.

## Exit Label

```text
goal5462_generic_optix_aabb_sparse_refit_complete__externally_reviewed
```
