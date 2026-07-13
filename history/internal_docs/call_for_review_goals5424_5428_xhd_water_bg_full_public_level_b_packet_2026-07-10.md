# Consolidated Call For Review - Goals5424-5428 X-HD Water/BG Full-Public Level-B Packet

Please strictly review Goals5424-5428 as one packet.

This packet does **not** claim exact paper input recovery, Figure 5
reproduction, full X-HD paper reproduction, author RT-core equivalence, or any
author-vs-RTDL performance ratio.

## Files Under Review

Goal5424:

```text
history/internal_docs/goal5424_xhd_post_level_b_blocker_priority_2026-07-10.md
history/internal_docs/call_for_review_goal5424_xhd_post_level_b_blocker_priority_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5424_post_level_b_blocker_priority.json
tests/goal5424_post_level_b_blocker_priority_test.py
```

Goal5425:

```text
history/internal_docs/goal5425_xhd_full_public_water_bg_wkt_generation_feasibility_2026-07-10.md
history/internal_docs/call_for_review_goal5425_xhd_full_public_water_bg_wkt_generation_feasibility_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5425_full_public_water_bg_wkt_generation_feasibility.json
tests/goal5425_full_public_water_bg_wkt_generation_feasibility_test.py
```

Goal5426:

```text
history/internal_docs/goal5426_xhd_full_public_water_bg_wkt_resource_gate_2026-07-10.md
history/internal_docs/call_for_review_goal5426_xhd_full_public_water_bg_wkt_resource_gate_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5426_full_public_water_bg_wkt_resource_gate.json
tests/goal5426_full_public_water_bg_wkt_resource_gate_test.py
```

Goal5427:

```text
history/internal_docs/goal5427_xhd_water_bg_paper_config_consolidation_2026-07-10.md
history/internal_docs/call_for_review_goal5427_xhd_water_bg_paper_config_consolidation_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5427_water_bg_paper_config_consolidation.json
tests/goal5427_water_bg_paper_config_consolidation_test.py
```

Goal5428:

```text
history/internal_docs/goal5428_xhd_level_b_matrix_with_water_bg_full_public_2026-07-10.md
history/internal_docs/call_for_review_goal5428_xhd_level_b_matrix_with_water_bg_full_public_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5428_level_b_matrix_with_water_bg_full_public.json
tests/goal5428_level_b_matrix_with_water_bg_full_public_test.py
```

Governance:

```text
history/internal_docs/governance_rule_stop_loss_gate_for_app_artifact_parity_2026-07-10.md
scripts/xhd_stop_loss_gate_check.py
```

## Packet Summary

Goal5424 selected the next branch:

```text
WaterBodies->BlockGroups full-public feasibility before more route work
```

Reason:

```text
Goal5309 shows WaterBodies and BlockGroups are the strongest full-public geo
candidate by point-count and MBR proximity:
  WaterBodies delta = +6,129 points (+0.0269%)
  BlockGroups delta = +127 points (+0.000243%)
  both MBR deltas < 1e-5 degrees
```

Goal5425 estimated generation resources:

```text
estimated_total_wkt_gib = 2.0944229466840625
recommended_free_disk_gib = 6.283268840052187
probe_time_floor = 1569.74s
```

Goal5426 ran the POD resource gate:

```text
POD preflight = OK
/tmp free GiB = 3.9125747680664062
generation_safety_gate_passed = false
```

Therefore full WKT regeneration was not safe on the current POD.  But existing
Goal5311 WKT artifacts already exist on the POD and match the Goal5310 manifest:

```text
WaterBodies sha256 = 0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39
BlockGroups sha256 = 8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e
all_files_exist = true
all_sizes_match = true
all_hashes_match = true
```

Goal5427 consolidated the correct denominator:

```text
Goal5311 default n_points_cell=15:
  HDResult = 0.8970130085945129
  paper value matched = false

Goal5314 paper-config n_points_cell=8:
  author HDResult = 0.8964367508888245
  matches paper log = true

RTDL exact-witness:
  HDResult float64 = 0.8964380566690101
  abs diff = 1.305780185645311e-06 <= 2e-6
  same witness float32 distance = 0.8964367508888245
```

