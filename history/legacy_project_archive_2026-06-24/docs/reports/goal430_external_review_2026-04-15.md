# Goal 430 External Review

Date: 2026-04-15
Reviewer: Claude Sonnet 4.6 (external AI review, second consensus seat)

## Performance reading: technically honest

The JSON data matches the reported medians exactly. RT engines cluster tightly
around 2.5–2.6 s across all three workloads and all three backends. PostgreSQL
warm-query is ~0.021–0.036 s. PostgreSQL fresh setup is ~10–11 s. No numbers
are cherry-picked or misreported. Median-over-3 is a reasonable and stated
methodology for first-wave bounded records.

The individual engine files (goal426/427/428) were run separately and show
slightly different absolute timings, as expected for independent runs. Row
hashes match across all four JSON sources for every workload, confirming
cross-run correctness consistency.

## PostgreSQL dual representation: correct

Both PostgreSQL legs are present in every JSON artifact:
`postgresql_query_seconds_*` (warm-query-only) and
`postgresql_setup_seconds_*` (fresh table build + index). The report text
explicitly names both scenarios, quantifies both, and draws the correct
inference from each. The "fresh build-plus-query" reading where RT wins is
arithmetically supported by the data (~2.5 s RT vs. ~10–11 s PG total). The
warm-query reading where RT loses (~2.5 s RT vs. ~0.025 s PG) is stated
plainly and not buried.

## Material overclaims: none found

The honest-claim boundary section is explicit:
- "none of the current RT backends is a warm-query PostgreSQL winner" — stated
- the fresh-build win is scoped to "one-shot reading" and "these bounded cases"
- no generalization to full SQL or DBMS behavior is made
- "RT performance leadership over warm PostgreSQL: not established" closes the
  report

The one observational note: the goal427 OptiX run contains a high PostgreSQL
setup outlier (~14.3 s for conjunctive_scan). The report correctly uses medians
and that outlier does not affect the reported figures.

## Verdict

ACCEPT
