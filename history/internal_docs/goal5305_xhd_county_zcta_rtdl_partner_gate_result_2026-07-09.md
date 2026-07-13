# Goal5305 - X-HD County-ZCTA RTDL Partner Gate Result

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

Goal5305 runs a RTDL generic partner route on the same bounded ArcGIS
County-ZCTA WKT fixture that Goal5304 ran through the author `hd_exec`
binary. The RTDL route matches the author `HDResult` within the declared
`1e-5` tolerance.

This closes the first same-fixture author/RTDL scalar comparison for a
Census/TIGER-like 2D WKT workload. It does not close exact paper input
provenance, Figure 5 reproduction, author RT-core algorithm equivalence, or
performance parity.

## Inputs

The input files are the Goal5303 bounded ArcGIS County-ZCTA WKT artifacts:

```text
Paper-reproduction-apps/x-hd-paper/data/generated/goal5303_arcgis_county_zcta_bounded/dtl_cnty_arcgis_bounded.wkt
Paper-reproduction-apps/x-hd-paper/data/generated/goal5303_arcgis_county_zcta_bounded/uszipcode_arcgis_bounded.wkt
```

The POD run used the copies already uploaded for Goal5304:

```text
/tmp/xhd_goal5304/data/dtl_cnty_arcgis_bounded.wkt
/tmp/xhd_goal5304/data/uszipcode_arcgis_bounded.wkt
/tmp/xhd_goal5304/out/author_county_zcta_arcgis_bounded.json
```

Observed point counts:

```text
input1: 38,034
input2: 50,272
logical pair count: 1,912,045,248
```

The WKT loader used by RTDL was extended in the app layer to match the author
loader semantics needed by this fixture:

- `POINT`: one coordinate;
- `LINESTRING`: all vertices;
- `MULTILINESTRING`: all vertices in every line string;
- `POLYGON`: outer ring only, including the closing vertex;
- `MULTIPOLYGON`: outer ring of every polygon, including closing vertices;
- holes are ignored for this author-compatible point-stream contract.

## RTDL Route

The successful RTDL run used the existing generic partner surface:

```text
rt.point_rows_to_partner_columns(..., partner="triton")
rt.directed_max_of_nearest_distance_2d_partner_columns(
    ...,
    partner="triton",
    triton_strategy="dense_point_nearest_tiled",
)
```

This is a generic directed max-of-nearest-distance route. It is not an
X-HD-specific RTDL primitive and it is not the author X-HD RT-core algorithm.

The first attempt used the existing generic Numba block-nearest route:

```text
partner="numba"
numba_strategy="block_nearest_rows"
```

That attempt failed on the current POD because Numba generated PTX 8.7 while
the available driver/JIT path accepted PTX only up to 8.4:

```text
CUDA_ERROR_UNSUPPORTED_PTX_VERSION
ptxas ... Unsupported .version 8.7; current version is '8.4'
```

This is recorded as an environment/toolchain no-go for this POD, not as an
algorithmic mismatch. Triton 3.4.0 and Torch 2.8.0+cu128 were present and the
generic Triton tiled route ran successfully.

## Evidence

Primary POD summary:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5305_county_zcta_rtdl_triton_summary_pod.json
```

Key fields:

```json
{
  "schema": "rtdl.paper_reproduction.xhd.goal5305.county_zcta_rtdl_partner_gate.v2",
  "author": {
    "HDResult": 65.44752502441406,
    "abs_diff": 5.2616073986655465e-06,
    "matched": true,
    "tolerance": 1e-05
  },
  "rtdl": {
    "HDResult": 65.44751976280666,
    "partner": "triton",
    "triton_strategy": "dense_point_nearest_tiled",
    "route": "directed_max_of_nearest_distance_2d_partner_columns",
    "partner_reference_contract": "generic_directed_max_of_nearest_distance_2d",
    "native_engine_row_contract": "not_called_partner_reference_only",
    "per_source_witness_exact": true
  }
}
```

The author/RTDL absolute difference is about `5.26e-6`, within the declared
`1e-5` tolerance. The tolerance is needed because the author result is emitted
through the author C++/CUDA/JSON path while the RTDL partner route computes the
generic exact value through a different floating-point implementation.

## Timing

Observed POD phases from the summary:

```text
load_input_sec:            0.654s
partner_column_upload_sec: 1.764s
rtdl_route_sec:            1.441s
total_sec:                 3.859s
```

These timings are included for transparency only. No performance ratio is
claimed because the denominators are not aligned:

- author `Running.AvgTime` is an internal author phase;
- RTDL `rtdl_route_sec` is a partner route wall phase;
- RTDL total includes app-owned WKT loading and partner-column upload;
- the RTDL route is a generic partner reference route, not the author X-HD
  RT-core algorithm.

## Claim Boundary

Authorized:

```text
Level-B bounded same-fixture scalar correctness for the Goal5303/Goal5304
ArcGIS County-ZCTA WKT fixture.
```

Not authorized:

```text
exact paper dataset reproduction
Figure 5 reproduction
author X-HD RT-core algorithm equivalence
author performance parity
performance ratio
full paper reproduction
```

The fixture remains geographically bounded and not representative: the first
County rows are Alabama counties while the first ZIP/ZCTA rows are Alaska
ZCTAs. This is still a useful ingestion/correctness stress case because it
uses larger polygon/multipolygon WKT streams with author-compatible outer-ring
semantics.

## Tests

Local tests run:

```text
py -m unittest \
  tests.goal5305_xhd_wkt_author_loader_semantics_test \
  tests.goal5305_xhd_county_zcta_rtdl_partner_gate_test \
  tests.goal5303_xhd_county_zcta_arcgis_bounded_fixture_test \
  tests.goal5304_xhd_county_zcta_author_ingestion_test
```

Result:

```text
Ran 14 tests in 1.508s
OK
```

The tests cover:

- WKT geometry point-stream semantics, including polygon outer rings and
  multipolygon outer rings;
- fixture point counts matching the manifest estimates;
- author/RTDL `HDResult` match within tolerance;
- the generic partner route contract;
- forbidden performance / exact-paper / RT-core claims remaining false.

## Next Recommended Work

1. Send Goals5302-5305 as a combined Census/TIGER-like Level-B packet for
   external review.
2. If approved, decide whether to build a better geographically matched
   County-ZCTA sample, or move to the next Figure-5 pair
   (`USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt`).
3. Do not claim performance ratio until an explicitly aligned author/RTDL
   phase boundary exists.