Goal5428 updated the Level-B matrix:

```text
graphics_case_count = 3
graphics_route_result_count = 6
bounded_geo_case_count = 2
bounded_geo_route_result_count = 2
full_public_geo_case_count = 1
full_public_geo_route_result_count = 1
total_case_count = 6
total_route_result_count = 9
```

New row:

```text
geo_water_bg_full_public_paper_config
input_identity_level = level_b_full_public_same_source_geo_not_exact_file_hash
```

## Claim Boundary To Attack

Authorized:

```text
Level-B scalar evidence matrix
WaterBodies->BlockGroups full-public paper-config scalar row
hash-verified reuse of existing Goal5311 WKT artifacts
```

Forbidden:

```text
exact paper WKT files recovered
geo Figure 5 reproduced
full X-HD paper reproduced
author-vs-RTDL performance ratio
author RT-core algorithm equivalence
route micro-optimization authorization
explicit -lb reopening
```

## Validation Commands Already Run

```text
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5427_xhd_water_bg_paper_config_consolidation_2026-07-10.md history/internal_docs/goal5428_xhd_level_b_matrix_with_water_bg_full_public_2026-07-10.md
RESULT: PASS

$env:PYTHONPATH='src'; py -m unittest tests.goal5428_level_b_matrix_with_water_bg_full_public_test tests.goal5427_water_bg_paper_config_consolidation_test tests.goal5426_full_public_water_bg_wkt_resource_gate_test tests.goal5423_level_b_matrix_consolidation_after_geo_test
Ran 25 tests OK
```

Goal5426 local validation:

```text
py -m unittest tests.goal5426_full_public_water_bg_wkt_resource_gate_test tests.goal5425_full_public_water_bg_wkt_generation_feasibility_test tests.goal5424_post_level_b_blocker_priority_test tests.goal5314_xhd_water_bg_corrected_comparison_summary_test tests.goal5311_xhd_water_bg_full_public_author_ingestion_test
Ran 25 tests OK
```

Known Windows warning:

```text
Could not find platform independent libraries <prefix>
```

This warning appeared and was not a test failure.

## Requested Verdict Labels

Approve:

```text
approve_goals5424_5428_xhd_water_bg_full_public_level_b_packet
```

Revise:

```text
revise_goals5424_5428_xhd_water_bg_packet
```

Block:

```text
block_goals5424_5428_xhd_water_bg_packet
```

## Review Questions

1. Did Goal5424 correctly select WaterBodies->BlockGroups as the next branch,
   and correctly reject route micro-optimization / explicit `-lb` as default
   next work?
2. Did Goal5425 correctly estimate WKT size, runtime floor, resource gates, and
   kill conditions without executing or claiming correctness?
3. Did Goal5426 correctly stop full regeneration because current `/tmp` free
   space is below the 6.283 GiB safety threshold?
4. Did Goal5426 correctly reuse existing Goal5311 WKT artifacts by hash and
   symlink instead of copying or regenerating?
5. Did Goal5427 correctly switch the denominator from Goal5311 default
   `n_points_cell=15` to Goal5314 paper-config `n_points_cell=8`?
6. Does Goal5427 correctly keep the float64-vs-float32 tolerance boundary
   explicit and avoid exact numeric overclaim?
7. Does Goal5428 correctly add the WaterBodies->BlockGroups full-public row as
   Level-B scalar evidence only?
8. Does the packet avoid claiming exact paper input recovery, geo Figure 5
   reproduction, full paper reproduction, author RT-core equivalence, or any
   performance ratio?
9. Does the stop-loss G-1 discipline correctly prevent reopening explicit
   `-lb` / row identity / app artifact parity?
10. Is the recommended next step correct: strict review or exact dataset /
    denominator provenance, not route micro-optimization?

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
10. ...
```
