# Goal4860 Result: Public Planar-Map LSI Row Materialization Repair

Date: 2026-07-02

## Verdict

Goal4860 is ready for external review.

The bug exposed while entering Section 5.7 has been sent back to the correct
single-stage owner: **Section 5.2 LSI row materialization**.

It is not a Section 5.3/PIP bug.  PIP remains a later gate.

## What Was Broken

Before this goal:

- the public planar-map LSI scalar count path returned the expected counts;
- the public/raw row path did not materialize the same intersection set;
- a minimal witness returned `count=2` but `rows=0`;
- Australia Lakes x Parks and County x Zipcode also showed row-count gaps.

That meant Section 5.7 could not honestly proceed, because overlay construction
requires actual LSI rows and coordinates, not only a scalar count.

## Repair

The repair makes the row route use the same planar-map LSI predicate contract
as the scalar count route.

Key implementation points:

- Added an explicit native row-materialization ABI for
  `prepared_left_grouped_range_direct_intersection_with_predicate_mode`.
- Added `PreparedOptixPlanarMapLsi2D.run_raw()` / `run()` to expose public
  LSI rows through `prepare_planar_map_lsi_2d_optix`.
- Row materialization now derives pair ids from the same grouped-range direct
  predicate source used by the count path.
- Added materialized intersection-point fallback logic for endpoint, tolerant
  endpoint-on-segment, and near-collinear overlap cases accepted by the
  planar-map LSI predicate.

Touched implementation files:

- `src/rtdsl/optix_runtime.py`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`

Focused regression test:

- `tests/goal4860_planar_map_lsi_row_materialization_test.py`

Evidence/gate scripts:

- `history/internal_docs/goal4860_lsi_row_gate.py`
- `history/internal_docs/goal4860_lsi_row_pair_diff_probe.py`
- `history/internal_docs/goal4860_lsi_missing_pair_geometry_probe.py`

## Focused Tests

POD command:

```text
cd /workspace/rtdl_goal4859_exec &&
timeout 90s env PYTHONPATH=src RTDL_OPTIX_LIB=/workspace/rtdl_goal4859_exec/build/librtdl_optix.so \
  python3 -m unittest tests.goal4860_planar_map_lsi_row_materialization_test -v
```

Result:

```text
Ran 5 tests in 5.501s
OK
```

Covered cases:

- minimal real witness: `count == rows == 2`;
- endpoint tolerance witness;
- near-collinear shared endpoint witness;
- endpoint-on-segment interior witness;
- near-collinear overlap representative witness.

## Non-Toy Gates

### County x Zipcode

Inputs:

- base:
  `/workspace/rayjoin_section57_same_source_cdb/point_cdb/dtl_cnty/dtl_cnty_Point.cdb`
- query:
  `/workspace/rayjoin_section57_same_source_cdb/point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb`

Evidence file:

- `history/internal_docs/goal4860_county_zipcode_lsi_row_gate_summary.json`

Result:

| field | value |
| --- | ---: |
| expected | 961165 |
| planar_map_lsi_count | 961165 |
| planar_map_lsi_row_count | 961165 |
| count_equals_expected | true |
| rows_equal_count | true |
| rows_equal_expected | true |

### Australia Lakes x Parks Representative

Inputs:

- base:
  `/workspace/goal4848_rep/current_osm_au/lakes_Australia_current_osm_Point.cdb`
- query:
  `/workspace/goal4848_rep/current_osm_au/parks_Australia_current_osm_Point.cdb`

Evidence file:

- `history/internal_docs/goal4860_au_lsi_row_gate_summary.json`

Result:

| field | value |
| --- | ---: |
| expected | 13622 |
| planar_map_lsi_count | 13622 |
| planar_map_lsi_row_count | 13622 |
| count_equals_expected | true |
| rows_equal_count | true |
| rows_equal_expected | true |

## Claim Boundary

Authorized by this result:

- Section 5.2 LSI row-materialization gate is repaired for the tested public
  planar-map LSI primitive path.
- Public `prepare_planar_map_lsi_2d_optix(...).count(...)` and
  `.run_raw(...)` now share the same LSI predicate contract on the tested cases.
- Section 5.7 may resume from correct LSI rows after review.

Not authorized:

- Section 5.3/PIP correctness claim;
- Section 5.7 overlay correctness claim;
- Section 5.7 performance claim;
- broad RayJoin paper-reproduction claim;
- broad RTDL performance claim.

## Answer To The User's Question

Yes, this bug can and should be sent back to the single-stage tests.

The current bug belongs to **5.2 LSI row materialization** because the scalar LSI
count worked while the row surface missed intersections.  It should not be
blamed on 5.3/PIP until the LSI row gate is clean.

After Goal4860, the 5.2 LSI row gate is clean on:

- focused synthetic witnesses;
- Australia representative pair;
- County x Zipcode large pair.

The next stage is to re-enter Section 5.7 from these repaired LSI rows, while
keeping 5.3/PIP as its own explicit gate.
