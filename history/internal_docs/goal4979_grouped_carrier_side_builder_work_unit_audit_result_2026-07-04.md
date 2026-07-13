# Goal4979 Result: Grouped Carrier Side-Builder Work-Unit Audit

Date: 2026-07-04

## Verdict Requested

`completed_side_builder_mixed_no_single_target`

## Summary

Goal4979 added work-unit metrics to the grouped carrier side-builder after Goal4978 showed that carrier construction is dominated by the Numba side-builder loop.

The result is useful but not a simple win:

- side0 builder remains much slower than side1;
- side0 does **not** scan more original chain points;
- side0 and side1 process the same number of sorted intersection rows;
- concat/cumsum/slice-copy remain negligible;
- the side0 cost is therefore not explained by a simple scalar work count.

This rules out several wrong optimization targets. The next step should be a side-order / locality / first-large-call diagnostic before rewriting the builder.

## Code Changes

Changed only the app-owned reproduction script and tests:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `tests/goal4979_grouped_carrier_side_work_metrics_test.py`

No RTDL core/native code was changed for Goal4979.

New fields in `grouped_carrier`:

- `side_work_metrics.side0`
- `side_work_metrics.side1`
- `side_work_metrics_total`

Recorded work-unit metrics:

- `chain_count`
- `chain_points_scanned`
- `edge_slots_scanned`
- `intersection_run_count`
- `intersection_row_count`
- `intersection_display_point_appends`
- `dedupe_append_calls`
- `split_flush_count`
- `chain_final_flush_count`
- `kept_group_count`
- `skipped_group_count`
- `emitted_point_row_count`
- `sorted_intersection_order_count`
- `run_start_count`

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

Route:

```text
--device-columnar
--compiled-group
--bounded-exact-lsi-device-columns --bounded-exact-lsi-capacity 600000
--point-location-device-face-columns
--fast-scaled-point-pack
```

Artifact:

- `history/internal_docs/goal4979_grouped_carrier_side_work_artifacts_2026-07-04/side_work_summary.json`

## Top-Level Timing

| Metric | Seconds |
|---|---:|
| writer-free hot | 4.140426 |
| downstream floor | 1.512434 |
| carrier total | 0.722812 |
| side0 Numba builder | 0.643152 |
| side1 Numba builder | 0.068494 |

Note: Goal4979 instrumentation increments counters inside the side-builder loop, so the absolute carrier time is slightly higher than Goal4978 (`0.722812s` vs `0.654825s`). The result should be used for work-unit diagnosis, not as a new performance headline.

## Work-Unit Metrics

| Metric | side0 | side1 | side0/side1 |
|---|---:|---:|---:|
| builder time | 0.643152s | 0.068494s | 9.390x |
| chain count | 1,612 | 10,144 | 0.159x |
| chain points scanned | 1,706,639 | 9,993,104 | 0.171x |
| edge slots scanned | 1,705,027 | 9,982,960 | 0.171x |
| intersection run count | 218,763 | 224,381 | 0.975x |
| intersection row count | 428,322 | 428,322 | 1.000x |
| intersection display appends | 856,644 | 856,644 | 1.000x |
| dedupe append calls | 2,563,283 | 10,849,748 | 0.236x |
| split flush count | 428,322 | 428,322 | 1.000x |
| kept group count | 215,786 | 213,188 | 1.012x |
| skipped group count | 214,148 | 225,278 | 0.951x |
| emitted point rows | 1,136,678 | 4,765,884 | 0.239x |

## Derived Rates

| Metric basis | side0 seconds / million | side1 seconds / million |
|---|---:|---:|
| chain points scanned | 0.376853 | 0.006854 |
| edge slots scanned | 0.377209 | 0.006861 |
| intersection runs | 2.939950 | 0.305256 |
| intersection rows | 1.501563 | 0.159912 |
| dedupe append calls | 0.250910 | 0.006313 |
| kept groups | 2.980510 | 0.321283 |
| skipped groups | 3.003308 | 0.304041 |
| emitted point rows | 0.565818 | 0.014372 |

These rates show that side0 is slower per unit across every measured scalar basis. This means the current metrics do not support a simple "more points" or "more groups" explanation.

## Structural Consistency

Compared with Goal4978, these anchors match exactly:

- `lsi_row_count`
- `xsect_sorted_counts`
- `vertex_positive_counts`
- `downstream_consumer`
- `scale_bounds`

`grouped_carrier` differs only because Goal4979 adds `side_work_metrics` and `side_work_metrics_total`.

The route still reports:

- `lsi_row_count = 428322`
- `group_count = 428974`
- `point_row_count = 5902562`
- `skipped_group_count = 439426`

## Interpretation

Goal4979 rules out the easy explanations:

1. **Not original point scan dominated.** side0 scans only 17.1% as many original chain points as side1, yet is 9.39x slower.
2. **Not intersection row count dominated.** side0 and side1 both process 428,322 sorted intersection rows.
3. **Not group count dominated.** kept/skipped group counts are roughly the same.
4. **Not concat/cumsum/slice-copy dominated.** Goal4978 already showed those are milliseconds.

The likely explanations are narrower:

- side0 has much higher intersection density per chain/edge, causing a different branch/locality pattern;
- side0 is the first large side-builder call and may include cache/page/JIT-residual effects not present in side1;
- side0's run layout may create worse memory-access locality even with similar row counts.

This means the next goal should **not** immediately rewrite the carrier. It should first run a side-order/locality diagnostic:

- execute side1 first and side0 second;
- optionally execute side0 twice in one process;
- compare builder time with identical work-unit counts;
- record run-size distribution, max run length, and intersections-per-chain/edge distribution.

If side0 remains slow independent of call order, the target is layout/branch locality. If side0 becomes fast when second, the target is first-large-call/cache or warmup.

## Claim Boundary

Authorized:

- Side-builder cost is not explained by simple point/group counts.
- Carrier concat/cumsum/copy should not be optimized next.
- The next diagnostic should test call-order/locality before algorithm rewrite.

Not authorized:

- No author-performance claim.
- No public high-performance claim.
- No RTDL core promotion of grouped carrier.
- No RayJoin-specific native/core primitive.
- No Layer 4 fusion.

## Exit Label

`completed_side_builder_mixed_no_single_target`
