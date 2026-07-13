# Call For Review: Goal5175 Author Log Workload Manifest

Date: 2026-07-08

Please strictly review Goal5175.

## Files Under Review

Result report:

```text
history/internal_docs/goal5175_author_log_workload_manifest_result_2026-07-08.md
```

Implementation:

```text
Paper-reproduction-apps/x-hd-paper/scripts/extract_xhd_author_log_manifest.py
tests/goal5175_xhd_author_log_workload_manifest_test.py
```

Evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_author_log_workload_manifest_goal5175_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

## Claim Being Reviewed

Allowed claim:

```text
Goal5175 extracts a structured author-log workload manifest from the pinned
X-HD author repository. It parses 281 JSON logs from current main-branch
expr/logs, records 335 unique author input paths, confirms that none of those
input files are present in the author repo/current machine, and records an
inventory-only count of 41755 JSON blobs under origin/paper:expr/for_the_paper.
This is dataset-provenance evidence only.
```

Forbidden claims:

```text
full X-HD paper reproduction
exact paper dataset reproduction
paper figure reproduction
author-performance parity
author-vs-RTDL performance ratio
author log statistics proving exact dataset identity
paper-branch inventory being treated as parsed workload records
```

## Critical Context

Goal5131 previously found that exact X-HD paper input files are not available in
the current evidence. Goal5175 does not solve that. Instead it makes the author
logs machine-readable so that future work can target exact workload paths and
understand what evidence remains missing.

The author logs provide paths, statistics, HDResult, and timing fields. They do
not provide input bytes, input hashes, public source snapshot hashes, or proof
that a reconstructed public dataset is byte-identical.

## Evidence Summary

Generated artifact:

```text
xhd_author_log_workload_manifest_goal5175_2026-07-08.json
```

Key fields:

```text
schema = rtdl.paper_reproduction.xhd.author_log_workload_manifest.v1
status = author_log_workload_manifest_extracted__input_files_not_present
summary.total_json_logs = 281
summary.unique_input_path_count = 335
summary.input_files_available_on_current_machine = 0
summary.input_files_available_in_author_repo = 0
log_roots_scanned = [{path: expr/logs, json_count: 281}]
additional_branch_log_inventories[0].root = expr/for_the_paper
additional_branch_log_inventories[0].json_count = 41755
additional_branch_log_inventories[0].status = inventory_only__json_blobs_not_parsed_into_workloads
claim_boundary.full_paper_reproduction_claimed = false
claim_boundary.exact_paper_dataset_reproduction_claimed = false
claim_boundary.figure_reproduction_claimed = false
claim_boundary.performance_ratio_claimed = false
```

Validation:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\data\manifest.json > $null
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_author_log_workload_manifest_goal5175_2026-07-08.json > $null
py -m unittest tests.goal5175_xhd_author_log_workload_manifest_test tests.goal5173_author_directed_route_mode_test

Ran 4 tests in 2.301s
OK
```

## Review Questions

1. Does the script correctly parse current-checkout author logs into structured
   workload records without claiming exact input availability?
2. Does the manifest honestly distinguish parsed main-branch `expr/logs` records
   from the inventory-only `origin/paper:expr/for_the_paper` JSON tree?
3. Are the summary counts (`281` parsed logs, `335` unique input paths, `0`
   available input files, `41755` inventory-only paper-branch JSON blobs)
   supported by the artifact?
4. Does the exact-dataset rule correctly state that paths/statistics/HDResult do
   not prove byte-identical paper inputs?
5. Does the test cover the parser behavior and claim-boundary flags adequately
   for this provenance-only goal?
6. Does the manifest update preserve existing X-HD claim boundaries and avoid a
   full-paper or performance claim?
7. Is it acceptable that paper-branch logs are inventory-only in this goal, with
   full parsing deferred to a future goal?
8. Should Goal5175 close as
   `completed_author_log_workload_manifest__implemented_review_pending`, or are
   additional amendments required before review approval?

## Expected Answer Shape

```text
Verdict:
  approve_goal5175_author_log_workload_manifest
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
