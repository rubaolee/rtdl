# Goal4963 Exact LSI Pair-Id Device Columns Design Gate

Date: 2026-07-04

## Exit Label

`completed_exact_lsi_pair_id_device_column_design_gate__implementation_not_started`

## Purpose

Goal4960 established the corrected fresh writer-free binary route:

```text
fresh writer-free binary route: ~0.889s
AuthorPatch overlay compute:    0.0421s
fresh comparison:               ~21.1x slower
cached/replay body:             ~0.087s, not same denominator
```

Goal4961 found that no larger representative input is currently available on
the active POD, so Goal4962 cannot honestly run yet.

Goal4963 defines the next implementation target for the current public sample:
an **exact planar-map LSI pair-id device-column route**. This is the missing
piece between existing public planar-map LSI and the Layer 1/2 writer-free
binary operator.

## Current Fact Pattern

### Existing route A: exact host pair-id rows

Current public API:

```python
with prepare_planar_map_lsi_2d_optix(base) as lsi:
    with lsi.prepare_query(query) as prepared_query:
        rows = prepared_query.run_pair_id_rows()
```

Implementation path:

```text
PreparedOptixPlanarMapLsi2DQuery.run_pair_id_rows()
-> PreparedOptixSegmentPairIntersection.run_prepared_left_grouped_range_direct_pair_id_rows(...)
-> native rtdl_optix_run_prepared_segment_pair_id_rows_prepared_left_grouped_range_direct_intersection_with_predicate_mode(...)
-> OptixRowView over host RtdlSegmentPairIdRow rows
```

This route is exact and uses the planar-map LSI predicate, but returns a host
`OptixRowView`. The app then converts it to NumPy columns.

### Existing route B: candidate device columns

Current lower-level API:

```python
prepared_segment_pair.candidate_device_columns(...)
```

This returns device `left_id/right_id` columns, but it is a candidate-event
surface. It is not the exact planar-map LSI predicate output. Goal4958 measured
this explicitly:

```text
candidate_event_count = 20972
exact_pair_count      = 20860
```

So candidate device columns cannot replace exact LSI pair rows in RayJoin
overlay correctness.

### Existing route C: left-id count device columns

Current lower-level API:

```python
left_id_count_prepared_left_device_columns(...)
```

This can produce exact source-row counts for some probes, but it only preserves
left-id grouped counts. It loses right ids and therefore cannot feed RayJoin
reprojection/sort/group semantics.

## Missing Generic Primitive

Required primitive:

```python
with prepare_planar_map_lsi_2d_optix(base) as lsi:
    with lsi.prepare_query(query) as q:
        columns = q.run_pair_id_device_columns()
        # columns.left_id/right_id remain device-resident
```

Contract:

```text
Primitive: PLANAR_MAP_LSI_2D
Result: exact pair-id device columns
Columns: left_id:uint64/right_id:uint64 or int64-compatible column descriptors
Predicate: planar_map_lsi, same as run_pair_id_rows()
Ownership: native owner handle with explicit release
No bundled RayJoin helper
No output-chain, polygon, face, chain, or AuthorOfficial semantics
```

This is generic because it is a planar-map line-segment-intersection result
shape. RayJoin is only one downstream app that can consume the pair stream.

## Proposed Public/Private API Shape

Python:

```python
class PreparedOptixPlanarMapLsi2DQuery:
    def run_pair_id_device_columns(self) -> OptixNativeDevicePairColumnOutput:
        ...

class PreparedOptixPlanarMapLsi2D:
    def run_pair_id_device_columns(self, query_records_or_cdb) -> OptixNativeDevicePairColumnOutput:
        ...
```

Native symbol should be named generically, for example:

```text
rtdl_optix_run_prepared_segment_pair_exact_pair_id_device_columns_prepared_left_grouped_range_direct_intersection_with_predicate_mode
```

Avoid names containing `rayjoin`, `overlay`, `output_chain`, `polygon`, or
`AuthorOfficial`.

Return type can reuse:

```python
OptixNativeDevicePairColumnOutput
```

if and only if its metadata distinguishes:

