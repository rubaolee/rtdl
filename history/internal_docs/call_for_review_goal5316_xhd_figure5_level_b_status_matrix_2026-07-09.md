# Call For Review - Goal5316 X-HD Figure-5 / Level-B Status Matrix

Please strictly review Goal5316.

## Files To Review

Primary result:

```text
history/internal_docs/goal5316_xhd_figure5_level_b_status_matrix_result_2026-07-09.md
```

Primary artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5316_figure5_level_b_status_matrix.json
```

Tests:

```text
tests/goal5316_xhd_figure5_level_b_status_matrix_test.py
```

Important upstream evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5291_figure5_dragon_happy_candidate_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5298_author_graphics_precheck_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5299_thai_happy_level_b_rtdl_comparison_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5300_thai_asian_level_b_rtdl_comparison_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5305_county_zcta_rtdl_triton_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5307_water_bg_author_rtdl_partner_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5309_full_public_arcgis_probe_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5314_water_bg_corrected_comparison_summary.json
```

## Context

Goal5316 does not implement a new route. It consolidates the current
Figure-5-like X-HD evidence into a status matrix.

The matrix must keep the following boundaries:

```text
Figure 5 reproduced = false
exact paper dataset reproduction = false
full paper reproduction = false
author-vs-RTDL performance ratio authorized = false
```

The purpose is to prevent Level-B / bounded / full-public / exact / performance
denominator evidence from being mixed together.

## Questions For Review

1. Does the matrix correctly preserve the claim boundary that Figure 5 is **not**
   reproduced and exact paper input provenance is still absent?

2. Does `graphics_dragon_happy_full_public` correctly state the strongest
   current graphics evidence as Level-B same-source scalar match, while carrying
   the Goal5211 early-break caveat (`per_source_witness_exact=false`)?

3. Does `graphics_dragon_asian_scaled_author_no_go` correctly block further
   RTDL timing under the current available public/scaled input, because the
   author rerun does not match the paper-log value?

4. Do the Thai graphics rows correctly distinguish exact-witness routes
   (`per_source_witness_exact=true`) from fast-scalar routes
   (`per_source_witness_exact=false`) while still allowing scalar Level-B
   matches?

5. Do `geo_county_zcta_bounded` and `geo_water_bg_bounded` remain correctly
   classified as bounded same-fixture correctness only, without being promoted
   to full-public, exact, representative, Figure-5, or performance evidence?

6. Does `geo_county_zcta_full_public_probe` correctly use the Goal5309 point
   count mismatch to block exact / Figure-5 promotion for the current public
   County source?

7. Does `geo_water_bg_full_public_corrected` correctly apply the Goal5313/5314
   correction: author paper-config denominator is `n_points_cell=8`, RTDL
   reports a float64 witness, the same witness in float32 equals author/paper,
   and the declared RTDL-vs-author numeric boundary is `2e-6`?

8. Is the matrix overclaiming anywhere by turning Level-B same-source or bounded
   evidence into exact paper dataset identity, Figure-5 reproduction, full paper
   reproduction, performance parity, or author RT-core equivalence?

9. Are all `primary_artifacts` sufficient and correctly traceable? Are any
   required upstream artifacts missing from the matrix?

10. Is the next-work framing correct: send Goals5313-5316 for review, then
    choose between input provenance, Figure-5 coverage, denominator-aligned
    performance design, or system extraction?

## Expected Answer Shape

Please answer in this shape:

```text
Verdict:
  approve_goal5316_figure5_level_b_status_matrix
  OR approve_with_required_amendments
  OR revise_goal5316_status_matrix

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
approve_goal5316_xhd_figure5_level_b_status_matrix
```
