# Goal4859 Section 5.7 Status: LSI Row-Surface Gap Found

Date: 2026-07-02

## Verdict

Goal4859 must pause the full Section 5.7 overlay attempt before performance or
full County x Zipcode output comparison.

The blocker is now sharply scoped:

`blocked_by_lsi_row_surface_contract_gap`

This is not a PIP/Section 5.3 failure yet. It is not a broad RayJoin failure.
It is specifically an LSI row-materialization contract failure exposed by
Section 5.7.

## Why This Belongs Back To Section 5.2

Section 5.2 had previously validated LSI scalar counts. That remains true for
the tested available cases.

Section 5.7 needs more than scalar counts. It needs the actual intersection rows:

- left segment id
- right segment id
- intersection coordinates

The current public count path and row materialization path disagree. Therefore
Section 5.2 needs a new row-contract gate:

`planar_map_lsi_count == planar_map_lsi_rows.length`

The old Section 5.2 count-only gate is necessary but not sufficient for Section
5.7 overlay construction.

## Evidence Summary

All evidence below was produced in user/application-author mode for Goal4859.
No RTDL runtime/native edits were made during this probe sequence.

### Small Synthetic Probe

File:

`history/internal_docs/goal4859_synthetic_count_vs_row_contract_probe_summary.json`

Result:

- `mismatch_count: 0`

Basic endpoint, crossing, collinear, and small multi-segment synthetic cases did
not reproduce the gap. This proves the issue is not the simplest endpoint rule.

### Australia Representative Pair

File:

`history/internal_docs/goal4859_au_lsi_row_surface_summary.json`

Result:

- expected / public planar-map LSI count: `13622`
- public raw segment-pair row count: `103843`

Interpretation: raw segment-pair rows are not the planar-map LSI row contract.

File:

`history/internal_docs/goal4859_au_hidden_predicate_lsi_rows_summary.json`

Result:

- public planar-map LSI count: `13622`
- hidden-predicate row count: `12508`

Interpretation: even forcing the historical hidden predicate path does not
materialize all rows counted by the scalar LSI path.

File:

`history/internal_docs/goal4859_au_user_layer_lsi_filter_summary.json`

Result:

- public planar-map LSI count: `13622`
- raw rows: `103843`
- user-layer filtered rows: `12508`

Interpretation: filtering raw rows in Python cannot recover the missing rows,
because the raw row materialization path is not a complete superset of the count
path.

### Correct County x Zipcode Input

File:

`history/internal_docs/goal4859_county_zipcode_correct_input_hidden_predicate_lsi_rows_summary.json`

Result:

- public planar-map LSI count: `961165`
- hidden-predicate row count: `937391`

Interpretation: the same count-vs-row gap appears on the intended first
Section 5.7 pair.

Note: an earlier local run against `/workspace/goal4851_county_zipcode_cdb`
produced a different count because that was the wrong regenerated input source.
The correct Goal4851-proven input source is:

- `/workspace/rayjoin_section57_same_source_cdb/point_cdb/dtl_cnty/dtl_cnty_Point.cdb`
- `/workspace/rayjoin_section57_same_source_cdb/point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb`

## Minimal Real Witness

File:

`history/internal_docs/goal4859_minimal_real_witness_probe_summary.json`

This witness has no CDB dependency. It uses two base segments and one query
segment extracted from the Australia representative case.

Base segments:

```text
id=14110870
(151.2771671, -33.8512399) -> (151.2772023, -33.8513923)

id=14387225
(151.2771671, -33.8512399) -> (151.2772023, -33.8513923)
```

Query segment:

```text
id=640
(151.2776856, -33.8511451) -> (151.2772023, -33.8513923)
```

Result:

- `public_planar_map_lsi_count: 2`
- `hidden_predicate_row_count: 0`
- `count_rows_match: false`

This is the smallest current proof of the row-surface bug.

## Why This Is Not Yet A 5.3/PIP Bug

No PIP or point-location stage is needed to reproduce the current mismatch.

The failure occurs before midpoint construction and before point-location:

`LSI count says two intersections exist; LSI rows return none.`

Therefore the current bug belongs to Section 5.2 row materialization, not
Section 5.3.

## Immediate Next Work

Create the next product/debug goal:

`Goal4860: repair public planar-map LSI row materialization`

Required gates:

1. Add a failing minimal witness regression from
   `goal4859_minimal_real_witness_probe_summary.json`.
2. Fix the public/native row materialization path so planar-map LSI rows match
   the scalar count path on the minimal witness.
3. Re-run the Australia representative pair:
   - count `13622`
   - row count `13622`
4. Re-run the correct County x Zipcode input:
   - count `961165`
   - row count `961165`
5. Only after these gates pass, resume Section 5.7 overlay assembly.

## Non-Authorization

This report does not authorize:

- Section 5.7 correctness completion.
- Section 5.7 performance measurement.
- full eight-pair paper reproduction.
- broad RayJoin or RTDL speed claims.
- treating raw segment-pair rows as planar-map LSI rows.
- moving to PIP/point-location debugging before LSI rows are correct.
