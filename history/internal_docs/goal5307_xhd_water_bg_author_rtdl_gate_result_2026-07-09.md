# Goal5307 - X-HD WaterBodies -> BlockGroups Author/RTDL Gate Result

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

Goal5307 runs both author `hd_exec` and RTDL on the Goal5306 bounded
WaterBodies -> BlockGroups WKT fixture.

The RTDL generic partner route matches the author `HDResult` within the
declared `1e-5` tolerance:

```text
author HDResult = 72.38665008544922
RTDL HDResult   = 72.38664516014835
abs_diff        = 4.925300871150284e-06
tolerance       = 1e-5
matched         = true
```

This is Level-B bounded same-fixture scalar correctness only. It is not exact
paper input recovery, not Figure 5 reproduction, not author X-HD RT-core
algorithm equivalence, and not a performance-ratio denominator.

## Inputs

The input files are the Goal5306 bounded ArcGIS WaterBodies/BlockGroups WKT
artifacts:

```text
Paper-reproduction-apps/x-hd-paper/data/generated/goal5306_arcgis_water_bg_bounded/USADetailedWaterBodies_arcgis_bounded.wkt
Paper-reproduction-apps/x-hd-paper/data/generated/goal5306_arcgis_water_bg_bounded/USACensusBlockGroupBoundaries_arcgis_bounded.wkt
```

POD copies:

```text
/tmp/xhd_goal5306/data/USADetailedWaterBodies_arcgis_bounded.wkt
/tmp/xhd_goal5306/data/USACensusBlockGroupBoundaries_arcgis_bounded.wkt
```

Observed point counts:

```text
input1 / WaterBodies: 124
input2 / BlockGroups: 894
```

## Author Run

Author binary:

```text
/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec
```

Author command:

```text
/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  -input1 /tmp/xhd_goal5306/data/USADetailedWaterBodies_arcgis_bounded.wkt \
  -input2 /tmp/xhd_goal5306/data/USACensusBlockGroupBoundaries_arcgis_bounded.wkt \
  -input_type wkt \
  -n_dims 2 \
  -variant rt \
  -execution gpu \
  -normalize=false \
  -json /tmp/xhd_goal5306/out/author_water_bg_arcgis_bounded.json \
  -overwrite=true \
  -check=false
```

Author evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/goal5307_raw/author_water_bg_arcgis_bounded.json
Paper-reproduction-apps/x-hd-paper/results/goal5307_raw/author_stdout.txt
Paper-reproduction-apps/x-hd-paper/results/goal5307_raw/author_stderr.txt
```

Key author fields:

```text
HDResult = 72.38665008544922
Running.AvgTime = 4.209 ms
GridResolution = [1, 1]
LargeCells = 1
Iterations = 2
```

## RTDL Route

The successful RTDL run uses the existing generic partner route:

```text
rt.point_rows_to_partner_columns(..., partner="triton")
rt.directed_max_of_nearest_distance_2d_partner_columns(
    ...,
    partner="triton",
    triton_strategy="dense_point_nearest_tiled",
)
```

Evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5307_water_bg_author_rtdl_partner_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/goal5307_raw/rtdl_water_bg_arcgis_bounded_triton_summary_raw_goal5305_runner.json
```

The raw RTDL run reuses the Goal5305 generic partner runner. Goal5307 wraps that
raw summary into a pair-specific summary so the primary artifact has correct
Goal5307 and WaterBodies/BlockGroups labels.

Key RTDL fields:

```text
HDResult = 72.38664516014835
route = directed_max_of_nearest_distance_2d_partner_columns
partner = triton
triton_strategy = dense_point_nearest_tiled
partner_reference_contract = generic_directed_max_of_nearest_distance_2d
native_engine_row_contract = not_called_partner_reference_only
per_source_witness_exact = true
```

## Timing

Observed POD phases from the RTDL summary:

```text
rtdl_load_input_sec = 0.006s
rtdl_partner_column_upload_sec = 1.528s
rtdl_route_sec = 1.305s
rtdl_total_sec = 2.839s
```

Author internal timing:

```text
Running.AvgTime = 4.209 ms
```

These numbers are not denominator-aligned. No performance ratio is claimed:

- author `Running.AvgTime` is an internal author phase;
- RTDL route wall is a generic partner reference route phase;
- RTDL total includes app-owned loading and partner-column upload;
- the RTDL route is not the author X-HD RT-core algorithm.

## Claim Boundary

Authorized:

```text
Level-B bounded same-fixture scalar correctness for the Goal5306
WaterBodies->BlockGroups WKT fixture.
```

Not authorized:

```text
exact paper dataset reproduction
geo Figure 5 reproduction
author X-HD RT-core algorithm equivalence
author performance parity
performance ratio
full paper reproduction
```

The fixture remains geographically bounded and not representative: the first
WaterBodies OBJECTIDs are in/near Hawaii, while the first BlockGroup OBJECTIDs
are in Alabama. It is a useful ingestion/correctness stress case, not a
paper-distribution sample.

## Tests

Local tests run:

```text
py -m unittest \
  tests.goal5306_xhd_water_bg_arcgis_bounded_fixture_test \
  tests.goal5307_xhd_water_bg_author_rtdl_gate_test \
  tests.goal5305_xhd_wkt_author_loader_semantics_test
```

Result:

```text
Ran 11 tests in 1.489s
OK
```

The tests cover:

- Goal5306 source/fixture manifest;
- author/RTDL `HDResult` match within tolerance;
- raw author and RTDL provenance files;
- generic partner route contract;
- forbidden exact-paper / Figure 5 / RT-core / performance claims remaining
  false.

## Next Recommended Work

1. Send Goals5306-5307 as a WaterBodies/BlockGroups bounded packet for review.
2. Combine Goals5302-5307 into a geo Level-B status packet: both X-HD Figure-5
   WKT pairs now have bounded author/RTDL scalar matches.
3. Do not claim Figure 5 reproduction unless exact paper input provenance or a
   defensible full-public same-source reconstruction is separately established.
