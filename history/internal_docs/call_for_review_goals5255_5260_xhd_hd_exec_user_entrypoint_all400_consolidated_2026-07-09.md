# Consolidated Call For Review - Goals5255-5260 X-HD hd_exec User Entrypoint

Please strictly review Goals5255-5260 together.

## Scope

```text
Goal5255: RTDL hd_exec-compatible single-case entrypoint
Goal5256: bounded 3-D GPU route POD smoke
Goal5257: one real ModelNet40 OFF pair through the entrypoint
Goal5258: Running.AvgTime time-semantics hardening
Goal5259: first-3 ModelNet40 batch bridge
Goal5260: all-400 ModelNet40 batch bridge through the same entrypoint
```

This packet is the current X-HD user-entrypoint milestone.

## Key Result

```text
All 400 unique public ModelNet40 pair identities represented in the paper-branch
log index were run through the RTDL hd_exec-compatible batch bridge.

selected_case_count = 400
matched_case_count = 400
failed_case_count = 0
all_cases_matched = true
route_label = cell-mbr-exact-witness
```

Error against author reruns:

```text
max_author_abs_diff    = 6.59728109919655e-08
median_author_abs_diff = 7.368051571643441e-09
tolerance              = 1e-6
```

## Files

Implementation:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec_summary_batch.py
```

Primary evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json
```

Reports:

```text
history/internal_docs/goal5255_xhd_rtdl_hd_exec_compatible_entrypoint_result_2026-07-09.md
history/internal_docs/goal5256_xhd_rtdl_hd_exec_gpu_route_pod_smoke_result_2026-07-09.md
history/internal_docs/goal5257_xhd_rtdl_hd_exec_modelnet40_pair_result_2026-07-09.md
history/internal_docs/goal5258_xhd_hd_exec_running_time_semantics_hardening_result_2026-07-09.md
history/internal_docs/goal5259_xhd_hd_exec_summary_batch_bridge_result_2026-07-09.md
history/internal_docs/goal5260_xhd_hd_exec_all400_modelnet40_batch_result_2026-07-09.md
```

Tests:

```text
tests/goal5255_xhd_rtdl_hd_exec_entrypoint_test.py
tests/goal5256_xhd_rtdl_hd_exec_pod_artifact_test.py
tests/goal5257_xhd_rtdl_hd_exec_modelnet40_pod_artifact_test.py
tests/goal5259_xhd_rtdl_hd_exec_summary_batch_test.py
tests/goal5259_xhd_rtdl_hd_exec_modelnet40_batch_pod_artifact_test.py
tests/goal5260_xhd_hd_exec_all400_batch_artifact_test.py
```

## Harsh Review Questions

1. Does this finally make the RTDL X-HD app feel like a user-facing counterpart
   to author `hd_exec`, rather than a pile of gates?

2. Does Goal5260 legitimately supersede first-3 batch evidence for the
   user-entrypoint batch bridge?

3. Are route label and witness-contract claims correct?

4. Does the packet avoid the still-forbidden claims:

```text
full X-HD paper reproduction complete
exact paper byte-input identity proved
all paper datasets/Figures reproduced
author RT-core algorithm equivalence
performance parity/speedup
Running.AvgTime author-internal denominator parity
```

5. Is all-400 public ModelNet40 exact-witness coverage through the user
   entrypoint now strong enough to be the ModelNet40 functional anchor?

6. What remains before full paper reproduction can be claimed?

## Expected Answer Shape

```text
Verdict: approve | approve_with_required_amendments | revise | block

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Question answers:
1. ...
...
6. ...

Recommended verdict label:
...
```

## Proposed Verdict If Accepted

```text
approve_goals5255_5260_xhd_hd_exec_user_entrypoint_all400_modelnet40
```
