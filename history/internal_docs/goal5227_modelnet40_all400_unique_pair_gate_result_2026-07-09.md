# Goal5227 - ModelNet40 All-400 Unique-Pair Gate Result

Date: 2026-07-09

## Verdict

```text
completed_modelnet40_all400_unique_pair_gate__398_of_400_at_1e_minus_6
```

Goal5227 ran the full 400 unique ModelNet40 normalized-public-OFF pair set in
chunks using the Goal5226 operational controls.

This is a real all-400 execution result, but it is **not** a 400/400 pass under
the current strict `1e-6` float-author tolerance.

## Execution

POD:

```text
host = 213.173.108.24
port = 13502
gpu  = NVIDIA RTX 4000 Ada Generation
remote repo = /root/rtdl_goal5093
```

Runner:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_modelnet40_normalized_batch_gate.py
```

Execution controls:

```text
--selection-strategy all_unique_pairs
--max-pairs 400
--chunk-size 25
--skip-completed
--continue-on-error
--goal-label Goal5227
```

The run used 16 chunks:

```text
chunk 000 through chunk 015
25 cases per chunk
400 cases total
```

## Result

Aggregate summary:

```text
selected_count = 400
matched_case_count = 398
failed_case_count = 2
all_cases_matched = false
```

Numerical error distribution:

```text
max RTDL-vs-author HDResult diff = 1.4973206821644602e-06
p99 RTDL-vs-author HDResult diff = 2.3762976246455292e-07
```

Timing totals from the gate summaries:

```text
RTDL route_wall_sec sum = 433.2045598253608
RTDL full total_sec sum = 629.2800005152822
author process_wall_sec sum = 257.22060713917017
```

These timings are reported as operational measurements only. They are **not**
an author-vs-RTDL performance ratio or parity claim.

## Failed Cases At 1e-6

### Case 63

```text
case_name = 0063_bowl_0074__bowl_0037
category = bowl
total_points = 9,264
members = ModelNet40/bowl/test/bowl_0074.off
          ModelNet40/bowl/train/bowl_0037.off

author HDResult = 0.4035000503063202
RTDL route distance = 0.403498552985638
abs diff = 1.4973206821644602e-06

author-vs-paper diff = 0.0
MBR matched = true
algorithm matched = true
```

### Case 114

```text
case_name = 0114_curtain_0125__curtain_0081
category = curtain
total_points = 172,873
members = ModelNet40/curtain/train/curtain_0125.off
          ModelNet40/curtain/train/curtain_0081.off

author HDResult = 0.4707379639148712
RTDL route distance = 0.4707389724572476
abs diff = 1.0085423763905865e-06

author-vs-paper diff = 0.0
MBR matched = true
algorithm matched = true
```

Both failures are numeric-threshold failures just above `1e-6`, not author
rerun failures, MBR failures, algorithm-selection failures, missing input
failures, or route crashes.

## Evidence Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5227_modelnet40_all400_aggregate_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5227_modelnet40_all400_case_artifacts_2026-07-09.tar.gz
```

Earlier checkpoint artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5227_modelnet40_all400_chunk000_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5227_modelnet40_all400_aggregate_after_chunk000_summary_2026-07-09.json
```

## Claim Boundary

Allowed:

```text
The algorithm-aware public-OFF normalized ModelNet40 route completed all 400
unique pairs and matched 398/400 under the current strict 1e-6 tolerance.
```

Forbidden:

```text
ModelNet40 is 400/400 complete under the current 1e-6 tolerance.
All 2000 ModelNet40 paper-log records are complete.
Exact paper input byte identity is proved.
Author-vs-RTDL performance ratio or parity is established.
Full X-HD paper reproduction is complete.
```

## Next Step

Open a narrow tolerance/semantic audit for the two near-threshold failures.
The audit should decide whether the ModelNet40 float-author tolerance should
remain `1e-6`, become a justified looser absolute tolerance such as `2e-6`, or
use a relative/ULP-aware criterion.
