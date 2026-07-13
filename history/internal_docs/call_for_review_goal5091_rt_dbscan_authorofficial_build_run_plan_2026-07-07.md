# Call For Review: Goal5091 RT-DBSCAN AuthorOfficial Build/Run Plan

Date: 2026-07-07

## Requested Verdict Label

```text
approve_goal5091_rt_dbscan_authorofficial_build_run_plan
```

## Review Scope

Please review:

```text
history/internal_docs/goal5091_rt_dbscan_authorofficial_build_run_plan_2026-07-07.md
Paper-reproduction-apps/rt-dbscan-paper/README.md
Paper-reproduction-apps/rt-dbscan-paper/results/README.md
Paper-reproduction-apps/rt-dbscan-paper/results/core_count_smoke_summary.json
Paper-reproduction-apps/rt-dbscan-paper/scripts/run_core_count_smoke.py
```

## Context

Goal5090 located the candidate author artifact and established a local
RTDL/oracle core-count smoke. Goal5091 inspects the author sample's command
shape and identifies the missing comparator output.

The author sample can be built as `sample02-rtdbscan` and run as:

```text
./sample02-rtdbscan [inFile] [size] [eps] [minPts] [outFile]
```

But the inspected source writes timing output while cluster output is commented
out. Therefore a minimal AuthorOfficial comparator patch is required before
same-input correctness can be claimed.

## Review Questions

1. Does the plan correctly identify `sample02-rtdbscan` as the author target?
2. Does it correctly record the author command-line shape?
3. Does it correctly identify the comparator gap: timing is written, but cluster
   or core output is not yet enabled?
4. Is `core_count` the correct first AuthorOfficial comparator target?
5. Does the plan correctly defer component signature / cluster labels until
   after the core-count gate?
6. Does it correctly classify future author changes as compatibility/comparator
   patches that must be disclosed?
7. Does it avoid claiming build success, comparator success, paper input
   recovery, paper reproduction, or performance?
8. Is Goal5092, a POD-ready AuthorOfficial core-count patch/run packet, the
   correct next step?

## Expected Answer Shape

Please provide:

- Verdict
- Blocking findings, if any
- Required amendments, if any
- Non-blocking notes
- Answers to the 8 review questions