```text
native_symbol = exact_pair_id_device_columns symbol
candidate_event_count = row_count, or a new exact_row_count field
contract = exact_planar_map_lsi_pair_ids
```

If that would overload candidate semantics too much, introduce a sibling
dataclass with the same column fields and stricter exact-result metadata.

## Required Implementation Strategy

The native implementation must not copy exact pairs into a host vector and then
re-upload. It should:

1. Count exact planar-map LSI pairs, or otherwise determine output capacity.
2. Allocate device `left_ids` and `right_ids` arrays.
3. Emit exact accepted pairs directly into those device arrays.
4. Return only descriptors, row count, capacity, overflow status, device ordinal,
   and phase timings to Python.

The implementation may use a two-pass exact-count-then-emit strategy if needed,
but the timing report must split:

```text
exact_count_sec
exact_device_emit_sec
host_materialization_sec
host_copy_sec
```

`host_materialization_sec` and `host_copy_sec` must be zero or explicitly absent
for the device-column route.

## Measurement Gate

This design does **not** assume that exact device columns will remove the full
~0.8s public LSI phase. That phase may be dominated by the exact traversal or
predicate itself rather than host materialization.

Goal4964 must first prove which is true:

| Case | Evidence | Decision |
|---|---|---|
| Host materialization/row bridge dominates | device-column fresh route materially reduces `lsi_public_rows_sec` while preserving exact pair count/fingerprint | Continue device-column implementation and Goal4965 |
| Exact traversal/predicate dominates | device-column route is near the same as host pair-id route | Do not oversell Layer 1/2; next performance problem is exact LSI traversal/predicate, not row-buffer handoff |
| Candidate route is faster but wrong | candidate row count differs from exact | Reject for RayJoin correctness |

This is the guard against repeating the prepared-replay denominator mistake.

## Correctness Gates

On the public County x Soil sample:

```text
exact_pair_count = 20860
fresh route semantic fingerprint:
  pair_count = 28815
  total_groups = 64459
  total_point_rows = 673371
```

The device-column route must match the host exact route before any performance
claim is allowed.

Minimum checks:

1. Exact pair-id device route row count equals host `run_pair_id_rows()`.
2. Device-column route consumed by the writer-free binary operator produces the
   same semantic fingerprint.
3. Existing `--validate-device-order` reference check remains true:

```text
map0_order_matches_cpu_longdouble_reference = true
map1_order_matches_cpu_longdouble_reference = true
```

## Genericity Gates

Must pass all:

- API and native symbol names are generic segment-pair / planar-map LSI names.
- Core result columns are only `left_id` and `right_id`.
- No face ids, output chains, text writer, AuthorOfficial, or RayJoin overlay
  semantics in the core primitive.
- The device-column output can be adapted through the existing generic
  `device_column_row_buffer` handoff.
- At least one non-RayJoin synthetic LSI consumer can consume the pair-id columns
  for a trivial device-side reduction or grouping.

## Performance Interpretation Rules

Allowed claim after Goal4964/4965 only if measured:

```text
Exact LSI pair-id device columns reduce fresh writer-free binary route from
~0.889s to X on the public County x Soil sample, with the same fingerprint.
```

Forbidden:

- Claiming `0.087s` as fresh overlay speed.
- Comparing cached/replay route to AuthorPatch `0.0421s`.
- Claiming this closes the full gap to AuthorPatch unless the fresh route is
  actually measured against the same denominator.
- Claiming broad RayJoin or Section 5.7 performance without larger data.

## Goal4964 Proposed Work

1. Add native exact pair-id device-column symbol.
2. Add Python wrapper on `PreparedOptixPlanarMapLsi2DQuery`.
3. Add app option in `section57_overlay_columnar_binary.py`, e.g.

```bash
--exact-lsi-device-columns
```

4. Add tests:

```text
tests/goal4964_exact_lsi_pair_id_device_columns_test.py
```

5. Run POD public sample:

```text
fresh host exact pair rows
fresh exact pair-id device columns
cached/replay remains diagnostic only
```

## Review Ask

Goal4963 should be approved only as a design gate. It does not authorize a
performance claim. It authorizes Goal4964 implementation only if reviewers agree
that the primitive is generic and the measurement gate is strong enough.
