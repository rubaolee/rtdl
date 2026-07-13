# Call For Review - Goal5261 X-HD hd_exec Entrypoint Performance Matrix

Date: 2026-07-09

## Review Scope

Please strictly review Goal5261, which builds a denominator-separated
performance matrix for the X-HD `hd_exec`-compatible all-400 ModelNet40 RTDL
entrypoint.

Primary result:

```text
history/internal_docs/goal5261_xhd_hd_exec_entrypoint_performance_matrix_result_2026-07-09.md
```

Code and evidence:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_hd_exec_entrypoint_performance_matrix.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5261_hd_exec_entrypoint_all400_performance_matrix_2026-07-09.json
tests/goal5261_xhd_hd_exec_entrypoint_performance_matrix_test.py

Input evidence:
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5253_modelnet40_all400_exact_seed_summary_2026-07-09.json
```

## Context

Goal5260 established that the RTDL `hd_exec`-compatible batch bridge matched
author rerun HDResult for all 400 public ModelNet40 pair identities under the
exact-witness route.

Goal5261 does not implement a new route. It reconciles the timing denominators:

```text
RTDL hd_exec-compatible route wall time
RTDL hd_exec-compatible case wall time
Author process wall time
Author internal Running.AvgTime
Older Goal5253 RTDL batch-harness route/total time
```

## Claims To Verify

1. The matrix is built from real Goal5260 and Goal5253 evidence and matches
   cases by `case_name`, failing closed on case-set mismatch.
2. The 400-case correctness envelope remains intact:

```text
matched_case_count = 400
per_source_witness_exact_case_count = 400
max_author_abs_diff <= 1e-6
```

3. Timing denominators are correctly separated:

```text
RTDL route-wall sum = 420.31053318828344 s
RTDL batch case-wall sum = 600.8750001639128 s
Author process-wall sum = 255.03741998970509 s
Author internal Running.AvgTime sum = 2794.7910000000006 ms
```

4. Ratios are denominator-labeled and not presented as speedup/parity claims:

```text
RTDL route sum / author process wall sum = 1.648034759782505x
RTDL case wall sum / author process wall sum = 2.356026814371663x
RTDL route sum / author internal Running.AvgTime sum = 150.3906850953375x
```

5. The matrix correctly shows that the hd_exec-compatible entrypoint route time
   is consistent with the older Goal5253 RTDL route evidence:

```text
RTDL hd_exec route sum / Goal5253 route sum = 0.9899840755927131x
```

6. The claim boundary remains strict:

```text
performance_parity_claimed = false
speedup_claimed = false
author_internal_avgtime_comparable_without_phase_review = false
exact_paper_dataset_identity_proved = false
full_xhd_paper_reproduction_claimed = false
all_paper_figures_reproduced = false
```

## Specific Review Questions

1. Is the matrix arithmetic correct and reproducible from the two input JSON
   artifacts?
2. Does matching by `case_name` provide the right fail-closed guard against
   accidental denominator mismatch?
3. Are the semantics of RTDL `Running.AvgTime` now clear enough that it cannot
   be confused with author internal `Running.AvgTime`?
4. Is the allowed performance statement fair:

```text
RTDL is about 1.65x slower than author process-wall sum by route-wall denominator,
and about 150.39x slower than author internal AvgTime by internal phase denominator.
```

5. Should the author internal AvgTime ratio be kept in the matrix as an explicit
   algorithm/phase-gap warning, or moved to an appendix to avoid misuse?
6. Does this matrix properly avoid claiming exact paper byte-input identity,
   Figure reproduction, or full X-HD paper reproduction?
7. Is it acceptable to use this matrix as the current all-400 performance
   statement for the RTDL `hd_exec`-compatible entrypoint, pending future exact
   dataset/Figure work?
8. Are there any remaining denominator or regime ambiguities that must be fixed
   before Goal5261 can be closed?

## Expected Verdict Labels

Preferred approval:

```text
approve_goal5261_hd_exec_entrypoint_performance_matrix_denominator_safe
```

Possible amendment:

```text
revise_goal5261_performance_matrix_denominator_or_claim_boundary
```

Possible block:

```text
block_goal5261_due_to_invalid_ratio_or_mixed_denominator
```

Please provide:

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to review questions:
```
