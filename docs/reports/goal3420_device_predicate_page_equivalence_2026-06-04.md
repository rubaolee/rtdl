# Goal3420 Device-Predicate Page Equivalence Probe

Status: implemented with pod evidence on NVIDIA RTX A5000.

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

## Pod Result

The full public RayJoin CDB probe was run on pod commit
`b1f25366acab845036963a06b5c7aa72fd141cd7`.

| Measure | Host-exact oracle | Device predicate pages |
| --- | ---: | ---: |
| points | 16,545 | 16,545 |
| closed shapes | 15,700 | 15,700 |
| pair rows | 47,262 | 47,570 |
| missing device pairs | 0 | n/a |
| extra device pairs | n/a | 308 |
| grouped point keys | 16,476 | 16,476 |
| mismatched grouped counts | 0 | 248 |

The device predicate path is therefore a strong device-resident broad-phase /
superset producer, but not an exact predicate authority yet. It emitted no
missing host-exact pairs on this dataset, but it emitted 308 extra pairs, which
is enough to corrupt 248 grouped counts.

## Boundaries

This is not the final v2.8 device-resident exact predicate implementation.

- The device-produced pair stream is still the candidate/native predicate path,
  not a new native exact page-plan producer.
- The host-exact path is used as a correctness oracle, not to produce the device
  pair columns.
- The full-CDB artifact does not prove equivalence. It proves the current device
  predicate is conservative on this dataset: no missing pairs, but false
  positives remain.
- Universal exact predicate, default-route, RT-core speedup, true zero-copy, and
  release claims remain blocked.

## Next Step

Add a device-resident refinement/filter after the RT candidate predicate and
before grouped continuation. The desired next shape is:

```text
native page plan -> RT broad-phase predicate pairs -> device exact/refine filter
-> exact device pair columns -> page-local grouped continuation
```

That next stage must keep the host-exact path as an oracle in tests, but must not
use host refinement to produce the device columns.
