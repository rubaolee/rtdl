# Consolidated Call For Review - Goals5255-5259 X-HD hd_exec User Entrypoint

Please strictly review Goals5255-5259 together.

## Scope

```text
Goal5255: RTDL hd_exec-compatible single-case entrypoint
Goal5256: bounded 3-D GPU route POD smoke through that entrypoint
Goal5257: real ModelNet40 OFF pair through that entrypoint
Goal5258: Running.AvgTime time-semantics hardening
Goal5259: summary-driven batch bridge over the same entrypoint
```

This packet is the current X-HD user-entrypoint milestone. It is not full paper
reproduction and not a performance-parity packet.

## Key Evidence

ModelNet40 single pair through `run_xhd_rtdl_hd_exec.py`:

```text
airplane_0036.off -> airplane_0515.off
author rerun HDResult = 0.09761668741703033

cell-mbr-exact-witness:
  HDResult = 0.09761668669590366
  abs_diff = 7.211e-10
  per_source_witness_exact = true

cell-mbr-fast-scalar:
  HDResult = 0.09761668669590366
  abs_diff = 7.211e-10
  per_source_witness_exact = false
```

ModelNet40 first-3 batch through `run_xhd_rtdl_hd_exec_summary_batch.py`:

```text
selected_case_count = 3
matched_case_count = 3
failed_case_count = 0
all_cases_matched = true
route_label = cell-mbr-exact-witness
```

## Files

Implementation:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec_summary_batch.py
```

Reports:

```text
history/internal_docs/goal5255_xhd_rtdl_hd_exec_compatible_entrypoint_result_2026-07-09.md
history/internal_docs/goal5256_xhd_rtdl_hd_exec_gpu_route_pod_smoke_result_2026-07-09.md
history/internal_docs/goal5257_xhd_rtdl_hd_exec_modelnet40_pair_result_2026-07-09.md
history/internal_docs/goal5258_xhd_hd_exec_running_time_semantics_hardening_result_2026-07-09.md
history/internal_docs/goal5259_xhd_hd_exec_summary_batch_bridge_result_2026-07-09.md
```

Tests:

```text
tests/goal5255_xhd_rtdl_hd_exec_entrypoint_test.py
tests/goal5256_xhd_rtdl_hd_exec_pod_artifact_test.py
tests/goal5257_xhd_rtdl_hd_exec_modelnet40_pod_artifact_test.py
tests/goal5259_xhd_rtdl_hd_exec_summary_batch_test.py
tests/goal5259_xhd_rtdl_hd_exec_modelnet40_batch_pod_artifact_test.py
```

## Harsh Review Questions

1. Is this now a real user-facing app entrypoint, or still just gate machinery?
2. Does the batch bridge truly call the new entrypoint?
3. Are route labels and witness contracts strong enough?
4. Does `Running.TimeSemantics` close the author-AvgTime denominator trap?
5. Is the first-3 batch correctly framed as a bridge, not all-400 proof?
6. Do Goals5252-5254 remain the authoritative all-400 evidence?
7. Does the packet avoid exact paper identity, Figure reproduction, author
   RT-core equivalence, and performance parity claims?

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
7. ...

Recommended verdict label:
...
```

## Proposed Verdict If Accepted

```text
approve_goals5255_5259_xhd_hd_exec_user_entrypoint_and_batch_bridge
```
