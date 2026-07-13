# Consolidated Call For Review - Goals5255-5264 X-HD hd_exec Entrypoint

Date: 2026-07-09

## Review Scope

Please strictly review the current X-HD `hd_exec`-compatible RTDL entrypoint
packet, Goals5255 through 5264.

This packet supersedes the earlier Goals5255-5263 packet by adding Goal5264:
Stanford Graphics Dragon -> AsianDragon scaled same-source candidate through the
same user-facing entrypoint.

## Primary Files

Result reports:

```text
history/internal_docs/goal5261_xhd_hd_exec_entrypoint_performance_matrix_result_2026-07-09.md
history/internal_docs/goal5262_xhd_user_entrypoint_docs_and_manifest_status_result_2026-07-09.md
history/internal_docs/goal5263_xhd_hd_exec_graphics_dragon_happy_entrypoint_result_2026-07-09.md
history/internal_docs/goal5264_xhd_hd_exec_graphics_dragon_asian_entrypoint_result_2026-07-09.md
```

Goal-specific calls:

```text
history/internal_docs/call_for_review_goal5261_xhd_hd_exec_entrypoint_performance_matrix_2026-07-09.md
history/internal_docs/call_for_review_goal5262_xhd_user_entrypoint_docs_and_manifest_status_2026-07-09.md
history/internal_docs/call_for_review_goal5263_xhd_hd_exec_graphics_dragon_happy_entrypoint_2026-07-09.md
history/internal_docs/call_for_review_goal5264_xhd_hd_exec_graphics_dragon_asian_entrypoint_2026-07-09.md
```

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5261_hd_exec_entrypoint_all400_performance_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5263_dragon_happy_hd_exec_fast_scalar_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5263_dragon_happy_hd_exec_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5264_dragon_asian_hd_exec_exact_witness_pod.json
```

Tests:

```text
tests/goal5260_xhd_hd_exec_all400_batch_artifact_test.py
tests/goal5261_xhd_hd_exec_entrypoint_performance_matrix_test.py
tests/goal5262_xhd_user_entrypoint_docs_status_test.py
tests/goal5263_xhd_hd_exec_graphics_dragon_happy_pod_artifact_test.py
tests/goal5264_xhd_hd_exec_graphics_dragon_asian_pod_artifact_test.py
```

## Current Status To Review

The README and manifest now use:

```text
xhd_public_modelnet40_all400_and_graphics_representatives_hd_exec_entrypoint_complete__full_paper_incomplete
```

This status is intended to mean:

```text
complete: user-facing RTDL hd_exec-compatible entrypoint evidence on public ModelNet40 all-400 plus two Stanford Graphics representative gates
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

Performance matrix for all-400:

```text
RTDL route-wall sum = 420.31053318828344 s
RTDL batch case-wall sum = 600.8750001639128 s
Author process-wall sum = 255.03741998970509 s
Author internal Running.AvgTime sum = 2794.7910000000006 ms
route/process-wall = 1.648034759782505x slower
route/author-internal-AvgTime = 150.3906850953375x slower
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

## Claims To Attack

Please attack whether the status string is too strong. In particular:

1. Does "entrypoint complete" overstate what is done, given exact paper datasets
   and figures remain incomplete?
2. Are the ModelNet40, Dragon/Happy, and Dragon/Asian gates enough to justify
   saying the `hd_exec`-compatible user entrypoint is the primary RTDL app entry?
3. Are the denominator-labeled performance ratios in Goal5261 safe, or should
   they be moved out of the user-facing status?
4. Is Dragon/Asian acceptable as a scaled same-source candidate, given the
   visible paper-log drift?
5. Are `per_source_witness_exact` caveats for Dragon/Happy fast-scalar and exact
   routes clear enough?
6. Does the README/manifest preserve the no-full-paper / no-exact-dataset /
   no-author-parity boundary?
7. Is there any hidden app-specialization in RTDL core, or is this still an
   app-owned paper reproduction wrapper over generic RTDL routes?

## Forbidden Summaries

Please reject any summary that says:

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
approve_goals5255_5264_xhd_hd_exec_entrypoint_modelnet40_graphics_packet
```

Possible amendment:

```text
revise_goals5255_5264_due_to_status_or_denominator_boundary
```

Possible block:

```text
block_goals5255_5264_due_to_overclaimed_full_paper_or_invalid_graphics_comparator
```

Please provide:

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to review questions:
```
