# Goal3407 - Independent Review of Goal3404: Exact Device Columns Explicit Retry

Date: 2026-06-04
Reviewer: Claude (claude-sonnet-4-6), independent read-only review
Verdict: **accept-with-boundary**

---

## Purpose

Goal3404 proves the explicit caller-controlled recovery path for
`PairColumnStreamCapacityStatus`: a bounded `exact_device_columns` call
overflows at `max_rows=100`, the caller reads `retry_capacity_hint=11316`, and
an explicit second call with that capacity produces a device-resident exact
stream whose pairs match the host-refined exact rows.

---

## Files Inspected

- `scripts/goal3404_exact_device_columns_explicit_retry_probe.py`
- `docs/reports/goal3404_exact_device_columns_explicit_retry_probe_2026-06-04.json`
- `docs/reports/goal3404_exact_device_columns_explicit_retry_probe_2026-06-04.md`
- `tests/goal3404_exact_device_columns_explicit_retry_probe_test.py`
- `src/rtdsl/optix_runtime.py` (lines 1547-1744, 10753-10829)

---

## Q1 - Explicit Caller-Controlled Retry vs Hidden Dispatch / Automatic Retry

**Pass.**

The probe code is unambiguous (script lines 52-64):

1. `prepared.exact_device_columns(points, max_rows=100)` → returns an
   `OptixNativeDevicePairColumnOutput` with `overflow=True`.
2. Caller reads `overflow_columns.retry_capacity_hint` from the returned object.
3. Caller explicitly issues `prepared.exact_device_columns(points, max_rows=retry_hint)`.

The `exact_device_columns` implementation (`optix_runtime.py:10753-10829`) contains
no retry loop. It makes exactly one call to the native library with the
caller-supplied `capacity` and returns the raw result. There is no mechanism
for automatic re-dispatch.

`_cupy_column` (`optix_runtime.py:1716-1721`) raises `RuntimeError` immediately
on overflow with the message `retry explicitly with max_rows>=required_capacity`
rather than silently retrying. This is the correct fail-closed behaviour.

`claim_boundary.automatic_retry_authorized` and `hidden_dispatch_authorized` are
both `false` in the artifact and are asserted false in the test.

---

## Q2 - Overflow Status: Required Capacity Exposed, No Partial Rows

**Pass.**

`PairColumnStreamCapacityStatus.__post_init__` (`optix_runtime.py:1558-1573`)
enforces two invariants at construction time when `overflowed=True`:

- `row_count == 0` (line 1568-1569): no partial rows can escape.
- `required_capacity > capacity` (line 1570-1571): overflow must be genuine.

These invariants are structural - a `PairColumnStreamCapacityStatus` object
with inconsistent state cannot be constructed. The constructor is reached via
the `capacity_status` property on every `OptixNativeDevicePairColumnOutput`,
so every callee is protected.

Artifact confirms: `overflow_row_count=0`, `overflow_capacity=100`,
`overflow_required_capacity=11316`, `partial_result_returned=false`.

`retry_capacity_hint` is derived directly from `required_capacity` when
`overflowed=True` (`optix_runtime.py:1576-1577`), making it the authoritative
retry signal without a separate field that could diverge.

One internal naming note: `required_capacity` on `OptixNativeDevicePairColumnOutput`
reads from `candidate_event_count` (`optix_runtime.py:1637-1638`). The metadata
documents this explicitly with `legacy_pair_column_count_field: "candidate_event_count"`
and `host_refined_exact_rows_inside_native_bridge: True`. This is a known design
choice for the host-refined bridge, not a gap.

---

## Q3 - Retried Stream Matches Exact Rows and Is Device-Resident

**Pass.**

The `device_resident` property (`optix_runtime.py:1616-1622`) requires all four
conditions to hold: `left_ids_device_ptr > 0`, `right_ids_device_ptr > 0`,
`capacity > 0`, `not overflow`. Artifact reports `retry_device_resident=true`.

Pair-match evidence from the artifact:

| Measure | Value |
|---|---:|
| Exact row count (host-refined) | 11316 |
| Retry row count | 11316 |
| Missing exact pairs | 0 |
| Extra pairs | 0 |
| `pairs_match_exact_rows` | true |

The probe extracts pairs from the retry CuPy columns via `_column_pairs` (a
set of `(point_id, shape_id)` tuples) and from the host-refined rows via
`_row_pairs`, then computes symmetric difference. Both missing and extra sets
are empty, confirming the retried device stream is an exact match.

The retry `capacity_status` correctly shows `retry_capacity_hint=null` on
success (`optix_runtime.py:1641-1642`), confirming no further retry is needed.

---

## Q4 - Claim Boundaries

**Pass. All boundaries closed.**

All nine claim-boundary flags are `false` in the artifact and are asserted false
in `test_retry_is_explicit_and_boundaries_are_closed`. Hardcoded guards in
the runtime (e.g., `true_zero_copy_authorized` returning `False` at
`optix_runtime.py:1625-1626`, `exact_relation_witness_rows_materialized`
returning `False` at `optix_runtime.py:1629-1630`) ensure these cannot be
enabled implicitly.

The probe's `claim_boundary` block explicitly includes both
`automatic_retry_authorized: false` and `hidden_dispatch_authorized: false`,
which are the two flags most relevant to this goal's claims.

---

## Summary

| Question | Finding |
|---|---|
| Explicit caller-controlled retry (not hidden/auto) | Pass |
| Overflow exposes required capacity, no partial rows | Pass |
| Retry stream matches exact rows, device-resident | Pass |
| All claim boundaries closed | Pass |

**Verdict: accept-with-boundary.**

The explicit recovery path is well-proven on hardware (NVIDIA RTX A5000,
driver 580.126.09, commit `02bd4510`). The boundary is exactly what the self-report
states: this proves capacity-guided explicit retry for the existing
host-refined exact device-column bridge. It does not authorize automatic retry,
chunked streaming overflow recovery, a device-only exact predicate, true
zero-copy, hidden dispatch, public speedup claims, RT-core claims, RayJoin
reproduction claims, or release authorization.
