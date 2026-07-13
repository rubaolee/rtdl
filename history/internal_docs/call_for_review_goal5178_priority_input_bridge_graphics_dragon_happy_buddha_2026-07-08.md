# Call For Review: Goal5178 Priority Input Bridge - Dragon HappyBuddha

Date: 2026-07-08

Please strictly review Goal5178.

## Files Under Review

Result report:

```text
history/internal_docs/goal5178_priority_input_bridge_graphics_dragon_happy_buddha_result_2026-07-08.md
```

Implementation:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_priority_input_bridge.py
tests/goal5178_xhd_priority_input_bridge_test.py
```

Evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_priority_input_bridge_goal5178_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_log_mapping_goal5177_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_branch_log_index_goal5176_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/data/external/stanford/README.md
Paper-reproduction-apps/x-hd-paper/data/manifest.json
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

## Claim Being Reviewed

Allowed claim:

```text
Goal5178 bridges the Goal5177 graphics_dragon_happy_buddha priority subset to
locally acquired public Stanford full-resolution Dragon/HappyBuddha PLY
candidates. The public files are present, their vertex counts match the author
paper-branch logs (437645 and 543652), and SHA256 hashes are recorded. This is
a strong Level B same-source candidate only.
```

Forbidden claims:

```text
exact paper dataset reproduction
full X-HD paper reproduction
Figure 5 graphics reproduction
author-performance parity
author-vs-RTDL performance ratio
local public files are byte-identical to author /local/storage files
the current RTDL route can process full 437645 x 543652 scale without a scalable route plan
```

## Critical Context

Goal5177 selected `graphics_dragon_happy_buddha` as the most practical first
paper-log-to-route target.

Goal5178 found that the author logs report:

```text
dragon.ply:        437645 points
happy_buddha.ply:  543652 points
```

and local public Stanford full PLY candidates have exactly those vertex counts.

This is strong same-source evidence, but it is still not exact paper input
identity because the author logs do not provide input file bytes or hashes.

## Evidence Summary

Generated artifact:

```text
xhd_priority_input_bridge_goal5178_graphics_dragon_happy_buddha_2026-07-08.json
```

Key fields:

```text
schema = rtdl.paper_reproduction.xhd.priority_input_bridge.v1
status = graphics_dragon_happy_buddha_public_stanford_candidate_bridged__level_b_only
author_log_records.record_count = 5
author_log_records.hd_results = [0.12572969496250153]
public_same_source_candidates.dragon.ply.ply_header.vertex_count = 437645
public_same_source_candidates.happy_buddha.ply.ply_header.vertex_count = 543652
bridge_assessment.all_full_public_candidates_present = true
bridge_assessment.full_public_candidate_point_counts_match_author_logs = true
bridge_assessment.strong_same_source_candidate = true
bridge_assessment.exact_paper_dataset_identity_proved = false
claim_boundary.level_b_same_source_candidate_claimed = true
claim_boundary.exact_paper_dataset_reproduction_claimed = false
claim_boundary.figure_reproduction_claimed = false
claim_boundary.performance_ratio_claimed = false
claim_boundary.full_paper_reproduction_claimed = false
```

Candidate hashes:

```text
dragon_vrip.ply:
  SHA256 = FEA87FF48F2ABA22FB53E7B67C3FF3F7B8C2A3B3A0653AF62C48BBA67C6D5744

happy_vrip.ply:
  SHA256 = 2283371216D748A08376A3C88698E283CC8F18D10CED348D6D133051BCF217AB
```

Validation:

```text
py -m unittest tests.goal5178_xhd_priority_input_bridge_test tests.goal5177_xhd_paper_target_log_mapping_test

Ran 2 tests in 0.112s
OK
```

## Review Questions

1. Does Goal5178 correctly bridge the Goal5177 priority subset to the public
   Stanford full PLY candidate files?
2. Are the author log record count, HDResult, sections, paths, and point counts
   supported by the artifact?
3. Are the public candidate PLY headers and SHA256 hashes recorded clearly?
4. Is the point-count match (`437645` and `543652`) enough for Level B
   same-source candidate status?
5. Does the report correctly refuse Level C exact paper dataset status despite
   the point-count match?
6. Are the reasons exact identity is not proved complete and clear?
7. Does the test enforce the key distinction: point-count match supports Level B
   but exact paper identity remains false?
8. Does the manifest/register update keep Goal5178 as implemented / review
   pending, not externally approved?
9. Is the recommended next step correct: scalable large-input feasibility plan
   or stronger author provenance, but no naive pairwise exact full-scale run?
10. Should Goal5178 close as
    `completed_priority_input_bridge_graphics_dragon_happy_buddha__level_b_only__implemented_review_pending`,
    or are amendments required?

## Expected Answer Shape

```text
Verdict:
  approve_goal5178_priority_input_bridge_level_b
  OR approve_with_required_amendments
  OR block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to review questions:
  1. ...
  ...
```
