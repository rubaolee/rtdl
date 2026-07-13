# Consolidated Call For Review - Goals5255-5266 X-HD hd_exec Entrypoint

Date: 2026-07-09

## Review Scope

Please strictly review the current X-HD `hd_exec`-compatible RTDL entrypoint
packet, Goals5255 through 5266.

This packet supersedes the earlier Goals5255-5265 packet by adding Goal5266:
ThaiStatuette scaled 1e-3 -> AsianDragon scaled 1e-3 through the same
user-facing RTDL entrypoint.

## Primary Result Reports

```text
history/internal_docs/goal5261_xhd_hd_exec_entrypoint_performance_matrix_result_2026-07-09.md
history/internal_docs/goal5262_xhd_user_entrypoint_docs_and_manifest_status_result_2026-07-09.md
history/internal_docs/goal5263_xhd_hd_exec_graphics_dragon_happy_entrypoint_result_2026-07-09.md
history/internal_docs/goal5264_xhd_hd_exec_graphics_dragon_asian_entrypoint_result_2026-07-09.md
history/internal_docs/goal5265_xhd_hd_exec_graphics_thai_happy_entrypoint_result_2026-07-09.md
history/internal_docs/goal5266_xhd_hd_exec_graphics_thai_asian_entrypoint_result_2026-07-09.md
```

## Primary Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5261_hd_exec_entrypoint_all400_performance_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5263_dragon_happy_hd_exec_fast_scalar_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5263_dragon_happy_hd_exec_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5264_dragon_asian_hd_exec_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5265_author_thai_happy_scaled_rt_gpu_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5265_thai_happy_hd_exec_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5266_author_thai_asian_scaled_rt_gpu_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5266_thai_asian_hd_exec_exact_witness_pod.json
```

## Current Status To Review

The README and manifest use:

```text
xhd_public_modelnet40_all400_and_graphics_representatives_hd_exec_entrypoint_complete__full_paper_incomplete
```

This is intended to mean:

```text
complete: user-facing RTDL hd_exec-compatible entrypoint evidence on public ModelNet40 all-400 plus multiple Stanford Graphics representative gates
not complete: exact paper byte-input identity, all paper datasets/Figures, author RT-core algorithm equivalence, author performance parity/speedup
```

## Evidence Summary

ModelNet40 all-400:

```text
case_count = 400
matched_case_count = 400
failed_case_count = 0
max_author_abs_diff = 6.59728109919655e-08
per_source_witness_exact = true for all cases
```

Dragon -> HappyBuddha:

```text
author rerun HDResult = 0.12572988867759705
RTDL HDResult = 0.12572988629271128
abs_diff ~= 2.38e-9
fast scalar route wall ~= 536.22 ms, per_source_witness_exact=false
exact witness route wall ~= 620.92 ms, per_source_witness_exact=true
point counts = 437645 / 543652
```

Dragon -> AsianDragon scaled 1e-3:

```text
author rerun HDResult = 0.06536787003278732
paper log HDResult = 0.06536811590194702
RTDL HDResult = 0.06536787240753439
abs(RTDL - author rerun) ~= 2.37e-9
RTDL route wall ~= 2651.05 ms
per_source_witness_exact = true
point counts = 437645 / 3609600
```

ThaiStatuette scaled 1e-3 -> HappyBuddha:

```text
paper log HDResult = 0.21912434697151184
author rerun HDResult = 0.21912431716918945
RTDL HDResult = 0.2191243235042005
abs(RTDL - author rerun) ~= 6.34e-9
RTDL route wall ~= 5013.23 ms
per_source_witness_exact = true
point counts = 4999996 / 543652
```

ThaiStatuette scaled 1e-3 -> AsianDragon scaled 1e-3:

```text
paper log HDResult = 0.28763845562934875
author rerun HDResult = 0.28763842582702637
RTDL HDResult = 0.2876384148709406
abs(RTDL - author rerun) ~= 1.10e-8
RTDL route wall ~= 10770.02 ms
per_source_witness_exact = true
point counts = 4999996 / 3609600
```

## Performance Boundary

The packet must not be read as author-performance parity:

```text
RTDL route wall is the RTDL selected route wall time.
Author Running.AvgTime is the author internal X-HD algorithm time.
No ratio is authorized unless the denominator and phase boundary are explicitly aligned.
```

Known denominator-labeled numbers:

```text
ModelNet40 all-400 RTDL route / author process-wall = 1.648x slower
ModelNet40 all-400 RTDL route / author internal AvgTime = 150.39x slower
ThaiStatuette -> AsianDragon RTDL route wall ~= 10.770s
ThaiStatuette -> AsianDragon author internal AvgTime = 18.864ms
```

## Review Questions

1. Is the `hd_exec`-compatible RTDL entrypoint now documented and tested as the
   user-facing X-HD paper-app route?
2. Do the ModelNet40 all-400 and Stanford Graphics representative gates support
   the stated status without overclaiming full paper reproduction?
3. Are all exact-witness graphics gates correctly marked
   `per_source_witness_exact=true`?
4. Does Goal5266 correctly add ThaiStatuette -> AsianDragon without promoting
   the scaled public candidate to exact paper byte-input identity?
5. Are timing denominators kept separate from author `Running.AvgTime`?
6. Are claim boundaries false for full paper reproduction, exact dataset
   identity, author RT-core equivalence, performance parity, and speedup?
7. Can Goals5255-5266 be marked `externally reviewed and approved`, or are
   amendments required?

## Expected Answer Shape

```text
Verdict: approve / approve_with_required_amendments / block
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to questions 1-7:
```
