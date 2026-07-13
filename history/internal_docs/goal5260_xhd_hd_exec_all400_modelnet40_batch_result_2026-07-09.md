# Goal5260 - X-HD hd_exec-Compatible All-400 ModelNet40 Batch Result

Date: 2026-07-09

## Objective

Run the entire 400 unique ModelNet40 pair set through the new RTDL
`hd_exec`-compatible batch bridge, so the user-facing entrypoint owns the same
bulk correctness evidence previously held only by the older batch harness.

This goal is about entrypoint completeness and bulk correctness. It is not a
performance-parity claim.

## Command

POD:

```text
NVIDIA RTX 4000 Ada Generation
remote worktree = /tmp/rtdl_goal5236
```

Command:

```text
cd /tmp/rtdl_goal5236
export PYTHONPATH=src:.
export LD_LIBRARY_PATH=build:${LD_LIBRARY_PATH:-}
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec_summary_batch.py \
  --case-summary Paper-reproduction-apps/x-hd-paper/results/xhd_goal5253_modelnet40_all400_exact_seed_summary_2026-07-09.json \
  --summary /tmp/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness.json \
  --rtdl-route cell-mbr-exact-witness \
  --n-dims 3 \
  --input-type off \
  --execution gpu \
  --normalize-each-input-to-author-unit-box \
  --author-float32-normalization \
  --grid-shape 96,60,72
```

Downloaded artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json
```

## Result

```text
selected_case_count = 400
matched_case_count = 400
failed_case_count = 0
all_cases_matched = true
```

Numerical error against author reruns:

```text
max_author_abs_diff    = 6.59728109919655e-08
median_author_abs_diff = 7.368051571643441e-09
sum_author_abs_diff    = 4.472201816704025e-06
tolerance              = 1e-6
```

Route timing from the RTDL `Running.AvgTime` fields:

```text
median_running_avg_time_ms = 675.8961826562881
sum_running_avg_time_ms    = 420310.53318828344
max_running_avg_time_ms    = 13892.487451434135
batch_elapsed_sec          = 600.8786783665419
```

Important denominator warning:

```text
Running.AvgTime is RTDL route wall time for the selected route label.
It is not author internal Running.AvgTime parity.
```

## What This Changes

Before this goal:

```text
Goals5252-5254 held all-400 ModelNet40 evidence through the older batch harness.
Goals5255-5259 proved the hd_exec-compatible entrypoint on bounded cases,
one ModelNet40 pair, and first-3 batch bridge.
```

After this goal:

```text
The hd_exec-compatible batch bridge itself has all-400 ModelNet40 exact-witness
coverage: 400 / 400 matched author rerun HDResult.
```

This is a meaningful paper-app usability milestone: the same user-facing RTDL
entrypoint family now supports single-case and all-400 batch execution.

## Claim Boundary

Allowed claim:

```text
The RTDL hd_exec-compatible batch bridge matched author reruns for all 400
unique public ModelNet40 pair identities represented in the paper-branch log
index under the exact-witness route label.
```

Allowed with caveat:

```text
This gives user-entrypoint all-400 coverage for the public ModelNet40 rerun
contract. It still does not prove exact paper byte-input identity.
```

Forbidden claims:

```text
full X-HD paper reproduction complete
all X-HD paper datasets reproduced
exact paper byte-input identity proved
Figure 5-11 reproduced
author RT-core algorithm equivalence
performance parity or speedup
Running.AvgTime comparable to author internal Running.AvgTime
```

## Validation

Artifact test:

```text
py -m unittest tests.goal5260_xhd_hd_exec_all400_batch_artifact_test
```

Expected assertions:

```text
400 / 400 matched
route_label = cell-mbr-exact-witness
per_source_witness_exact = true for every case
max author_abs_diff <= 1e-6
Running.TimeSemantics present for every case
claim-boundary flags remain false for paper/performance overclaims
```

## Status

```text
implemented_review_pending
```

## Next Recommended Work

1. Send Goal5260 for strict review.
2. If accepted, update the X-HD README to make the hd_exec-compatible runner
   the primary RTDL app entrypoint.
3. Continue beyond ModelNet40: exact paper dataset/Figure blockers and the
   author internal AvgTime algorithm gap remain open.
