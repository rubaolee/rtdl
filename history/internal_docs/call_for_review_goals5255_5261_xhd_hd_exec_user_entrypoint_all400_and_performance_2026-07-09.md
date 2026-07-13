# Consolidated Call For Review - Goals5255-5261 X-HD hd_exec User Entrypoint, All-400, and Performance Matrix

Date: 2026-07-09

## Review Scope

Please strictly review Goals5255-5261 as a consolidated X-HD user-entrypoint
packet.

This packet covers:

```text
Goal5255: RTDL hd_exec-compatible single-case entrypoint.
Goal5256: bounded 3D GPU route POD smoke through the entrypoint.
Goal5257: one public ModelNet40 OFF pair through the entrypoint.
Goal5258: Running.AvgTime semantics hardening.
Goal5259: summary-driven batch bridge over the entrypoint.
Goal5260: all-400 public ModelNet40 batch through the entrypoint.
Goal5261: denominator-separated all-400 performance matrix.
```

## Files To Review

Result reports:

```text
history/internal_docs/goal5255_xhd_rtdl_hd_exec_compatible_entrypoint_result_2026-07-09.md
history/internal_docs/goal5256_xhd_rtdl_hd_exec_gpu_route_pod_smoke_result_2026-07-09.md
history/internal_docs/goal5257_xhd_rtdl_hd_exec_modelnet40_pair_result_2026-07-09.md
history/internal_docs/goal5258_xhd_hd_exec_running_time_semantics_hardening_result_2026-07-09.md
history/internal_docs/goal5259_xhd_hd_exec_summary_batch_bridge_result_2026-07-09.md
history/internal_docs/goal5260_xhd_hd_exec_all400_modelnet40_batch_result_2026-07-09.md
history/internal_docs/goal5261_xhd_hd_exec_entrypoint_performance_matrix_result_2026-07-09.md
```

Call-for-review files:

```text
history/internal_docs/call_for_review_goal5255_xhd_rtdl_hd_exec_compatible_entrypoint_2026-07-09.md
history/internal_docs/call_for_review_goal5256_xhd_hd_exec_gpu_route_pod_smoke_2026-07-09.md
history/internal_docs/call_for_review_goal5257_xhd_hd_exec_modelnet40_pair_2026-07-09.md
history/internal_docs/call_for_review_goal5258_xhd_hd_exec_running_time_semantics_hardening_2026-07-09.md
history/internal_docs/call_for_review_goal5259_xhd_hd_exec_summary_batch_bridge_2026-07-09.md
history/internal_docs/call_for_review_goal5260_xhd_hd_exec_all400_modelnet40_batch_2026-07-09.md
history/internal_docs/call_for_review_goal5261_xhd_hd_exec_entrypoint_performance_matrix_2026-07-09.md
```

Implementation and evidence:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec_summary_batch.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_hd_exec_entrypoint_performance_matrix.py

Paper-reproduction-apps/x-hd-paper/results/xhd_goal5256_rtdl_hd_exec_bounded3d_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5256_rtdl_hd_exec_bounded3d_fast_scalar_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5257_modelnet40_airplane_0036_0515_exact_witness_hd_exec_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5257_modelnet40_airplane_0036_0515_fast_scalar_hd_exec_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5259_modelnet40_first3_hd_exec_batch_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5261_hd_exec_entrypoint_all400_performance_matrix_2026-07-09.json
```

Tests:

```text
tests/goal5255_xhd_rtdl_hd_exec_entrypoint_test.py
tests/goal5256_xhd_rtdl_hd_exec_pod_artifact_test.py
tests/goal5257_xhd_rtdl_hd_exec_modelnet40_pod_artifact_test.py
tests/goal5259_xhd_rtdl_hd_exec_summary_batch_test.py
tests/goal5259_xhd_rtdl_hd_exec_modelnet40_batch_pod_artifact_test.py
tests/goal5260_xhd_hd_exec_all400_batch_artifact_test.py
tests/goal5261_xhd_hd_exec_entrypoint_performance_matrix_test.py
```

## Central Claims To Review

1. The RTDL app now has an author-style `hd_exec`-compatible user entrypoint.
2. The entrypoint supports single-case and summary-driven batch execution.
3. Through that entrypoint family, all 400 public ModelNet40 pair identities
   represented in the paper-branch log index matched author rerun HDResult:

```text
400 / 400 matched
max_author_abs_diff = 6.59728109919655e-08
tolerance = 1e-6
per_source_witness_exact = true for all 400 under cell-mbr-exact-witness
```

4. Performance is denominator-separated:

```text
RTDL hd_exec route-wall sum = 420.31053318828344 s
RTDL hd_exec batch case-wall sum = 600.8750001639128 s
Author process-wall sum = 255.03741998970509 s
Author internal Running.AvgTime sum = 2794.7910000000006 ms

RTDL route / author process-wall = 1.648034759782505x slower
RTDL route / author internal AvgTime = 150.3906850953375x slower
```

5. The packet does **not** claim:

```text
full X-HD paper reproduction complete
exact paper byte-input identity proved
all X-HD paper datasets reproduced
Figure 5-11 reproduced
author RT-core algorithm equivalence
author performance parity or speedup
RTDL Running.AvgTime comparable to author internal Running.AvgTime
```

## Review Questions

1. Is the `hd_exec`-compatible entrypoint faithful enough as a user-facing RTDL
   app entrypoint while remaining app-owned rather than RTDL core behavior?
2. Are unsupported author modes rejected fail-closed rather than silently
   accepted?
3. Are the `Running.TimeSemantics` fields sufficient to prevent denominator
   confusion?
4. Does Goal5260 legitimately supersede first-3 batch smoke as the all-400
   user-entrypoint functional evidence?
5. Is Goal5261's performance matrix arithmetic correct and denominator-safe?
6. Should the 150.39x author-internal-AvgTime ratio remain in the main matrix
   as an explicit phase-gap warning, or be moved to an appendix to avoid misuse?
7. Does the consolidated packet preserve all prior X-HD claim boundaries,
   especially exact paper byte-input identity and full paper reproduction?
8. What should be the next required work after this packet:
   user documentation, exact paper dataset/Figure work, or algorithm/internal
   AvgTime gap analysis?

## Expected Verdict Labels

Preferred approval:

```text
approve_goals5255_5261_xhd_hd_exec_entrypoint_all400_and_denominator_safe_performance
```

Possible amendment:

```text
revise_goals5255_5261_due_to_entrypoint_or_timing_claim_boundary
```

Possible block:

```text
block_goals5255_5261_due_to_mixed_denominator_or_overclaimed_reproduction_status
```

Please provide:

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to review questions:
```
