# Goal5259 - X-HD hd_exec Summary Batch Bridge Result

Date: 2026-07-09

## Objective

Provide a batch bridge that drives the new RTDL `hd_exec`-compatible entrypoint
over cases from an existing evidence summary. This makes the user-facing
entrypoint usable for representative batches without rewriting the already
validated ModelNet40 selection/extraction logic.

This is an app usability and evidence-integration step, not a new algorithm
optimization.

## Implemented

New app-owned script:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec_summary_batch.py
```

It reads a summary with `cases[*].public_paths` and author HD values, invokes:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
```

for each selected case, and writes a batch summary.

The bridge does not add ModelNet40, X-HD, or `hd_exec` semantics to RTDL core.

## Local Tests

```text
py -m unittest tests.goal5259_xhd_rtdl_hd_exec_summary_batch_test
```

This test uses a small directed WKT case to prove the bridge is not hardwired
to ModelNet40.

## POD Batch

Source summary:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5253_modelnet40_all400_exact_seed_summary_2026-07-09.json
```

Command:

```text
cd /tmp/rtdl_goal5236
export PYTHONPATH=src:.
export LD_LIBRARY_PATH=build:${LD_LIBRARY_PATH:-}
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec_summary_batch.py \
  --case-summary Paper-reproduction-apps/x-hd-paper/results/xhd_goal5253_modelnet40_all400_exact_seed_summary_2026-07-09.json \
  --summary /tmp/xhd_goal5259_modelnet40_first3_hd_exec_batch_exact_witness.json \
  --max-cases 3 \
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
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5259_modelnet40_first3_hd_exec_batch_exact_witness_pod.json
```

Result:

```text
selected_case_count = 3
matched_case_count = 3
failed_case_count = 0
all_cases_matched = true
```

Cases:

```text
0000_airplane_0036__airplane_0515
  rtdl_hd_result = 0.09761668669590366
  author_abs_diff = 7.211266722650933e-10
  per_source_witness_exact = true
  Running.AvgTime = 696.9386786222458 ms

0001_airplane_0144__airplane_0384
  rtdl_hd_result = 0.1666227493856342
  author_abs_diff = 6.375113270618016e-09
  per_source_witness_exact = true
  Running.AvgTime = 499.0488365292549 ms

0002_airplane_0384__airplane_0569
  rtdl_hd_result = 0.5679504193198579
  author_abs_diff = 8.212338142854492e-09
  per_source_witness_exact = true
  Running.AvgTime = 9002.206914126873 ms
```

The third case is slow, matching earlier all-400 evidence for this case. This
is evidence that the bridge is exercising the same route family, not a new
performance result.

## Claim Boundary

Allowed claim:

```text
The RTDL hd_exec-compatible entrypoint can be driven over a small ModelNet40
batch selected from the all-400 evidence summary; the first three cases matched
author rerun HDResult under the exact-witness route label.
```

Forbidden claims:

```text
the hd_exec-compatible batch bridge has reproduced all 400 cases
the bridge replaces Goals5252-5254 as all-400 evidence
the batch proves performance parity or speedup
the batch proves exact paper byte-input identity
full X-HD paper reproduction is complete
```

## Status

```text
implemented_review_pending
```

## Next Recommended Work

1. Send Goals5255-5259 for strict review as the current X-HD user-entrypoint
   packet.
2. If accepted, decide whether all-400 should be rerun through the
   hd_exec-compatible bridge for UX consistency. This is optional because
   Goals5252-5254 remain the bulk all-400 evidence.
3. Continue the real hard work: exact paper dataset/Figure blockers and the
   author internal AvgTime algorithm gap.
