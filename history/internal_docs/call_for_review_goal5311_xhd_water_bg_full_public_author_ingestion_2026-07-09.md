# Call For Review - Goal5311 X-HD WaterBodies -> BlockGroups Full-Public Author Ingestion

Date: 2026-07-09

Please strictly review Goal5311.

## Files To Review

```text
history/internal_docs/goal5311_xhd_water_bg_full_public_author_ingestion_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5311_water_bg_full_public_author_ingestion_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/goal5311_raw/author_water_bg_full_public.json
Paper-reproduction-apps/x-hd-paper/results/goal5311_raw/author_stderr.txt
tests/goal5311_xhd_water_bg_full_public_author_ingestion_test.py
```

Goal5310 input manifest:

```text
Paper-reproduction-apps/x-hd-paper/data/generated/goal5310_water_bg_full_public_wkt_candidate/manifest.json
```

## Context

Goal5309 identified WaterBodies-BlockGroups as a strong full-public candidate
by point count and MBR. Goal5310 materialized that candidate into full WKT.

Goal5311 runs only author `hd_exec` on that candidate. It does not run RTDL.

## Review Questions

1. Does the remote hash verification prove the author run used the Goal5310
   full-public WKT files?
2. Does the author JSON prove successful ingestion and execution on the
   full-public candidate?
3. Do the author input point counts exactly match Goal5310's manifest counts?
4. Is the paper-log mismatch correctly interpreted as blocking exact / Figure-5
   reproduction for this candidate?
5. Does the report correctly avoid claiming RTDL correctness, performance
   ratio, exact paper input recovery, or full paper reproduction?
6. Is it valid to use Goal5311 as the author denominator for a later Level-B
   full-public RTDL scalar comparison, while keeping the paper-log mismatch
   visible?
7. Are the tests sufficient to pin the key facts and claim boundary?
8. Should Goal5311 be closed as
   `completed_water_bg_full_public_author_ingestion__paper_value_not_matched`?

## Expected Answer Shape

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to Q1-Q8:
```

Requested verdict label if approved:

```text
approve_goal5311_water_bg_full_public_author_ingestion__paper_value_not_matched
```
