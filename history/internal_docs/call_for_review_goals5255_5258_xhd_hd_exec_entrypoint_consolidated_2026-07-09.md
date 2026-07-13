# Consolidated Call For Review - Goals5255-5258 X-HD RTDL hd_exec Entrypoint

Please strictly review Goals5255-5258 together.

## Scope

```text
Goal5255: add RTDL hd_exec-compatible user entrypoint
Goal5256: prove bounded 3-D GPU route execution through the entrypoint
Goal5257: prove a real ModelNet40 OFF pair through the entrypoint
Goal5258: harden Running.AvgTime time semantics to prevent denominator misuse
```

## Files

Implementation:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
Paper-reproduction-apps/x-hd-paper/README.md
```

Reports:

```text
history/internal_docs/goal5255_xhd_rtdl_hd_exec_compatible_entrypoint_result_2026-07-09.md
history/internal_docs/goal5256_xhd_rtdl_hd_exec_gpu_route_pod_smoke_result_2026-07-09.md
history/internal_docs/goal5257_xhd_rtdl_hd_exec_modelnet40_pair_result_2026-07-09.md
history/internal_docs/goal5258_xhd_hd_exec_running_time_semantics_hardening_result_2026-07-09.md
```

POD artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5256_rtdl_hd_exec_bounded3d_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5256_rtdl_hd_exec_bounded3d_fast_scalar_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5257_modelnet40_airplane_0036_0515_exact_witness_hd_exec_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5257_modelnet40_airplane_0036_0515_fast_scalar_hd_exec_pod.json
```

Tests:

```text
tests/goal5255_xhd_rtdl_hd_exec_entrypoint_test.py
tests/goal5256_xhd_rtdl_hd_exec_pod_artifact_test.py
tests/goal5257_xhd_rtdl_hd_exec_modelnet40_pod_artifact_test.py
```

## Evidence Summary

The entrypoint now:

```text
accepts author-style key flags
writes HDResult + Running author-shaped JSON
stores route labels and claim boundaries under RTDL
labels Running.AvgTime as RTDL route wall time, not author internal AvgTime
runs bounded 3-D GPU route labels on POD
runs a real public ModelNet40 OFF pair on POD
```

ModelNet40 pair:

```text
airplane_0036.off -> airplane_0515.off
author rerun HDResult = 0.09761668741703033

cell-mbr-exact-witness:
  HDResult = 0.09761668669590366
  abs_diff = 7.211266722650933e-10
  per_source_witness_exact = true

cell-mbr-fast-scalar:
  HDResult = 0.09761668669590366
  abs_diff = 7.211266722650933e-10
  per_source_witness_exact = false
```

## Harsh Review Questions

1. Is this genuinely a user-facing paper-app entrypoint?
2. Does it preserve directed `input1 -> input2` HDResult semantics?
3. Does one ModelNet40 pair remain correctly scoped as an entrypoint bridge,
   not all-400 proof?
4. Are route labels strong enough to prevent scalar/exact-witness confusion?
5. Does Goal5258 fully close the `Running.AvgTime` denominator-confusion risk?
6. Do the POD artifacts prove real GPU execution through the entrypoint?
7. Does the package avoid exact paper identity, Figure, author RT-core parity,
   and performance speedup claims?

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
approve_goals5255_5258_xhd_hd_exec_entrypoint_hardened_and_modelnet40_bridged
```
