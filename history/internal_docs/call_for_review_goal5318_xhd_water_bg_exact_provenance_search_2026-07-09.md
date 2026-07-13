# Call For Review - Goal5318 X-HD WaterBodies/BG Exact-Provenance Search

Please strictly review Goal5318.

## Files Under Review

Primary result:

```text
history/internal_docs/goal5318_xhd_water_bg_exact_provenance_search_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5318_water_bg_exact_provenance_search.json
tests/goal5318_xhd_water_bg_exact_provenance_search_test.py
```

Context dependencies:

```text
Paper-reproduction-apps/x-hd-paper/data/generated/goal5310_water_bg_full_public_wkt_candidate/manifest.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5314_water_bg_corrected_comparison_summary.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5317_figure5_exact_input_acquisition_gap_matrix.json
history/internal_docs/goal5317_xhd_figure5_exact_input_acquisition_gap_matrix_result_2026-07-09.md
```

## Requested Review Focus

This is a provenance search, not a route/performance goal.

Please attack especially:

1. Whether Goal5318 correctly refuses to promote WaterBodies/BG to exact paper
   input status.
2. Whether the ArcGIS service/item metadata is useful same-source evidence but
   not enough for exact WKT provenance.
3. Whether the small point-count deltas and value match are correctly treated
   as Level-B support rather than exact dataset proof.
4. Whether prior RayJoin CDB assets are correctly classified as related but not
   X-HD WKT provenance.
5. Whether the test suite locks the negative claim boundary strongly enough.

## Expected Answer Shape

Please answer in this shape:

```text
Verdict:
  approve_goal5318_water_bg_exact_provenance_not_found_keep_level_b
  OR revise_goal5318_...
  OR block_goal5318_...

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Review questions:
  1. Does the artifact preserve the strong Level-B WaterBodies/BG evidence
     without overstating it as exact paper input recovery?
  2. Does the exact dataset rule correctly require author files/hashes,
     byte-identical deterministic regeneration, or external equivalence
     acceptance?
  3. Are current WKT hashes and point deltas carried forward correctly?
  4. Is ArcGIS metadata interpreted correctly: same-source support, not exact
     author byte provenance?
  5. Is the linked WaterBodies layer package item useful provenance context but
     still insufficient for author WKT identity?
  6. Are BlockGroups update/vintage fields correctly treated as a reason not to
     claim a frozen exact author snapshot?
  7. Are prior RayJoin CDB assets correctly kept out of X-HD exact-WKT evidence?
  8. Is the decision label
     `water_bg_exact_provenance_not_found_keep_level_b` justified?
  9. Does the test file check both the positive evidence and the negative
     exact-claim boundary?
  10. Should the next work remain external provenance / dataset acquisition
      rather than more WaterBodies/BG performance runs?
```

## Claim Boundary To Preserve

Allowed:

```text
WaterBodies/BG remains the strongest current geo Level-B candidate.
ArcGIS metadata supports same-source/public-source provenance discussion.
Author paper-config n_points_cell=8 reproduces paper-log scalar.
RTDL exact-witness float64 agrees with author/paper float32 within 2e-6.
```

Forbidden:

```text
WaterBodies/BG exact paper WKT files were recovered.
Current ArcGIS public services are proven byte-identical to author HDDatasets WKT inputs.
Figure 5 geo is reproduced.
Author-vs-RTDL performance ratio is authorized.
Matching HDResult/counts/MBRs proves exact dataset identity.
```

## Requested Verdict Label

If approved, please use:

```text
approve_goal5318_water_bg_exact_provenance_not_found_keep_level_b
```
