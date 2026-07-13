# Consolidated Call For Review - Goals5255-5262 X-HD hd_exec Entrypoint, All-400, Performance, And Docs

Date: 2026-07-09

## Review Scope

Please strictly review Goals5255-5262 as one X-HD user-entrypoint packet.

This supersedes the earlier Goals5255-5261 review packet by adding Goal5262's
README/manifest update.

## Goals Covered

```text
Goal5255: RTDL hd_exec-compatible single-case entrypoint.
Goal5256: bounded 3D GPU route POD smoke through the entrypoint.
Goal5257: one public ModelNet40 OFF pair through the entrypoint.
Goal5258: Running.AvgTime semantics hardening.
Goal5259: summary-driven batch bridge over the entrypoint.
Goal5260: all-400 public ModelNet40 batch through the entrypoint.
Goal5261: denominator-separated all-400 performance matrix.
Goal5262: README/manifest status update making the user entrypoint visible.
```

## Primary Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec_summary_batch.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_hd_exec_entrypoint_performance_matrix.py
Paper-reproduction-apps/x-hd-paper/README.md
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

Primary artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5261_hd_exec_entrypoint_all400_performance_matrix_2026-07-09.json
```

Primary reports:

```text
history/internal_docs/goal5255_xhd_rtdl_hd_exec_compatible_entrypoint_result_2026-07-09.md
history/internal_docs/goal5256_xhd_rtdl_hd_exec_gpu_route_pod_smoke_result_2026-07-09.md
history/internal_docs/goal5257_xhd_rtdl_hd_exec_modelnet40_pair_result_2026-07-09.md
history/internal_docs/goal5258_xhd_hd_exec_running_time_semantics_hardening_result_2026-07-09.md
history/internal_docs/goal5259_xhd_hd_exec_summary_batch_bridge_result_2026-07-09.md
history/internal_docs/goal5260_xhd_hd_exec_all400_modelnet40_batch_result_2026-07-09.md
history/internal_docs/goal5261_xhd_hd_exec_entrypoint_performance_matrix_result_2026-07-09.md
history/internal_docs/goal5262_xhd_user_entrypoint_docs_and_manifest_status_result_2026-07-09.md
```

## Central Claims

1. The X-HD RTDL paper app now has an app-owned `hd_exec`-compatible user
   entrypoint family.
2. The entrypoint family ran all 400 public ModelNet40 pair identities
   represented in the paper-branch log index through the exact-witness route:

```text
matched_case_count = 400
failed_case_count = 0
max_author_abs_diff = 6.59728109919655e-08
per_source_witness_exact = true for all 400 cases
```

3. The current denominator-separated performance statement is:

```text
RTDL hd_exec route-wall sum = 420.31053318828344 s
RTDL hd_exec batch case-wall sum = 600.8750001639128 s
Author process-wall sum = 255.03741998970509 s
Author internal Running.AvgTime sum = 2794.7910000000006 ms

RTDL route / author process-wall = 1.648034759782505x slower
RTDL route / author internal AvgTime = 150.3906850953375x slower
```

4. The README and manifest now expose this as the current paper-app user
   entrypoint status:

```text
xhd_public_modelnet40_all400_hd_exec_entrypoint_complete__full_paper_incomplete
```

5. The packet explicitly does **not** claim:

```text
full X-HD paper reproduction complete
exact original paper byte-input identity
all paper datasets reproduced
Figure 5-11 reproduced
author RT-core algorithm equivalence
author performance parity or speedup
```

## Review Questions

1. Is the user entrypoint faithful enough to the author's key `hd_exec` flags
   while remaining app-owned?
2. Is all-400 ModelNet40 functional evidence properly tied to public-data
   author reruns rather than exact paper byte-input identity?
3. Are the Timing/Running semantics strong enough to prevent denominator mixing?
4. Is the performance matrix fair and denominator-separated?
5. Does the new README status communicate progress without implying full paper
   completion?
6. Does the manifest keep all overclaim boundary flags false?
7. What next work should be required after this packet: exact paper dataset
   provenance, missing non-ModelNet40 datasets/Figures, or author RT-core
   internal AvgTime algorithm gap?

## Expected Verdict Labels

Preferred approval:

```text
approve_goals5255_5262_xhd_hd_exec_entrypoint_all400_performance_and_docs
```

Possible amendment:

```text
revise_goals5255_5262_due_to_entrypoint_docs_or_performance_boundary
```

Possible block:

```text
block_goals5255_5262_due_to_overclaimed_full_paper_or_mixed_denominator
```

Please provide:

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to review questions:
```
