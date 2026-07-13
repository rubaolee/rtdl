# Call For Review: Goal5176 Paper-Branch Log Index

Date: 2026-07-08

Please strictly review Goal5176.

## Files Under Review

Result report:

```text
history/internal_docs/goal5176_paper_branch_log_index_result_2026-07-08.md
```

Implementation:

```text
Paper-reproduction-apps/x-hd-paper/scripts/extract_xhd_paper_branch_log_index.py
tests/goal5176_xhd_paper_branch_log_index_test.py
```

Evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_branch_log_index_goal5176_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

## Claim Being Reviewed

Allowed claim:

```text
Goal5176 parses the X-HD author paper-branch expr/for_the_paper/logs tree
through git object access, without checking out long Windows paths. The
artifact parses 41755 JSON blobs with zero parse errors, retains all 4535
run_all records, samples non-run_all training logs, and records 1946 unique
input paths. This is paper-branch workload provenance only.
```

Forbidden claims:

```text
full X-HD paper reproduction
exact paper dataset reproduction
paper figure reproduction
author-performance parity
author-vs-RTDL performance ratio
author log statistics proving exact input identity
RTDL reproducing all Figure 5-11 results
```

## Critical Context

Goal5175 only inventoried the `origin/paper:expr/for_the_paper` JSON tree. A
normal Windows checkout of that branch fails on the long log paths. Goal5176
uses git tree/blob access instead and turns the inventory into a structured
index.

This still does not provide input file bytes or hashes.

## Evidence Summary

Generated artifact:

```text
xhd_paper_branch_log_index_goal5176_2026-07-08.json
```

Key fields:

```text
schema = rtdl.paper_reproduction.xhd.paper_branch_log_index.v1
status = paper_branch_log_index_extracted_via_git_objects__input_files_not_present
author_repo.head = 8c3846866052e1e8755210021f23fac2cbe8c3d6
summary.json_blob_count = 41755
summary.parsed_json_count = 41755
summary.parse_error_count = 0
summary.run_all_record_count = 4535
summary.unique_input_path_count = 1946
summary.input_files_available_in_author_repo = 0
summary.input_files_available_on_current_machine = 0
claim_boundary.full_paper_reproduction_claimed = false
claim_boundary.exact_paper_dataset_reproduction_claimed = false
claim_boundary.figure_reproduction_claimed = false
claim_boundary.performance_ratio_claimed = false
```

Run-all structure:

```text
run_all/auto_tune = 1814
run_all/eb_gpu = 907
run_all/hybrid_gpu = 907
run_all/rt_gpu = 907
```

Validation:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_paper_branch_log_index_goal5176_2026-07-08.json > $null
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_author_log_workload_manifest_goal5175_2026-07-08.json > $null
py -m unittest tests.goal5176_xhd_paper_branch_log_index_test tests.goal5175_xhd_author_log_workload_manifest_test

Ran 2 tests in 1.067s
OK
```

## Review Questions

1. Does the script genuinely avoid ordinary checkout and parse logs through git
   tree/blob access?
2. Are the artifact counts (`41755` JSON blobs, `41755` parsed, `0` parse
   errors, `4535` run_all records, `1946` unique input paths) supported by the
   JSON artifact?
3. Is the output bounding acceptable: all `run_all` records included, non-run_all
   training logs sampled plus aggregated?
4. Does the report clearly distinguish paper-branch workload provenance from
   exact input file provenance?
5. Does the artifact preserve claim boundaries and avoid full-paper, exact
   dataset, figure, or performance-ratio claims?
6. Is the focused test sufficient for the git-object parsing path and
   claim-boundary flags?
7. Does this goal properly advance the full reproduction effort by identifying
   the paper-branch workload matrix while still refusing to overclaim?
8. Should Goal5176 close as
   `completed_paper_branch_log_index__implemented_review_pending`, or are
   amendments required?

## Expected Answer Shape

```text
Verdict:
  approve_goal5176_paper_branch_log_index
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
