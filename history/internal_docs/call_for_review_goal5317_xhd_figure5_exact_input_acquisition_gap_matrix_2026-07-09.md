# Call For Review - Goal5317 X-HD Figure-5 Exact-Input Acquisition Gap Matrix

Please strictly review Goal5317.

## Files To Review

Result:

```text
history/internal_docs/goal5317_xhd_figure5_exact_input_acquisition_gap_matrix_result_2026-07-09.md
```

Primary artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5317_figure5_exact_input_acquisition_gap_matrix.json
```

Tests:

```text
tests/goal5317_xhd_figure5_exact_input_gap_matrix_test.py
```

Upstream evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_log_mapping_goal5177_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5267_full_paper_coverage_gap_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5288_figure5_timing_denominator_audit_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5297_dataset_acquisition_manifest_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5309_full_public_arcgis_probe_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5316_figure5_level_b_status_matrix.json
```

## Context

Goal5316 consolidated the current Figure-5-like evidence and kept the claim
boundary closed:

```text
Figure 5 reproduction complete = false
exact paper dataset reproduction complete = false
author-vs-RTDL performance ratio authorized = false
```

Goal5317 chooses the next bottleneck: exact paper input provenance. It does not
run new author/RTDL code. It creates a row-level acquisition gap matrix for:

```text
BraTS2020_ValidationData
Stanford graphics
County -> ZCTA
WaterBodies -> BlockGroups
OSM Lakes/Parks/AllNodes
```

## Main Claim Under Review

Goal5317 recommends:

```text
Goal5318 = WaterBodies/BG exact-provenance search before any new performance work
```

Reason:

```text
WaterBodies/BG is the closest current geo candidate:
  - paper-like MBRs;
  - tiny point-count deltas compared with paper logs;
  - author paper-config n_points_cell=8 reproduces paper-log HDResult exactly;
  - RTDL exact-witness float64 matches author/paper float32 within 2e-6.
```

But Goal5317 must **not** claim exact WKT recovery, Figure-5 completion, or
performance parity.

## Questions For Review

1. Is the exact dataset rule strong enough? Specifically, does it correctly
   say that matching point counts, MBRs, Gini/statistics, HDResult, or path names
   is not sufficient for Level-C exact paper input status?

2. Does the BraTS row correctly classify the blocker as access / exact image
   list / conversion provenance, rather than as an RTDL route-code problem?

3. Does the Stanford graphics row correctly keep the current evidence at
   Level-B public same-source, even for value-matched pairs?

4. Does the Stanford graphics row correctly keep current Dragon->Asian scaled
   as no-go under the available mapping?

5. Does the County->ZCTA row correctly block route/performance work because the
   current public County source has a +32.2% point-count mismatch?

6. Does the WaterBodies->BlockGroups row correctly identify it as the strongest
   current geo exact-provenance search target while still refusing exact/Figure-5
   promotion?

7. Does the OSM row correctly defer Lakes/Parks/AllNodes until snapshot,
   filter, and conversion provenance exists?

8. Is the ranked next-action list correct, or should another row outrank
   WaterBodies/BG for exact-input search?

9. Does the recommended Goal5318 scope avoid unnecessary POD reruns and focus
   on provenance search first?

10. Does Goal5317 overclaim anywhere by turning Level-B / full-public /
    bounded evidence into exact paper input identity?

## Expected Answer Shape

Please answer in this shape:

```text
Verdict:
  approve_goal5317_xhd_figure5_exact_input_acquisition_gap_matrix
  OR approve_with_required_amendments
  OR revise_goal5317_exact_input_gap_matrix

Blocking findings:
  - ...

Required amendments:
  - ...

Non-blocking notes:
  - ...

Answers to the 10 review questions:
  1. ...
  ...
  10. ...
```

## Requested Verdict Label If Approved

```text
approve_goal5317_xhd_figure5_exact_input_acquisition_gap_matrix
```
