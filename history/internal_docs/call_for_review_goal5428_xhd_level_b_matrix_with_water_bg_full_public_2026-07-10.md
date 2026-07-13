# Call For Review - Goal5428 X-HD Level-B Matrix With Water/BG Full-Public Row

Please strictly review Goal5428.

## Files Under Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5428_level_b_matrix_with_water_bg_full_public.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5428_level_b_matrix_with_water_bg_full_public.json
tests/goal5428_level_b_matrix_with_water_bg_full_public_test.py
history/internal_docs/goal5428_xhd_level_b_matrix_with_water_bg_full_public_2026-07-10.md
history/internal_docs/call_for_review_goal5428_xhd_level_b_matrix_with_water_bg_full_public_2026-07-10.md
```

Relevant prior evidence:

```text
history/internal_docs/goal5423_xhd_level_b_matrix_consolidation_after_geo_2026-07-10.md
history/internal_docs/goal5427_xhd_water_bg_paper_config_consolidation_2026-07-10.md
history/internal_docs/goal5426_xhd_full_public_water_bg_wkt_resource_gate_2026-07-10.md
history/internal_docs/goal5314_xhd_water_bg_corrected_comparison_summary_2026-07-09.md
```

## Requested Verdict Labels

Approve:

```text
approve_goal5428_level_b_matrix_with_water_bg_full_public_no_ratio
```

Revise:

```text
revise_goal5428_level_b_matrix
```

Block:

```text
block_goal5428_level_b_matrix
```

## Review Questions

1. Does Goal5428 correctly expand the Level-B matrix to 3 graphics cases,
   2 bounded geo cases, and 1 full-public geo case?
2. Is the `geo_water_bg_full_public_paper_config` row correctly classified as
   `level_b_full_public_same_source_geo_not_exact_file_hash` rather than exact
   paper input?
3. Does the row correctly use Goal5314 paper-config author denominator
   (`n_points_cell=8`, `HDResult=0.8964367508888245`)?
4. Does the RTDL row correctly preserve the declared tolerance boundary
   (`0.8964380566690101`, abs diff about `1.3058e-6 <= 2e-6`)?
5. Does the report correctly keep bounded `water_bg_bounded` separate from the
   stronger full-public `geo_water_bg_full_public_paper_config` row?
6. Does it avoid claiming geo Figure 5 reproduction, exact paper dataset
   recovery, full paper reproduction, author RT-core equivalence, or
   performance ratios?
7. Are the remaining blockers complete and visible?
8. Does the builder remain consolidation-only, with no author execution, no
   RTDL execution, no POD calls, and no route optimization?
9. Is the next recommendation correct: strict review of Goals5424-5428 or exact
   dataset/denominator provenance, not route micro-optimization or explicit
   `-lb`?

## Expected Answer Shape

Please answer with:

```text
Verdict: <one requested label>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
...
9. ...
```
