# Goal5294 - X-HD Figure 10 Scalability / Overlap Source-Log Audit

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Purpose

Goal5294 audits the author-side evidence for X-HD Figure 10 before any RTDL
route or performance comparison work.

Figure 10 is the scalability / overlap-sensitivity figure.  The pinned author
source separates it into:

```text
vary input scale
vary translate / overlap
```

This goal asks whether the pinned author source and checked-in logs already
contain the numeric matrix needed to reproduce that figure.

This goal does not run RTDL and does not compute any RTDL/author performance
ratio.

## Implementation

New app-owned audit builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure10_scalability_overlap_audit.py
```

Output artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5294_figure10_scalability_overlap_audit_2026-07-09.json
```

Focused regression:

```text
tests/goal5294_xhd_figure10_scalability_overlap_audit_test.py
```

No RTDL core or native files were changed.

## Inputs

The builder reads:

```text
.codex_tmp/xhd_author_repo
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_log_mapping_goal5177_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_matrix_2026-07-08.json
```

Pinned author commit:

```text
7bf41c8442d059c94f4178355c6d5a10571d9658
```

Audited author files:

```text
expr/run_scalability.sh
expr/draw_scalability.py
expr/logs/scalability/...
```

## Author Script Evidence

`expr/run_scalability.sh` is present and defines a scalability matrix over:

```text
dataset = all_nodes.wkt
input_type = wkt
n_dims = 3
execution = gpu
repeat = 1
check = false
variants = [eb, nn, clover, rt]
```

Scale sweep:

```text
limit values = [12500000, 25000000, 50000000, 100000000, 200000000, 400000000]
fixed translate = 0.005
```

Translate / overlap sweep:

```text
translate values = [
  0.0001, 0.0002, 0.0004, 0.0008,
  0.0016, 0.0032, 0.0064, 0.0128,
  0.0256, 0.0512, 0.1024, 0.2048
]
fixed limit = 10000000
```

`expr/draw_scalability.py` is present and expects:

```text
logs/scalability/eb_gpu/scal_vary_size
logs/scalability/eb_gpu/scal_vary_translate
logs/scalability/nn_gpu/scal_vary_size
logs/scalability/nn_gpu/scal_vary_translate
logs/scalability/clover_gpu/scal_vary_size
logs/scalability/clover_gpu/scal_vary_translate
logs/scalability/rt_gpu/scal_vary_size
logs/scalability/rt_gpu/scal_vary_translate
```

It plots:

```text
Input.Files[0].NumPoints
Input.Translate
Running.AvgTime
```

and labels:

```text
EB
NN-KD
NN-Clover
X-HD
```

The artifact records:

```text
script_draw_contract_aligned = true
```

Meaning:

```text
The author run script and plotting file agree on the four variants, size sweep,
translate / overlap sweep, and Running.AvgTime metric.
```

## Checked-In Log Evidence

The checked-in `expr/logs/scalability` matrix is absent:

```text
root_exists = false
total_json_count = 0
complete_variant_sweep_matrix_present = false
```

Every expected directory has zero JSON files:

```text
expr/logs/scalability/eb_gpu/scal_vary_size = 0
expr/logs/scalability/eb_gpu/scal_vary_translate = 0
expr/logs/scalability/nn_gpu/scal_vary_size = 0
expr/logs/scalability/nn_gpu/scal_vary_translate = 0
expr/logs/scalability/clover_gpu/scal_vary_size = 0
expr/logs/scalability/clover_gpu/scal_vary_translate = 0
expr/logs/scalability/rt_gpu/scal_vary_size = 0
expr/logs/scalability/rt_gpu/scal_vary_translate = 0
```

The existing paper-branch `run_all` mapping has workload-family records:

```text
record_count = 4535
coverage_status = workload_families_present__scale_overlap_labels_missing
```

Interpretation:

```text
run_all contains enough records to choose broad workload-family candidates, but
it does not identify the Figure 10 scale / overlap subsets, overlap-controlled
input-generation details, selectivity diagnostics, or exact input hashes.
```

Therefore `run_all` must not be treated as a substitute Figure 10 denominator.

## Decision

Goal5294 reports:

```text
status = figure10_scalability_overlap_audit_ready__figure10_not_reproduced__scalability_logs_missing
figure10_reproduced = false
scalability_numeric_matrix_available = false
run_all_workload_family_records_available = true
run_all_scale_overlap_labels_available = false
author_script_available = true
```

Current blocker:

```text
Author source contains run_scalability.sh and draw_scalability.py for size and
translate/overlap sweeps, but checked-in logs/scalability has no JSON records.
The paper-branch run_all logs have workload-family records, but they do not
identify the Figure 10 scale/overlap subsets or overlap diagnostics. Figure 10
reproduction requires regenerating or recovering the scalability numeric matrix
with exact or explicitly Level-B inputs.
```

## Claim Boundary

Allowed:

```text
Figure 10 author-side source/log audit is ready.
Author scalability scripts are present and internally aligned.
Checked-in scalability logs are missing.
run_all has workload-family records but no scale/overlap labels.
Figure 10 remains not reproduced.
```

Not authorized:

```text
Figure 10 reproduced
exact paper dataset reproduction
RTDL/author scalability or overlap parity
author-vs-RTDL performance ratio
run_all workload-family logs treated as Figure 10
full X-HD paper reproduction
```

## Validation

Commands run:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure10_scalability_overlap_audit.py
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure10_scalability_overlap_audit.py
py -m unittest tests.goal5294_xhd_figure10_scalability_overlap_audit_test
```

Local Python printed the known environment warning:

```text
Could not find platform independent libraries <prefix>
```

All commands exited successfully.

Focused test result:

```text
Ran 3 tests in 0.085s
OK
```

## POD Usage

No POD was required for Goal5294.  This is an author source/log audit over
checked-in files.

A POD becomes relevant only if the next approved step is to run
`run_scalability.sh` or equivalent author commands to regenerate the
`logs/scalability` matrix.

## Next Recommended Step

Do not start RTDL Figure 10 comparison work yet.  Choose one:

```text
1. If exact all_nodes/HDDatasets inputs are available on a POD, run author
   run_scalability.sh or equivalent commands to regenerate scalability logs.
2. If exact inputs are unavailable, define a separately named Level-B
   scalability/overlap diagnostic and do not call it Figure 10 reproduction.
3. Move to another paper blocker whose author-side denominator is stronger.
```

Any future Figure 10 execution goal should first produce an author-side
size/translate numeric matrix with clear input provenance.  Only then should
RTDL comparison or performance work begin.
