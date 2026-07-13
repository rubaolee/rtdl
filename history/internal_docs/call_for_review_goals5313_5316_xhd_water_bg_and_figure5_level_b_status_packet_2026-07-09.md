# Call For Review - Goals5313-5316 X-HD WaterBodies/BG Correction And Figure-5 Level-B Status Packet

Please strictly review Goals5313-5316 as one packet.

This packet is intentionally a claim-boundary / denominator review. It should
be attacked for overclaiming, hidden denominator drift, Level-B-to-exact
promotion, warm/fresh confusion, and performance-ratio leakage.

## Files To Review

### Goal5313 - WaterBodies/BG Author Config Alignment

```text
history/internal_docs/goal5313_xhd_water_bg_author_config_alignment_result_2026-07-09.md
history/internal_docs/call_for_review_goal5313_xhd_water_bg_author_config_alignment_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_author_water_bg_full_public_n_points_cell_8.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_water_bg_n_points_cell_alignment_summary.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_water_bg_witness_distance_probe.json
tests/goal5313_xhd_water_bg_n_points_cell_alignment_test.py
```

### Goal5314 - Corrected WaterBodies/BG Comparison Summary

```text
history/internal_docs/goal5314_xhd_water_bg_corrected_comparison_summary_result_2026-07-09.md
history/internal_docs/call_for_review_goal5314_xhd_water_bg_corrected_comparison_summary_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5314_water_bg_corrected_comparison_summary.json
tests/goal5314_xhd_water_bg_corrected_comparison_summary_test.py
```

### Goal5315 - Status Docs Update

```text
history/internal_docs/goal5315_xhd_water_bg_status_docs_update_result_2026-07-09.md
history/internal_docs/call_for_review_goal5315_xhd_water_bg_status_docs_update_2026-07-09.md
history/internal_docs/xhd_current_status_after_goal5314_2026-07-09.md
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
Paper-reproduction-apps/x-hd-paper/results/README.md
tests/goal5315_xhd_water_bg_status_docs_test.py
```

### Goal5316 - Figure-5 / Level-B Status Matrix

```text
history/internal_docs/goal5316_xhd_figure5_level_b_status_matrix_result_2026-07-09.md
history/internal_docs/call_for_review_goal5316_xhd_figure5_level_b_status_matrix_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5316_figure5_level_b_status_matrix.json
tests/goal5316_xhd_figure5_level_b_status_matrix_test.py
```

## Packet Thesis

The packet makes two bounded moves:

1. It resolves the WaterBodies->BlockGroups full-public scalar mismatch as an
   author configuration denominator issue:

   ```text
   paper-log num_points_cell = 8
   Goal5311 default author rerun num_points_cell = 15
   Goal5313 paper-config rerun num_points_cell = 8
   ```

2. It consolidates current Figure-5-like X-HD evidence into a status matrix
   without claiming exact paper inputs, Figure-5 completion, full paper
   reproduction, or author-vs-RTDL performance parity.

## Critical Numbers To Verify

### WaterBodies -> BlockGroups

Goal5311 default-author denominator:

```text
author default n_points_cell=15 HDResult = 0.8970130085945129
paper-log HDResult                         = 0.8964367508888245
```

Goal5313 paper-config denominator:

```text
author n_points_cell=8 HDResult = 0.8964367508888245
paper-log HDResult              = 0.8964367508888245
```

RTDL witness boundary:

```text
RTDL exact-witness float64 distance = 0.8964380566690101
same witness float32 distance       = 0.8964367508888245
abs diff float64 vs author float32  = 1.305780185645311e-06
declared tolerance                  = 2e-6
matches at 1e-6                     = false
matches at 2e-6                     = true
```

### Dragon -> HappyBuddha

```text
paper-log HDResult       = 0.12572969496250153
author rerun HDResult    = 0.12572988867759705
RTDL HDResult            = 0.12572988629271128
RTDL vs author abs diff  = 2.3848857610975216e-09
```

Carry-forward caveat:

```text
global_bound_early_break = true
per_source_witness_exact = false
```

### Dragon -> Asian

```text
paper-log HDResult    = 0.06536811590194702
author rerun HDResult = 0.06545527279376984
abs diff              = 8.715689182281494e-05
```

This must remain a no-go for RTDL timing under the current available input
mapping.

### County -> ZCTA Full-Public Probe

```text
County paper point count    = 9,438,045
County observed point count = 12,477,179
delta                       = +3,039,134 (+32.2009%)
```

This must block exact/Figure-5 promotion for the current public County source.

## Required Review Questions

1. Does Goal5313 prove that the WaterBodies/BG mismatch was caused by
   `n_points_cell` denominator drift rather than by an RTDL semantic mismatch?

2. Is it correct to supersede the Goal5311 default `n_points_cell=15` author
   rerun as the final paper-log denominator while preserving it as
   config-sensitivity evidence?

3. Is the Goal5314 numeric boundary honest: RTDL exact-witness float64 does
   not equal author/paper float32 at `1e-6`, but does match at an explicit
   `2e-6` tolerance, and the same witness rounded to float32 equals the
   author/paper value?

4. Do Goals5313-5315 avoid claiming exact paper WKT recovery, Figure-5
   completion, identical internal numeric precision, or performance parity?

5. Does Goal5316 correctly classify Dragon->HappyBuddha as the strongest
   graphics Level-B scalar match while preserving the early-break
   approximate-witness caveat?

6. Does Goal5316 correctly keep Dragon->Asian as an author-value no-go under
   the current available public/scaled input?

7. Does Goal5316 correctly keep Thai graphics rows as Level-B same-source
   scalar matches, not exact paper dataset reproduction?

8. Does Goal5316 correctly keep County->ZCTA bounded and full-public evidence
   from being promoted to exact/Figure-5 status?

9. Does Goal5316 correctly classify WaterBodies->BlockGroups full-public as
   the strongest current geo Level-B row, while still blocking exact WKT,
   Figure-5, performance, and identical-precision claims?

10. Are any rows missing from the matrix that should be present for current
    Figure-5-like X-HD status?

11. Are any row labels too strong, especially `full_public`, `paper_config`,
    `corrected`, `matched`, or `strongest_current`?

12. Is the proposed next decision correct: after this packet, choose between
    exact input provenance, additional Figure-5 coverage, denominator-aligned
    performance design, or system extraction?

## Expected Answer Shape

Please answer in this shape:

```text
Verdict:
  approve_goals5313_5316_xhd_water_bg_and_figure5_level_b_status_packet
  OR approve_with_required_amendments
  OR revise_goals5313_5316_packet

Blocking findings:
  - ...

Required amendments:
  - ...

Non-blocking notes:
  - ...

Answers to the 12 review questions:
  1. ...
  ...
  12. ...
```

## Requested Verdict Label If Approved

```text
approve_goals5313_5316_xhd_water_bg_and_figure5_level_b_status_packet
```
