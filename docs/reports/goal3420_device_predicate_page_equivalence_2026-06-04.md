# Goal3420 Device-Predicate Page Equivalence Probe

Status: implemented locally; pod evidence required before it can be used as
v2.8 engineering evidence.

## Purpose

Goals 3413-3418 gave RTDL a caller-visible page/retry contract and the first
native page-plan handle for exact point/closed-shape pair columns. The remaining
hard block is that the current `exact_device_columns` path is still
host-refined inside the native bridge before pair IDs are uploaded to CUDA
columns.

This goal adds a narrow evidence probe for the next step: use the existing
device-produced point/closed-shape predicate column path page by page, retry
overflow explicitly, consume the result on device with grouped count, and compare
the emitted pair multiset against the old host-exact path used only as an oracle.

## What This Does

The probe in `scripts/goal3420_device_predicate_page_equivalence_probe.py`:

1. Loads the public RayJoin CDB fixture.
2. Splits the query points into caller-visible pages with
   `PairColumnPagedRecoveryContract`.
3. For each page, runs `prepared.candidate_device_columns(...)`.
4. Retries pages explicitly when the first capacity is too small.
5. Consumes recovered device columns through
   `grouped_count_by_left_id_compact_device_columns(...)`.
6. Downloads only audit samples/counts to compare against the existing host-exact
   oracle.

## Boundaries

This is not the final v2.8 device-resident exact predicate implementation.

- The device-produced pair stream is still the candidate/native predicate path,
  not a new native exact page-plan producer.
- The host-exact path is used as a correctness oracle, not to produce the device
  pair columns.
- A passing full-CDB artifact proves equivalence for that dataset and backend
  configuration only.
- Universal exact predicate, default-route, RT-core speedup, true zero-copy, and
  release claims remain blocked.

## Next Step If The Probe Passes

Promote the successful pattern into a native page-plan mode that can produce
device-predicate pages from the native handle, still fail-closed and still
audited against host-exact oracle fixtures until the exactness contract is
broadened.
