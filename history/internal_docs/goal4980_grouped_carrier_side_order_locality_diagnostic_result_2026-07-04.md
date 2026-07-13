# Goal4980 Result: Grouped Carrier Side-Order / Locality Diagnostic

Date: 2026-07-04

## Verdict Requested

`completed_side_order_locality_diagnostic__reverse_order_wins`

## Summary

Goal4979 showed that side0 builder time was not explained by simple work-unit counts. Goal4980 tested whether the slow side0 timing was data-inherent or order/cache/locality related.

The result is decisive:

```text
side order 0,1: side0 builder = 0.692401s, carrier = 0.773479s
side order 1,0: side0 builder = 0.019657s, carrier = 0.104935s
```

Reversing the side-builder order keeps structural results identical while reducing carrier construction by about 0.6685s on the top4 representative route.

This means the prior side0 cost is not an inherent side0 work-volume cost. It is an order/locality/cache effect exposed by running side0 first.

## Code Changes

Changed only the app-owned paper-reproduction script and tests:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `tests/goal4979_grouped_carrier_side_work_metrics_test.py`

No RTDL core/native files were changed.

Added diagnostic CLI:

```text
--compiled-group-side-order 0,1
--compiled-group-side-order 1,0
```

Allowed values are only `0,1` and `1,0`.

The default remains `0,1`; Goal4980 measures the reversed diagnostic route but does not yet make it the default.

## Local Validation

Commands:

```text
py -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
$env:PYTHONPATH='src'; py -m unittest tests.goal4979_grouped_carrier_side_work_metrics_test tests.goal4978_grouped_carrier_decomposition_test tests.goal4977_fast_scaled_point_pack_test
```

Result:

```text
Ran 7 tests in 0.003s
OK
```

## POD Evidence

POD:

- `root@213.173.108.6 -p 10626`

Input:

- left: `Paper-reproduction-apps/rayjoin-paper/_data/goal4971_top4_arcgis/top4_county.cdb`
- right: `Paper-reproduction-apps/rayjoin-paper/_data/goal4971_top4_arcgis/top4_zipcode.cdb`

Common route:

```text
--device-columnar
--compiled-group
--bounded-exact-lsi-device-columns --bounded-exact-lsi-capacity 600000
--point-location-device-face-columns
--fast-scaled-point-pack
```

Artifacts:

- `history/internal_docs/goal4980_grouped_carrier_side_order_artifacts_2026-07-04/side_order_0_1_summary.json`
- `history/internal_docs/goal4980_grouped_carrier_side_order_artifacts_2026-07-04/side_order_1_0_summary.json`

## Timing Comparison

| Metric | side order `0,1` | side order `1,0` | Change |
|---|---:|---:|---:|
| writer-free hot | 4.251859s | 3.526743s | -0.725116s |
| downstream floor | 1.579240s | 0.903088s | -0.676152s |
| carrier total | 0.773479s | 0.104935s | -0.668544s |
| side0 builder | 0.692401s | 0.019657s | -0.672744s |
| side1 builder | 0.069559s | 0.073979s | +0.004420s |
| LSI phase | 2.669020s | 2.620071s | -0.048949s |
| vertex PIP side0-in-side1 | 0.058653s | 0.058867s | +0.000214s |
| vertex PIP side1-in-side0 | 0.336261s | 0.322014s | -0.014247s |

The carrier construction improvement almost entirely comes from side0 builder time:

```text
side0 builder: 0.692401s -> 0.019657s
carrier total: 0.773479s -> 0.104935s
```

## Structural Consistency

These anchors match exactly between `0,1` and `1,0`:

- `lsi_row_count`
- `xsect_sorted_counts`
- `vertex_positive_counts`
- `downstream_consumer`
- `scale_bounds`
- grouped carrier `group_count`
- grouped carrier `point_row_count`
- grouped carrier `skipped_group_count`

Values:

```text
lsi_row_count = 428322
group_count = 428974
point_row_count = 5902562
skipped_group_count = 439426
```

The group order changes when side order is reversed, but the binary descriptor consumer result is identical. This is acceptable for the current writer-free binary descriptor route, whose consumer aggregates descriptor pairs and does not require a paper-text output-chain ordering.

## Interpretation

Goal4979 showed:

- side0 scans fewer original points than side1;
- side0 and side1 process the same number of intersection rows;
- kept/skipped group counts are similar;
- yet side0 first was much slower.

Goal4980 shows that when side1 runs first, side0 becomes fast:

```text
side0 first: 0.692401s
side0 second: 0.019657s
```

Therefore the side0 cost is not data-inherent. It is an order/locality/cache effect. The most likely causes are:

- cold access to shared display/intersection arrays when side0's dense intersection pattern runs first;
- memory/page/cache effects in the first carrier side-builder pass;
- branch/locality behavior triggered by side0's high intersection density per original edge, which becomes cheap after side1 has warmed shared arrays.

This also explains why simple work-unit counts in Goal4979 could not predict the cost.

## Product Meaning

For the writer-free binary descriptor route, reversing carrier side order is a valid app-owned optimization candidate:

- it does not change LSI/PIP semantics;
- it does not change grouped counts or downstream descriptor-pair results;
- it does not require RTDL core/native changes;
- it is not a RayJoin-specific RTDL primitive.

However, it should not be silently promoted yet. It should be made explicit as a route policy:

```text
For binary descriptor consumers, build the larger/right side first to warm shared intersection/display arrays before the dense left-side group build.
```

The paper-text output route may still require original ordering. This optimization is currently authorized only for the writer-free binary descriptor route.

## Next Goal Direction

Goal4981 should promote the reversed side order for the binary descriptor route only, with a fail-closed check:

1. Default binary descriptor route uses `--compiled-group-side-order 1,0` or an explicit policy equivalent.
2. Validate grouped counts and downstream descriptor consumer against `0,1`.
3. Keep paper-text route separate.
4. Report the new top4 writer-free hot number and downstream floor.

Expected result, based on Goal4980:

```text
writer-free hot ~= 3.53s
downstream floor ~= 0.90s
carrier total ~= 0.10s
```

## Claim Boundary

Authorized:

- Reversing carrier side-builder order materially reduces the writer-free binary descriptor route on top4.
- The speedup is route-local and app-owned.
- Structural descriptor-consumer anchors remain identical.

Not authorized:

- No paper byte-equality claim for reversed-order binary route.
- No public high-performance claim.
- No author-performance headline.
- No RTDL core promotion.
- No RayJoin-specific core/native primitive.
- No Layer 4 fusion.

## Exit Label

`completed_side_order_locality_diagnostic__reverse_order_wins`
