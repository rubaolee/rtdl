# Consolidated Call For Review - Goals5255-5256 X-HD RTDL hd_exec Entrypoint

Please strictly review Goals5255-5256 together.

## Scope

Goal5255 adds the app-owned RTDL `hd_exec`-compatible entrypoint.
Goal5256 validates that entrypoint on a live GPU POD for bounded 3-D route
labels.

This packet should be reviewed as an app usability / execution-contract
milestone, not as a full paper-reproduction or performance-parity claim.

## Files

Goal5255:

```text
history/internal_docs/goal5255_xhd_rtdl_hd_exec_compatible_entrypoint_result_2026-07-09.md
history/internal_docs/call_for_review_goal5255_xhd_rtdl_hd_exec_compatible_entrypoint_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
tests/goal5255_xhd_rtdl_hd_exec_entrypoint_test.py
Paper-reproduction-apps/x-hd-paper/README.md
```

Goal5256:

```text
history/internal_docs/goal5256_xhd_rtdl_hd_exec_gpu_route_pod_smoke_result_2026-07-09.md
history/internal_docs/call_for_review_goal5256_xhd_rtdl_hd_exec_gpu_route_pod_smoke_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5256_rtdl_hd_exec_bounded3d_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5256_rtdl_hd_exec_bounded3d_fast_scalar_pod.json
tests/goal5256_xhd_rtdl_hd_exec_pod_artifact_test.py
```

## What Must Be Judged Harshly

1. Does the new runner really improve the user-facing paper app shape, or is it
   just another internal gate with a friendlier name?

2. Does it preserve the proven directed `input1 -> input2` `HDResult` contract?

3. Does the author-shaped `Running.AvgTime` field create a misleading
   denominator risk? If so, require wording or schema amendments.

4. Are route labels mandatory and clear enough to avoid collapsing:

```text
public-columnar
cell-mbr-fast-scalar
cell-mbr-exact-witness
```

5. Do the POD artifacts prove real GPU route execution through this entrypoint?

6. Does the runner remain app-owned, with no X-HD / hd_exec / paper semantics
   promoted into RTDL core?

7. Does the package avoid all forbidden claims:

```text
full X-HD paper reproduction complete
exact paper dataset identity proven
author RT-core algorithm equivalence
author performance parity
unlabeled RTDL performance number
```

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
approve_goals5255_5256_xhd_rtdl_hd_exec_entrypoint_and_gpu_smoke
```
