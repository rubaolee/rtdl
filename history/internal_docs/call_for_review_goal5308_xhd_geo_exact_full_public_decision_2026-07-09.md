# Call for Review - Goal5308 X-HD Geo Exact / Full-Public Decision

Please strictly review Goal5308.

## Files to Review

```text
history/internal_docs/goal5308_xhd_geo_exact_full_public_decision_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5308_geo_exact_full_public_decision_2026-07-09.json
tests/goal5308_xhd_geo_exact_full_public_decision_test.py
history/internal_docs/xhd_geo_level_b_bounded_packet_goals5302_5307_2026-07-09.md
history/internal_docs/goal5303_xhd_county_zcta_arcgis_bounded_fixture_result_2026-07-09.md
history/internal_docs/goal5305_xhd_county_zcta_rtdl_partner_gate_result_2026-07-09.md
history/internal_docs/goal5306_xhd_water_bg_arcgis_bounded_fixture_result_2026-07-09.md
history/internal_docs/goal5307_xhd_water_bg_author_rtdl_gate_result_2026-07-09.md
```

## Context

Goals5302-5307 create bounded author/RTDL scalar correctness evidence for both
X-HD Figure-5 WKT pair names:

```text
dtl_cnty.wkt -> uszipcode.wkt
USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt
```

Goal5308 is the decision gate that prevents those bounded results from being
overstated as exact paper input or Figure-5 reproduction.

Key facts from the Goal5308 JSON:

```text
Exact author WKT paths are known from logs but not available locally or on POD.

Paper County-ZCTA point counts:
  9,438,045 / 43,952,878
Bounded County-ZCTA point counts:
  38,034 / 50,272

Paper WaterBodies-BG point counts:
  22,818,694 / 52,271,340
Bounded WaterBodies-BG point counts:
  124 / 894
```

Goal5308 therefore keeps Figure-5/full-paper claims blocked and authorizes only
a next full-public ArcGIS point-count / MBR probe.

## Review Questions

1. Does Goal5308 correctly preserve the distinction between bounded Level-B
   scalar correctness and exact/Figure-5 reproduction?
2. Does the evidence support the statement that exact paper WKT files are still
   unavailable on the current local/POD state?
3. Are the paper-log point counts and HDResults correctly extracted for the two
   geo WKT pair names?
4. Does the report make clear that the bounded fixtures are much smaller and
   not representative?
5. Is `level_c_exact_paper_geo_reproduction_blocked = true` the correct
   decision?
6. Is the next authorized goal
   `full_public_arcgis_point_count_mbr_probe_before_any_figure5_claim`
   correctly chosen?
7. Does the report avoid unauthorized claims: exact paper input recovery,
   Figure 5 reproduction, performance ratio, and full paper reproduction?
8. Should Goals5302-5307 now be reviewed as a bounded geo packet, while
   Goal5309 handles full-public source/provenance probing separately?

## Expected Verdict Labels

```text
approve_goal5308_geo_exact_full_public_decision__bounded_not_figure5
revise_goal5308_due_to_missing_or_inaccurate_paper_log_provenance
block_goal5308_due_to_bounded_to_figure5_overclaim
```
