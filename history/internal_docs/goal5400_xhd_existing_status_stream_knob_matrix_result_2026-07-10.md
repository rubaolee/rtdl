# Goal5400 - X-HD Existing Status-Stream Knob Matrix Result

Date: 2026-07-10

## Goal

Goal5400 tests whether the current generic native v7 active-query status-stream
front door can reach the author explicit `-lb` denominator by changing existing
generic knobs before implementing a new status-state machine.

This is a pre-implementation matrix:

- do not add new native code;
- vary only existing generic knobs;
- compare row denominator and hash against the Goal5387 author trace v2 oracle;
- keep explicit `-lb` fail-closed unless row/hash parity is proven.

## Author Oracle

```text
author active queries = 437645
author raw offload rows = 27133990
author raw hash = 4333109858711462591
author feedback updates = 294
```

Oracle file:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_execution.json
```

## POD

```text
host = 213.173.108.24
port = 13502
preflight = POD_OK
GPU = NVIDIA RTX 4000 Ada Generation
```

Input:

```text
input1 = /tmp/xhd_goal5234/data/dragon.ply
input2 = /tmp/xhd_goal5234/data/asian_dragon.ply
point_count_a = 437645
point_count_b = 3609600
```

## Matrix

All successful runs use:

```text
grid_shape = 96,60,72
grid_cell_builder = native_cuda
grid_cell_point_order = input-stable
initial_state = local-grid-cell
local_grid_seed_executor = native_cuda
max_inline_points = 256
row_capacity = 30000000
```

| Case | inline | emit_pruned | probe mode | Rows | Ratio vs author | Hash parity | Outcome |
|---|---:|---:|---|---:|---:|---|---|
| Goal5398 baseline | true | false | active-initial-best-prune | 2,600,727 | 0.0958475698 | false | under-count |
| default/no-inline | false | false | default | 2,600,727 | 0.0958475698 | false | under-count |
| default/inline | true | false | default | 2,188,225 | 0.0806451613 | false | under-count |
| heavy-before-inline-prune | true | false | heavy-before-inline-prune | overflow attempted 3,102,465,405 | 114.34x attempted | n/a | over-count / fail-closed |
| active-initial + emit-pruned | true | true | active-initial-best-prune | overflow attempted 6,436,445,015 | 237.28x attempted | n/a | over-count / fail-closed |

Successful artifact files:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5398_native_v7_status_stream_parity_gate_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5400_probe_default_no_inline_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5400_probe_default_inline_pod.json
```

Overflow evidence:

```text
heavy-before-inline-prune:
  RuntimeError: attempted 3102465405; capacity 30000000;
  failure_mode=fail_closed_overflow; partial_result_returned=False

active-initial-best-prune + emit_pruned_rows:
  RuntimeError: attempted 6436445015; capacity 30000000;
  failure_mode=fail_closed_overflow; partial_result_returned=False
```

## Interpretation

The existing knob surface does not contain the author explicit `-lb` stream:

- existing no-pruned-row modes under-count by about 10x to 12.4x;
- emit-pruned / heavy-before-inline surfaces over-count by about 114x to 237x;
- none of the tested configurations are close to the author denominator;
- none match the author raw hash.

This confirms the Goal5399 conclusion:

```text
The gap is not an ABI bug, hash-order bug, or simple parameter setting.  It is
a semantic mismatch between author raw shader offload append rows and RTDL's
current frontier/status emission points.
```

## Decision

Proceed only with a real generic status-state machine implementation if the
project continues the `-lb` line.

Do not spend further goals on remapping the current v7 rows or trying nearby
knob combinations.

Decision label:

```text
existing_status_stream_knobs_exhausted__generic_status_state_machine_required_or_stop
```

## Claim Boundary

Allowed summary:

```text
Goal5400 shows that existing generic status-stream knobs do not reproduce the
Goal5387 author explicit -lb denominator. Current modes either under-count
badly or over-count by orders of magnitude. A true generic status-state machine
is required if the -lb line continues.
```

Forbidden summaries:

```text
RTDL supports explicit -lb.
RTDL matches author OffloadingSize.
Figure 7 or Figure 11 is reproduced.
The knob matrix found an author-compatible mode.
Over-counted overflow rows can be sampled into author parity.
Full X-HD paper reproduction is complete.
```
