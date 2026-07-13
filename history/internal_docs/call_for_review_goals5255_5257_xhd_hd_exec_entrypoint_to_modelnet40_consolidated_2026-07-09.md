# Consolidated Call For Review - Goals5255-5257 X-HD RTDL hd_exec Entrypoint

Please strictly review Goals5255-5257 together.

## Scope

```text
Goal5255: add RTDL hd_exec-compatible user entrypoint
Goal5256: prove the entrypoint reaches bounded 3-D GPU routes on POD
Goal5257: prove the entrypoint runs a real public ModelNet40 OFF pair on POD
```

This packet addresses app usability and same-input functionality. It does not
claim full X-HD paper reproduction or performance parity.

## Files

Core implementation:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
Paper-reproduction-apps/x-hd-paper/README.md
```

Reports:

```text
history/internal_docs/goal5255_xhd_rtdl_hd_exec_compatible_entrypoint_result_2026-07-09.md
history/internal_docs/goal5256_xhd_rtdl_hd_exec_gpu_route_pod_smoke_result_2026-07-09.md
history/internal_docs/goal5257_xhd_rtdl_hd_exec_modelnet40_pair_result_2026-07-09.md
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

Goal5257 ModelNet40 pair:

```text
input1 = ModelNet40/airplane/train/airplane_0036.off
input2 = ModelNet40/airplane/train/airplane_0515.off
point_count_a = 370568
point_count_b = 376741
author rerun HDResult = 0.09761668741703033

cell-mbr-exact-witness:
  HDResult = 0.09761668669590366
  author_abs_diff = 7.211266722650933e-10
  per_source_witness_exact = true

cell-mbr-fast-scalar:
  HDResult = 0.09761668669590366
  author_abs_diff = 7.211266722650933e-10
  per_source_witness_exact = false
```

## Harsh Review Questions

1. Is this genuinely a user-facing app entrypoint, or just another gate wrapper?

2. Does it preserve the author-proven directed `input1 -> input2` HDResult
   contract?

3. Is one ModelNet40 pair enough only as an entrypoint bridge, while Goals5252-
   5254 remain the bulk all-400 evidence?

4. Are route labels mandatory and clear enough to avoid mixing scalar value
   correctness with exact-witness correctness?

5. Does `Running.AvgTime` create denominator confusion with the author's
   internal `Running.AvgTime`? If yes, require schema/wording amendments.

6. Does the packet avoid claiming exact paper byte-input identity, Figure
   reproduction, author RT-core equivalence, speedup, or performance parity?

7. Are the POD artifacts sufficient evidence that the entrypoint reaches real
   GPU route execution?

8. Should this packet be accepted as the current X-HD user-entrypoint milestone
   before the next algorithm/performance goal?

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
8. ...

Recommended verdict label:
...
```

## Proposed Verdict If Accepted

```text
approve_goals5255_5257_xhd_hd_exec_entrypoint_to_modelnet40_bridge
```
