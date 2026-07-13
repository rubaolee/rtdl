# Call For Review - Goal5258 X-HD hd_exec Running Time Semantics Hardening

Please strictly review Goal5258.

## Files Under Review

```text
history/internal_docs/goal5258_xhd_hd_exec_running_time_semantics_hardening_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
tests/goal5255_xhd_rtdl_hd_exec_entrypoint_test.py
tests/goal5256_xhd_rtdl_hd_exec_pod_artifact_test.py
tests/goal5257_xhd_rtdl_hd_exec_modelnet40_pod_artifact_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5256_rtdl_hd_exec_bounded3d_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5256_rtdl_hd_exec_bounded3d_fast_scalar_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5257_modelnet40_airplane_0036_0515_exact_witness_hd_exec_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5257_modelnet40_airplane_0036_0515_fast_scalar_hd_exec_pod.json
```

## Question

Does Goal5258 adequately prevent the author-shaped `Running.AvgTime` field in
the RTDL JSON from being misread as author internal `Running.AvgTime` parity?

## Specific Review Points

1. Are the new fields machine-readable and visible enough?

```text
Running.TimeSemantics
Running.Repeats[].TimeSemantics
Running.Repeats[].Iterations[].TimeSemantics
RTDL.running_avg_time_semantics
```

2. Do the refreshed POD artifacts actually contain those fields?

3. Do the tests now enforce the presence of the denominator warning?

4. Is the wording strong enough to block performance/parity misuse?

5. Does this preserve author-shaped JSON compatibility while adding RTDL-specific
   metadata?

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
5. ...

Recommended verdict label:
...
```

## Proposed Verdict If Accepted

```text
approve_goal5258_xhd_hd_exec_running_time_semantics_hardening
```
