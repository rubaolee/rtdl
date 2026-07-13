# Call For Review: Goal5304 X-HD County-ZCTA Author Ingestion

Date: 2026-07-09

Please strictly review Goal5304.

## Files To Review

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5304_county_zcta_author_ingestion_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/goal5304_raw/author_county_zcta_arcgis_bounded.json
Paper-reproduction-apps/x-hd-paper/results/goal5304_raw/author_stdout.txt
Paper-reproduction-apps/x-hd-paper/results/goal5304_raw/author_stderr.txt
tests/goal5304_xhd_county_zcta_author_ingestion_test.py
history/internal_docs/goal5304_xhd_county_zcta_author_ingestion_result_2026-07-09.md
```

Relevant prior artifacts:

```text
Paper-reproduction-apps/x-hd-paper/data/generated/goal5303_arcgis_county_zcta_bounded/manifest.json
Paper-reproduction-apps/x-hd-paper/data/generated/goal5303_arcgis_county_zcta_bounded/dtl_cnty_arcgis_bounded.wkt
Paper-reproduction-apps/x-hd-paper/data/generated/goal5303_arcgis_county_zcta_bounded/uszipcode_arcgis_bounded.wkt
history/internal_docs/goal5303_xhd_county_zcta_arcgis_bounded_fixture_result_2026-07-09.md
history/internal_docs/call_for_review_goal5303_xhd_county_zcta_arcgis_bounded_fixture_2026-07-09.md
```

## Scope

Goal5304 is an author-ingestion gate only.

It does:

```text
upload the Goal5303 WKT fixture to the current POD;
run author hd_exec with input_type=wkt, n_dims=2, normalize=false;
download the author JSON/stdout/stderr;
record HDResult, point counts, author timing fields, and claim boundary.
```

It does not:

```text
run RTDL;
claim author/RTDL correctness;
claim exact paper dataset recovery;
claim geo Figure 5 reproduction;
claim performance ratio;
claim full paper reproduction.
```

## Claims To Check

1. POD access used the wrapper and the current POD is recorded correctly.
2. The remote WKT hashes match Goal5303.
3. Author `hd_exec` command uses the expected geo contract:
   `input_type=wkt`, `n_dims=2`, `variant=rt`, `execution=gpu`,
   `normalize=false`.
4. The raw author JSON exists and reports:
   - `HDResult = 65.44752502441406`
   - `NumPoints = 38034 / 50272`
   - `Running.AvgTime = 6.169 ms`
5. The author point counts match Goal5303's author-loader outer-ring point
   estimates.
6. The report does not overclaim RTDL correctness, exact dataset status,
   Figure 5 reproduction, performance, or full paper reproduction.
7. Goal5305 should run RTDL only after this author-ingestion gate is accepted.

## Questions For Reviewer

1. Does Goal5304 correctly prove author-side WKT ingestion for the bounded
   County-ZCTA fixture?
2. Are the author command flags appropriate for the X-HD paper geo path?
3. Are the point counts sufficient evidence that the WKT conversion matches the
   author loader's outer-ring semantics for this bounded fixture?
4. Is it correct that this goal still does not prove author/RTDL correctness?
5. Is it correct that no performance ratio is allowed from this author-only run?
6. Is the Alabama-vs-Alaska fixture caveat carried forward strongly enough?
7. Should Goal5304 close with
   `completed_county_zcta_author_ingestion__author_hd_exec_passed__rtdl_not_run`?

## Requested Verdict Label

```text
approve_goal5304_county_zcta_author_ingestion__author_hd_exec_passed
```
