# Consolidated Call For Review - Goals5255-5265 X-HD hd_exec Entrypoint

Date: 2026-07-09

## Review Scope

Please strictly review the current X-HD `hd_exec`-compatible RTDL entrypoint
packet, Goals5255 through 5265.

This packet supersedes the earlier Goals5255-5264 packet by adding Goal5265:
public Stanford ThaiStatuette acquisition/scaling plus ThaiStatuette ->
HappyBuddha through the same user-facing entrypoint.

## Primary Result Reports

```text
history/internal_docs/goal5261_xhd_hd_exec_entrypoint_performance_matrix_result_2026-07-09.md
history/internal_docs/goal5262_xhd_user_entrypoint_docs_and_manifest_status_result_2026-07-09.md
history/internal_docs/goal5263_xhd_hd_exec_graphics_dragon_happy_entrypoint_result_2026-07-09.md
history/internal_docs/goal5264_xhd_hd_exec_graphics_dragon_asian_entrypoint_result_2026-07-09.md
history/internal_docs/goal5265_xhd_hd_exec_graphics_thai_happy_entrypoint_result_2026-07-09.md
```

## Primary Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5261_hd_exec_entrypoint_all400_performance_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5263_dragon_happy_hd_exec_fast_scalar_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5263_dragon_happy_hd_exec_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5264_dragon_asian_hd_exec_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5265_thai_statuette_scaled_1e-3_candidate_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5265_author_thai_happy_scaled_rt_gpu_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5265_thai_happy_hd_exec_exact_witness_pod.json
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
author_abs_diff ~= 2.37e-9
rtdl_vs_paper_log_abs_diff ~= 2.43e-7
exact witness route wall ~= 2651.05 ms
per_source_witness_exact=true
point counts = 437645 / 3609600
```

ThaiStatuette scaled 1e-3 -> HappyBuddha:

```text
paper log HDResult = 0.21912434697151184
author rerun HDResult = 0.21912431716918945
RTDL HDResult = 0.2191243235042005
author_abs_diff ~= 6.34e-9
rtdl_vs_paper_log_abs_diff ~= 2.35e-8
exact witness route wall ~= 5013.23 ms
per_source_witness_exact=true
point counts = 4999996 / 543652
```

Performance matrix for ModelNet40 all-400:

```text
RTDL route-wall sum = 420.31053318828344 s
RTDL batch case-wall sum = 600.8750001639128 s
Author process-wall sum = 255.03741998970509 s
Author internal Running.AvgTime sum = 2794.7910000000006 ms
route/process-wall = 1.648034759782505x slower
route/author-internal-AvgTime = 150.3906850953375x slower
```

## Claims To Attack

Please attack whether the status string is too strong. In particular:

1. Does "entrypoint complete" overstate what is done, given exact paper datasets
   and figures remain incomplete?
2. Are ModelNet40 all-400 plus three graphics representative gates enough to
   justify saying `run_xhd_rtdl_hd_exec.py` is the primary RTDL app entry?
3. Are the scaled AsianDragon and scaled ThaiStatuette candidates documented
   enough to remain Level-B, not Level-C exact paper inputs?
4. Are performance numbers denominator-labeled and safely non-parity?
5. Does the README/manifest preserve no-full-paper / no-exact-dataset /
   no-author-parity boundaries?
6. Is there any hidden X-HD/author specialization in RTDL core, or are these
   app-owned paper reproduction wrappers over generic RTDL routes?

## Forbidden Summaries

Reject any summary that says:

```text
full X-HD paper reproduction is complete
RTDL matches the original paper inputs exactly
RTDL reproduces Figures 5-11
RTDL equals or beats author performance
RTDL implements the author X-HD RT-core algorithm
same-source/scaled public graphics candidates are exact paper datasets
```

## Expected Verdict Labels

Preferred approval:

```text
approve_goals5255_5265_xhd_hd_exec_entrypoint_modelnet40_graphics_packet
```

Possible amendment:

```text
revise_goals5255_5265_due_to_status_scaled_candidate_or_denominator_boundary
```

Possible block:

```text
block_goals5255_5265_due_to_overclaimed_full_paper_or_invalid_scaled_candidate
```

Please provide:

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to review questions:
```
