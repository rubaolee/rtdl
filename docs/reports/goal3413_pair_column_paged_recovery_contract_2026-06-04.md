# Goal3413 - Generic Pair-Column Paged Recovery Contract

Date: 2026-06-04

Verdict: accept-with-boundary.

## Purpose

Goal3411 proved that full-CDB exact pair-column recovery can be orchestrated
with caller-visible point windows, explicit retry, and key-addition merging.
Goal3413 pulls the reusable pieces out of that probe into a generic contract:

- `PairColumnPageRequest`
- `PairColumnPagedRecoveryContract`
- `PairColumnPageRecoveryRecord`
- `iter_pair_column_page_requests(...)`
- `merge_grouped_count_maps(...)`
- `summarize_page_recovery_records(...)`

The contract is deliberately about pair-column pages and grouped summaries, not
about a named application.

## Contract Rules

- Pages are caller-visible.
- Initial capacity is bounded and explicit.
- Overflow is fail-closed.
- Retry is explicit and caller controlled.
- Per-page grouped summaries merge by key addition.
- Group keys are not assumed to be disjoint across pages.
- Hidden dispatch and automatic retry remain unauthorized.

## Probe

The new probe script,
`scripts/goal3413_pair_column_paged_recovery_probe.py`, uses the generic
contract against the same full `br_county.cdb` workload as Goal3411. It emits a
fresh artifact once run on an OptiX pod:

`docs/reports/goal3413_pair_column_paged_recovery_probe_2026-06-04.json`

## Boundary

This is still a Python-level orchestration contract, not the native graduation
target. It does not implement:

- native paged streams,
- device-only exact predicates,
- automatic retry,
- hidden dispatch,
- true zero-copy,
- public speedup claims,
- RT-core speedup claims,
- RayJoin reproduction claims,
- release authorization.

The next native target remains:

```text
prepare -> page_plan -> produce_page(page_index) -> consume_page -> release_page
```
