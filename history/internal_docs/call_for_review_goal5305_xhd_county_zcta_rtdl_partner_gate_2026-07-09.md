# Call for Review - Goal5305 X-HD County-ZCTA RTDL Partner Gate

Please strictly review Goal5305.

## Files to Review

```text
history/internal_docs/goal5305_xhd_county_zcta_rtdl_partner_gate_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5305_county_zcta_rtdl_triton_summary_pod.json
Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5305_county_zcta_rtdl_numba_gate.py
tests/goal5305_xhd_wkt_author_loader_semantics_test.py
tests/goal5305_xhd_county_zcta_rtdl_partner_gate_test.py
history/internal_docs/goal5303_xhd_county_zcta_arcgis_bounded_fixture_result_2026-07-09.md
history/internal_docs/goal5304_xhd_county_zcta_author_ingestion_result_2026-07-09.md
```

## Context

Goal5303 created a bounded ArcGIS County-ZCTA WKT fixture. Goal5304 ran author
`hd_exec` on that same fixture and produced:

```text
author HDResult = 65.44752502441406
point counts     = 38,034 / 50,272
```

Goal5305 extends the X-HD app-owned WKT loader to support the author-compatible
point-stream semantics needed by polygonal WKT, then runs RTDL's existing
generic partner route on the same fixture:

```text
directed_max_of_nearest_distance_2d_partner_columns
partner="triton"
triton_strategy="dense_point_nearest_tiled"
```

The POD evidence reports:

```text
RTDL HDResult = 65.44751976280666
abs_diff      = 5.2616073986655465e-06
tolerance     = 1e-5
matched       = true
```

## Review Questions

1. Does the app-owned WKT loader extension correctly implement the author-style
   point stream for the geometries used here: point, line string, multi-line
   string, polygon outer ring, and multipolygon outer rings?
2. Do the tests adequately pin the important WKT semantics, including polygon
   outer rings, ignored holes, preserved closing vertices, and fixture point
   counts?
3. Does the Goal5305 POD summary genuinely compare RTDL against the Goal5304
   author JSON on the same bounded WKT fixture?
4. Is the author/RTDL match (`abs_diff ~= 5.26e-6 <= 1e-5`) sufficient for this
   bounded same-fixture scalar correctness gate?
5. Is the RTDL route properly characterized as a generic partner reference
   route rather than the author X-HD RT-core algorithm?
6. Is it acceptable that the first Numba attempt is recorded as a POD
   PTX/toolchain no-go and that the successful route uses the existing generic
   Triton tiled partner route?
7. Does the result avoid unauthorized claims: exact paper dataset recovery,
   Figure 5 reproduction, author RT-core equivalence, performance parity,
   performance ratio, and full paper reproduction?
8. Are the phase timings presented only as transparency and not as a
   denominator-aligned performance comparison?
9. Is the fixture limitation stated clearly enough: bounded ArcGIS fixture,
   not exact paper input, not geographically representative because the first
   County rows and first ZCTA rows are not geographically paired?
10. Can Goal5305 be marked `implemented_review_pending` and sent together with
    Goals5302-5304 as the first Census/TIGER-like Level-B author/RTDL
    correctness packet?

## Expected Verdict Labels

```text
approve_goal5305_county_zcta_rtdl_partner_gate__level_b_bounded_match
revise_goal5305_wkt_semantics_or_claim_boundary
block_goal5305_due_to_invalid_author_rtdl_comparison_or_overclaim
```
