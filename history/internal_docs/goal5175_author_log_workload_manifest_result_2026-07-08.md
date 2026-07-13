# Goal5175 Author Log Workload Manifest Result

Date: 2026-07-08

## Verdict

```text
completed_author_log_workload_manifest__implemented_review_pending
```

Goal5175 extracts a structured workload manifest from the pinned X-HD author
repository logs and records a separate inventory for the larger paper-branch log
tree.

This goal deepens dataset provenance. It does **not** make an exact paper
dataset, figure reproduction, full paper reproduction, or performance-ratio
claim.

## Why This Goal Exists

Goal5131 established that the exact X-HD paper input files are not present in
the author repository or current workspace. Goal5175 asks the next narrower
question:

```text
What exact author workload paths, point counts, Gini values, HDResult values,
and timing fields are visible from the author-provided logs?
```

This makes the missing-dataset problem actionable. Instead of saying only
"datasets unavailable", the paper app now has a machine-readable map of the
author's logged workloads and the evidence those logs do and do not provide.

## Implementation

New script:

```text
Paper-reproduction-apps/x-hd-paper/scripts/extract_xhd_author_log_manifest.py
```

Command run:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\extract_xhd_author_log_manifest.py \
  --author-repo .codex_tmp\xhd_author_repo \
  --output Paper-reproduction-apps\x-hd-paper\results\xhd_author_log_workload_manifest_goal5175_2026-07-08.json
```

The script parses JSON logs from the checked-out author repository and records:

- author repository HEAD and branch heads;
- hashes for key author experiment scripts;
- log roots scanned;
- per-log workload records;
- unique author input paths;
- point counts, Gini values, MBRs, `HDResult`, `Running.AvgTime`, and repeat
  timing summaries where available;
- explicit exact-dataset rules and claim boundaries.

It also records an inventory-only view of the `origin/paper` branch
`expr/for_the_paper` JSON tree. That inventory is deliberately not promoted to
parsed workload records in this goal.

## Evidence Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_author_log_workload_manifest_goal5175_2026-07-08.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.author_log_workload_manifest.v1
```

Summary:

```text
total_json_logs parsed from main expr/logs: 281
unique author input paths:                 335
input files available on current machine:  0
input files available in author repo:      0

logs_by_family:
  end2end: 260
  mem:      21

logs_by_variant_execution:
  rt_gpu:     264
  clover_gpu: 10
  nn_gpu:       7

logs_by_category:
  BraTS2020_ValidationData: 250
  geo:                         15
  graphics:                    16
```

Current checkout log roots scanned:

```text
expr/logs: 281 JSON files
```

Additional branch inventory:

```text
origin/paper:expr/for_the_paper
  JSON blobs: 41755
  status: inventory_only__json_blobs_not_parsed_into_workloads
  largest prefixes:
    logs/train:   37220
    logs/run_all:  4535
```

Environment note:

```text
An attempted ordinary Windows checkout of the paper branch failed on the
for_the_paper log tree because many JSON paths exceed the local path-length
limit. Goal5175 therefore records paper-branch logs through git tree inventory
rather than by materializing those files into the Windows worktree. A future
paper-branch parser should use git object/tree access or a Linux/POD checkout.
```

## What The Logs Prove

The parsed author logs provide:

```text
input absolute paths
dataset basenames
point counts
Gini indices
MBR statistics
HDResult and timing fields
experiment script command structure
```

Example author path shape:

```text
/local/storage/shared/HDDatasets/graphics/dragon.ply
/local/storage/shared/HDDatasets/graphics/happy_buddha.ply
```

The logs also preserve author-reported `HDResult`, `Running.AvgTime`, repeat
`ReportedTime`, BVH time, and iteration timing/offload fields when present.

## What The Logs Do Not Prove

The logs do **not** provide:

```text
input file bytes
input file hashes
public source snapshot hashes
proof that a reconstructed public dataset is byte-identical
```

Therefore Goal5175 does not upgrade Level B same-source representative evidence
to Level C exact paper dataset reproduction. Matching point counts or Gini values
remains necessary but not sufficient for exact dataset identity.

## Manifest Update

Updated:

```text
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

The manifest now includes the Goal5175 artifact under `evidence.result_artifacts`
with `matched = null` and a note that exact input bytes/hashes remain absent.

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\data\manifest.json > $null
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_author_log_workload_manifest_goal5175_2026-07-08.json > $null
py -m unittest tests.goal5175_xhd_author_log_workload_manifest_test tests.goal5173_author_directed_route_mode_test
```

Result:

```text
Ran 4 tests in 2.301s
OK
```

Known local noise:

```text
Could not find platform independent libraries <prefix>
```

This is the existing Windows `py` environment noise; the tests and JSON checks
passed.

## Claim Boundary

Allowed claim:

```text
Goal5175 extracts a structured author-log workload manifest from the pinned
author repository. The manifest records 281 parsed main-branch logs, 335 unique
author input paths, zero available exact input files, and an inventory-only
paper-branch log tree with 41755 JSON blobs. It deepens dataset provenance but
does not provide exact input bytes or hashes.
```

Forbidden claims:

```text
full X-HD paper reproduction
exact paper dataset reproduction
paper figure reproduction
author-performance parity
author-vs-RTDL performance ratio
treating author log statistics as exact dataset identity
treating inventory-only paper-branch logs as parsed workload records
```

## Next Recommended Goal

Goal5176 should decide whether to parse the `origin/paper` branch
`expr/for_the_paper` JSON logs into a separate, bounded manifest or whether to
first target a smaller exact-workload subset from the existing 281 parsed logs.
Either way, the next goal must keep the Level B/Level C boundary intact:

```text
author log path/statistics != exact input file identity
```
