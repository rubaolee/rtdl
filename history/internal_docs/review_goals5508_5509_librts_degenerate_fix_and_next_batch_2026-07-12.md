# External Review: Goals5508-5509 LibRTS

Date: 2026-07-12

## Verdicts

```text
Goal5508: approve_goal5508_generic_float32_degenerate_indexed_aabb_validity_fix
Goal5509: approve_goal5509_exact_range_intersects_next_batch_bounded
```

Blocking findings: none.

Required amendments: none.

## Goal5508 assessment

The fix is a genuine generic RTDL correctness correction, not author-specific
imitation. Four indexed records in each diagnosed prefix become zero-width or
zero-height after float32 conversion. Generic OptiX AABB padding made those
records traversable and created false-positive intersections. The isolated
subsets reproduce the complete pre-fix excess (`27` and `5005`), while author
and fixed RTDL both return zero.

The implementation uses an app-neutral strict validity predicate,
`min_x < max_x && min_y < max_y`, in the generic native intersection kernel.
It selects the correct indexed record for both forward and backward passes and
contains no LibRTS, RTSpatial, paper, or author identity. The two official
prefixes now match exactly:

```text
parks_Europe: 34,240,217 == 34,240,217
lakes_bz2:    34,581,812 == 34,581,812
```

The claim boundary is correct: no full matrix, pair-row, performance, paper,
author-specific-core, zero-copy, or Embree claim is authorized.

## Goal5509 assessment

The second exact query family,
`range-intersects_select_0.0001_queries_10000`, is provenance-bound to the
verified archive and reuses verified geometry members. Four independently
checkpointed cases match at count level:

```text
parks_Europe:                   2,486,816 == 2,486,816
dtl_cnty:                         242,920 ==   242,920
USACensusBlockGroupBoundaries:    423,893 ==   423,893
USADetailedWaterBodies:           651,647 ==   651,647
```

`parks.bz2` and `lakes.bz2` were attempted in the large batch but did not
receive independent checkpoints before the POD process was reclaimed. They
are correctly recorded as unresolved capacity/process-lifetime cases, not
matches and not semantic mismatches.

The current evidence is count-level only because the standard author binary
does not expose pair rows. Coverage is `10/42` attempted across the current
and prior batches, with `32` exact pairs remaining. No complete matrix,
pointwise relation, Figure 6, performance ratio, full-paper, zero-copy,
author-parity, or Embree claim is authorized.

## Non-blocking notes

1. Document strict validity semantics in the generic AABB API: consumers that
   need meaningful zero-width/zero-height geometry may require a separately
   authorized mode. The current default rejects degenerate boxes because the
   prior padded behavior was a false-positive artifact.
2. Add an explicit regression fixture that exercises the validity guard in
   both forward and backward passes, including the `prim` versus `qidx`
   indexed-record selection.
3. Continue using per-case checkpoint files for large official workloads; do
   not aggregate only at process exit.

## Final disposition

Goals5508 and 5509 are externally reviewed and approved within their bounded
claim boundaries. The range-intersects line remains open for the two large
case checkpoints and the remaining verified archive pairs. This review does
not authorize reopening performance or pair-row claims.
