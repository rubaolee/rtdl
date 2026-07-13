# Goal5258 - X-HD hd_exec Running Time Semantics Hardening

Date: 2026-07-09

## Objective

Prevent the author-shaped `Running.AvgTime` field in the RTDL
`hd_exec`-compatible JSON from being misread as the author's internal
`Running.AvgTime` denominator.

This is a schema/wording hardening goal. It does not change the route algorithm.

## Change

Updated:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
```

New fields:

```text
Running.TimeSemantics
Running.Repeats[].TimeSemantics
Running.Repeats[].Iterations[].TimeSemantics
RTDL.running_avg_time_semantics
```

Core text:

```text
Running.AvgTime is populated for author-shaped JSON compatibility, but it is
RTDL route wall time for the selected route label. It must not be compared to
author internal Running.AvgTime without an explicit phase-boundary review.
```

## Refreshed POD Artifacts

Regenerated with the new semantics fields:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5256_rtdl_hd_exec_bounded3d_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5256_rtdl_hd_exec_bounded3d_fast_scalar_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5257_modelnet40_airplane_0036_0515_exact_witness_hd_exec_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5257_modelnet40_airplane_0036_0515_fast_scalar_hd_exec_pod.json
```

Verification:

```text
All four refreshed artifacts contain Running.TimeSemantics and
RTDL.running_avg_time_semantics.
```

## Tests Updated

```text
tests/goal5255_xhd_rtdl_hd_exec_entrypoint_test.py
tests/goal5256_xhd_rtdl_hd_exec_pod_artifact_test.py
tests/goal5257_xhd_rtdl_hd_exec_modelnet40_pod_artifact_test.py
```

New assertions require:

```text
"RTDL route wall time" in Running.TimeSemantics
"not be compared to author internal" in RTDL.running_avg_time_semantics
```

## Claim Boundary

Allowed:

```text
The RTDL hd_exec-compatible JSON now carries explicit time-semantics metadata
so author-shaped Running.AvgTime cannot be honestly quoted as author internal
AvgTime parity.
```

Forbidden:

```text
Running.AvgTime is comparable to author Running.AvgTime
Running.AvgTime proves speedup/parity
POD artifact timings are a performance headline
```

## Status

```text
implemented_review_pending
```
