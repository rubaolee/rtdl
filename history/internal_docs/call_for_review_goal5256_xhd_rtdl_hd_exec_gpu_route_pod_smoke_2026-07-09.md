# Call For Review - Goal5256 X-HD RTDL hd_exec GPU Route POD Smoke

Please strictly review Goal5256.

## Files Under Review

```text
history/internal_docs/goal5256_xhd_rtdl_hd_exec_gpu_route_pod_smoke_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5256_rtdl_hd_exec_bounded3d_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5256_rtdl_hd_exec_bounded3d_fast_scalar_pod.json
tests/goal5256_xhd_rtdl_hd_exec_pod_artifact_test.py
```

Goal5255 files are prerequisite context:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
history/internal_docs/call_for_review_goal5255_xhd_rtdl_hd_exec_compatible_entrypoint_2026-07-09.md
```

## Context

Goal5255 added a user-facing RTDL runner that mirrors the author `hd_exec` key
flags and writes author-shaped JSON. Goal5256 verifies on a live GPU POD that
the same runner can execute bounded 3-D GPU RTDL route labels, not only the CPU
public-columnar route.

## Questions

1. Do the POD artifacts prove that the new `run_xhd_rtdl_hd_exec.py` entrypoint
   can execute bounded 3-D GPU route labels through the author-style CLI?

2. Are the two route labels separated clearly enough?

```text
cell-mbr-fast-scalar
cell-mbr-exact-witness
```

3. Is it acceptable that `cell-mbr-fast-scalar` reports
   `per_source_witness_exact=true` on this tiny bounded fixture, as long as the
   report explicitly says this is not a general property of the route?

4. Do both JSON artifacts retain the author-shaped top-level fields `HDResult`
   and `Running`, while also retaining explicit `RTDL` route metadata?

5. Are the claim-boundary flags sufficient to prevent reading this POD smoke as
   full paper reproduction, author RT-core equivalence, or performance parity?

6. Is `Running.AvgTime` too easy to misread as author internal AvgTime? If so,
   what wording should be tightened before this runner is documented as the user
   entrypoint?

7. Are the artifact tests strong enough for this bounded smoke, or should they
   also assert more detailed nested route fields?

8. Does this goal remain app-owned, without promoting X-HD or `hd_exec`
   semantics into RTDL core?

9. Should Goal5256 be accepted as a live-GPU execution proof for the Goal5255
   entrypoint?

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
9. ...

Recommended verdict label:
...
```

## Proposed Verdict If Accepted

```text
approve_goal5256_xhd_rtdl_hd_exec_gpu_route_pod_smoke
```
