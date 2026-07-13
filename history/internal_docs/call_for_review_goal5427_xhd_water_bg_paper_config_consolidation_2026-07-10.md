# Call For Review - Goal5427 X-HD WaterBodies->BlockGroups Paper-Config Consolidation

Please strictly review Goal5427.

## Files Under Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5427_water_bg_paper_config_consolidation.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5427_water_bg_paper_config_consolidation.json
tests/goal5427_water_bg_paper_config_consolidation_test.py
history/internal_docs/goal5427_xhd_water_bg_paper_config_consolidation_2026-07-10.md
history/internal_docs/call_for_review_goal5427_xhd_water_bg_paper_config_consolidation_2026-07-10.md
```

Relevant prior evidence:

```text
history/internal_docs/goal5426_xhd_full_public_water_bg_wkt_resource_gate_2026-07-10.md
history/internal_docs/goal5314_xhd_water_bg_corrected_comparison_summary_2026-07-09.md
history/internal_docs/goal5311_xhd_water_bg_full_public_author_ingestion_result_2026-07-09.md
```

## Requested Verdict Labels

Approve:

```text
approve_goal5427_water_bg_paper_config_consolidation_no_rerun
```

Revise:

```text
revise_goal5427_water_bg_paper_config_consolidation
```

Block:

```text
block_goal5427_water_bg_paper_config_consolidation
```

## Review Questions

1. Is it correct that Goal5427 performs no new author or RTDL execution and only
   consolidates existing evidence?
2. Is it correct to avoid rerunning the 873s-class RTDL exact-witness route,
   given that Goal5426 verifies the current POD symlink inputs hash-match the
   same Goal5310 WKT artifacts used by Goal5314?
3. Does the report correctly select Goal5314 `n_points_cell=8` as the
   paper-config author denominator?
4. Does it keep Goal5311 `n_points_cell=15` visible only as default-author
   config sensitivity evidence, not as the paper denominator?
5. Does the RTDL comparison use the declared Goal5314 tolerance boundary
   correctly: float64 RTDL result differs from author float32 by about
   `1.3058e-6 <= 2e-6`?
6. Is the statement "same witness float32 distance matches the paper log"
   supported by Goal5314 and carried without overclaim?
7. Does the claim boundary correctly block exact paper dataset recovery,
   geo Figure 5 reproduction, full paper reproduction, performance ratio,
   author RT-core equivalence, route micro-optimization, and explicit `-lb`?
8. Is it acceptable to mark the full-public WaterBodies->BlockGroups row as
   Level-B scalar evidence, not Level-C exact paper input and not Level-D
   figure reproduction?
9. Should the next Goal5428 fold this row into the Level-B matrix as
   `geo_water_bg_full_public_paper_config`?

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
