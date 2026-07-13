# Goal5176 Paper-Branch Log Index Result

Date: 2026-07-08

## Verdict

```text
completed_paper_branch_log_index__implemented_review_pending
```

Goal5176 parses the X-HD author `paper` branch `expr/for_the_paper/logs` JSON
tree through git object access, without checking out the long file paths into
the Windows worktree.

This is paper-branch workload provenance. It is not exact paper dataset
reproduction, figure reproduction, full paper reproduction, or a performance
ratio.

## Why This Goal Exists

Goal5175 parsed the current main-branch `expr/logs` tree and discovered a much
larger `origin/paper:expr/for_the_paper` log tree with 41755 JSON blobs. A normal
Windows checkout of that branch fails because many JSON paths exceed the local
path-length limit.

Goal5176 therefore reads the `paper` branch directly through git trees and blob
objects. That turns the inventory-only finding into a structured paper-branch
workload index.

## Implementation

New script:

```text
Paper-reproduction-apps/x-hd-paper/scripts/extract_xhd_paper_branch_log_index.py
```

Command:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\extract_xhd_paper_branch_log_index.py \
  --repo .codex_tmp\xhd_author_repo_goal5176_nocheckout \
  --rev HEAD \
  --root expr/for_the_paper/logs \
  --output Paper-reproduction-apps\x-hd-paper\results\xhd_paper_branch_log_index_goal5176_2026-07-08.json \
  --max-sample-records 250
```

The temporary author repository was cloned with:

```text
git clone --no-checkout --branch paper --single-branch https://github.com/pwrliang/X-HD.git .codex_tmp\xhd_author_repo_goal5176_nocheckout
```

No ordinary checkout of the long paper log paths was required.

## Evidence Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_branch_log_index_goal5176_2026-07-08.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.paper_branch_log_index.v1
```

Paper branch commit:

```text
8c3846866052e1e8755210021f23fac2cbe8c3d6
```

## Result Summary

```text
json blobs discovered:       41755
json blobs parsed:           41755
parse errors:                    0
run_all records retained:     4535
non-run_all sample records:    250
unique input paths:           1946
input files available:           0
```

Log groups:

```text
run_all:  4535
train:   37220
```

Run-all sections:

```text
run_all/auto_tune: 1814
run_all/eb_gpu:     907
run_all/hybrid_gpu: 907
run_all/rt_gpu:     907
```

Top run-all categories:

```text
run_all/auto_tune/BraTS2020_ValidationData: 1000
run_all/auto_tune/ModelNet40:                800
run_all/auto_tune/geo:                         6
run_all/auto_tune/graphics:                    8
run_all/eb_gpu/BraTS2020_ValidationData:     500
run_all/eb_gpu/ModelNet40:                   400
run_all/eb_gpu/geo:                            3
run_all/eb_gpu/graphics:                       4
run_all/hybrid_gpu/BraTS2020_ValidationData: 500
run_all/hybrid_gpu/ModelNet40:               400
run_all/hybrid_gpu/geo:                        3
run_all/hybrid_gpu/graphics:                   4
run_all/rt_gpu/BraTS2020_ValidationData:     500
run_all/rt_gpu/ModelNet40:                   400
run_all/rt_gpu/geo:                            3
run_all/rt_gpu/graphics:                       4
```

Dimensions:

```text
2-D logs: 12555
3-D logs: 29200
```

Global numeric summaries from parsed logs:

```text
HDResult count:  41755
HDResult min:        0.0
HDResult median:    14.59451961517334
HDResult max:      364.60986328125

Running.AvgTime count:  41755
Running.AvgTime min:        0.2766
Running.AvgTime median:     9.3136
Running.AvgTime max:     3425.6767999999997
```

## Output Bounding

The artifact keeps the output reviewable:

```text
all run_all records included: true
non-run_all records sampled:  true
max non-run_all sample records: 250
unique input sample records: 500
```

The full `train` set is summarized by counters and samples rather than emitted
as 37220 full records.

## What This Proves

Goal5176 proves that the paper branch carries a machine-readable workload log
tree and that RTDL can parse it without checking out long paths.

It provides:

```text
paper-branch log topology
run_all matrix counts
author input paths/basenames where present
point counts and Gini values where present
HDResult and timing fields where present
```

This is stronger than Goal5175's inventory-only view of the paper branch.

## What This Does Not Prove

The paper branch logs still do not provide:

```text
input file bytes
input file hashes
public source snapshot hashes
proof that reconstructed public inputs are byte-identical to the paper inputs
```

Therefore Goal5176 does not upgrade the project to Level C exact paper dataset
reproduction.

## Manifest Update

Updated:

```text
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

The manifest now includes the Goal5176 artifact under `evidence.result_artifacts`
with `matched = null`.

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_paper_branch_log_index_goal5176_2026-07-08.json > $null
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_author_log_workload_manifest_goal5175_2026-07-08.json > $null
py -m unittest tests.goal5176_xhd_paper_branch_log_index_test tests.goal5175_xhd_author_log_workload_manifest_test
```

Result:

```text
Ran 2 tests in 1.067s
OK
```

Known local noise:

```text
Could not find platform independent libraries <prefix>
```

## Claim Boundary

Allowed claim:

```text
Goal5176 parses the X-HD author paper-branch log tree through git object access:
41755 JSON blobs parsed, zero parse errors, 4535 run_all records retained, and
1946 unique input paths observed. It is workload provenance only.
```

Forbidden claims:

```text
full X-HD paper reproduction
exact paper dataset reproduction
paper figure reproduction
author-performance parity
author-vs-RTDL performance ratio
claiming author log statistics prove exact input identity
claiming RTDL has reproduced all Figure 5-11 results
```

## Next Recommended Goal

Goal5177 should map the `run_all` records to the paper's target figures/tables
and identify the smallest exact-workload subset that would matter first if input
files become available.

The next goal should still keep this boundary:

```text
paper-branch author logs != exact input files
```
