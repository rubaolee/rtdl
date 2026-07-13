# Goal5390 X-HD Full Trace Summary Gate Result

Date: 2026-07-10

## Verdict

```text
implemented_review_pending
```

## Summary

Goal5390 runs the X-HD active-query bridge probe on the full Dragon ->
AsianDragon source set, with no `--source-limit`, and emits the Goal5388 generic
trace summary from actual RTDL offload rows.

This supersedes Goal5389 for the full-parity question.  Goal5389 proved the
trace-summary plumbing on 64 sources; Goal5390 proves the current full-source
RTDL stream still does **not** match the Goal5387 author trace v2 oracle.

Key result:

```text
active_query_count_parity = true
row_count_parity          = false
hash_parity               = false
explicit_lb_support       = false
```

## Artifacts

Primary artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5390_full_trace_summary_gate.json
```

Raw POD artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5390_full_trace_summary_pod.json
```

Implementation and tests:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_active_query_frontier_bridge_probe.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5390_full_trace_summary_gate.py
tests/goal5390_full_trace_summary_gate_test.py
```

Prior evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_execution.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5389_bridge_trace_summary_smoke.json
```

## POD Execution

POD wrapper preflight was used:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
```

Observed:

```text
POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

The run used:

```text
input1 = /tmp/xhd_goal5234/data/dragon.ply
input2 = /tmp/xhd_goal5234/data/asian_dragon.ply
source_limit = none
grid_shape = 96,60,72
grid_cell_builder = native_cuda
grid_cell_point_order = input-stable
initial_state = local-grid-cell
local_grid_seed_executor = native_cuda
radius = 79.2156982421875
max_inline_points = 256
frontier_row_capacity = 30000000
inline_nearest = true
frontier_status_probe_mode = active-initial-best-prune
author_oracle = xhd_goal5387_author_trace_v2_execution.json
```

The raw POD summary was downloaded to:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5390_full_trace_summary_pod.json
```

## Author Trace V2 Target

From Goal5387:

```text
active_in_queue_size                  = 437645
raw_offload_rows_before_sort_reduce   = 27133990
status_count_offloading_append        = 27133990
raw_offload_row_hash                  = 4333109858711462591
raw_offload_row_sample_point_ids      = [11168, 210712, 437119]
raw_offload_row_sample_cell_ids       = [2924, 17, 17]
```

## RTDL Full-Source Trace Summary

Goal5390 emits:

```text
contract = generic_active_query_status_trace_summary_v1
active_query_count = 437645
row_count = 2188225
status_count_offloading = 2188225
raw_offload_row_hash = 10510374331443640811
sample_indices = [0, 1094112, 2188224]
sample source_ids = [18080, 219488, 437599]
sample cell_ids = [6279, 6286, 6145]
```

Frontier row context:

```text
frontier row_count = 2600727
frontier attempted_count = 2600727
frontier overflowed = false
native_symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v6
frontier_status_probe_contract = generic_active_query_initial_best_status_probe
```

## Comparison

```text
active_query_count_parity = true

author raw offload rows = 27133990
RTDL bridge offload rows = 2188225
row delta = 24945765
row ratio RTDL / author = 0.08064516129032258
row_count_parity = false

author raw hash = 4333109858711462591
RTDL raw hash = 10510374331443640811
hash_parity = false

author sample point ids = [11168, 210712, 437119]
RTDL sample source ids = [18080, 219488, 437599]
sample_comparable_to_author = true
```

This means the full-source bridge is now comparable to the author v2 trace at
the active-count / row-count / hash-sample level, but the actual RTDL status
stream is still not the author status-machine stream.

## Timing

The timing is diagnostic only and must not be used as a paper performance
comparison:

```text
load_inputs = 0.34597449004650116 s
grid_cell_mbrs = 0.44852539151906967 s
initial_seed = 0.14327648282051086 s
frontier_rows = 1.12689857929945 s
active_query_bridge = 9.771344847977161 s
total = 11.840128637850285 s
```

The bridge cost is not the main correctness blocker. The blocker is semantic
denominator mismatch:

```text
2188225 RTDL offload rows != 27133990 author raw offload rows
```

## Verification

Built artifact:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5390_full_trace_summary_gate.py
```

Focused tests:

```text
py -m unittest \
  tests.goal5390_full_trace_summary_gate_test \
  tests.goal5389_bridge_trace_summary_smoke_test \
  tests.goal5388_active_query_trace_summary_test \
  tests.goal5381_active_query_frontier_bridge_probe_test
```

Observed:

```text
Ran 12 tests in 1.267s
OK
```

## Claim Boundary

Allowed:

```text
Goal5390 is a full-source trace-summary gate.
The RTDL bridge now emits comparable full-source active-query trace summary
fields.
The active query count matches the author trace v2 oracle.
The row count, row hash, and row samples do not match.
```

Forbidden:

```text
Do not claim explicit -lb support.
Do not claim row-count parity.
Do not claim hash/sample parity.
Do not claim Figure 7 or Figure 11 reproduction.
Do not claim same-denominator memory.
Do not claim author RT-core algorithm parity.
Do not claim author-vs-RTDL performance ratio.
Do not claim exact paper dataset reproduction.
Do not claim full X-HD paper reproduction.
```

## Decision

Goal5390 closes the "maybe source-limited plumbing hid the issue" question.
It did not.

The full-source stream reaches:

```text
active_query_count = 437645
```

but it still emits:

```text
RTDL offload rows = 2188225
author offload rows = 27133990
```

Therefore explicit X-HD `-lb` remains unsupported. The next step is either:

```text
1. implement a genuine generic native multi-round status stream that changes
   the row denominator toward the author trace v2 oracle; or
2. close explicit -lb as unsupported under the current RTDL execution model.
```

## Exit Label

```text
native_status_stream_denominator_mismatch__lb_remains_unsupported
```
