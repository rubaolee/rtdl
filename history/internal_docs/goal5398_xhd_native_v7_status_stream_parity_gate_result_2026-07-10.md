# Goal5398 - X-HD Native v7 Status-Stream Parity Gate Result

Date: 2026-07-10

## Goal

Goal5398 tests whether the new generic native v7 active-query status-stream
front door from Goal5397 can match the Goal5387 author trace v2 oracle for the
Dragon -> AsianDragon Level-B public workload.

The test is intentionally narrow:

- compare active-query status-stream rows against the author trace v2 oracle;
- report row-count and hash/sample parity or mismatch;
- keep explicit X-HD `-lb` support fail-closed unless the native v7 stream
  matches the author denominator and hash/sample evidence.

## Inputs

POD:

```text
host = 213.173.108.24
port = 13502
preflight = POD_OK
GPU = NVIDIA RTX 4000 Ada Generation
```

Dataset:

```text
input1 = /tmp/xhd_goal5234/data/dragon.ply
input2 = /tmp/xhd_goal5234/data/asian_dragon.ply
point_count_a = 437645
point_count_b = 3609600
```

Author oracle:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_execution.json
author_active_in_queue_size = 437645
author_raw_offload_rows_before_sort_reduce = 27133990
author_raw_offload_row_hash = 4333109858711462591
author_status_count_offloading = 27133990
author_feedback_update_count = 294
```

RTDL route:

```text
grid_shape = 96,60,72
grid_cell_builder = native_cuda
grid_cell_point_order = input-stable
initial_state = local-grid-cell
local_grid_seed_executor = native_cuda
max_inline_points = 256
inline_nearest = true
frontier_status_probe_mode = active-initial-best-prune
row_capacity = 30000000
```

## Validation

POD focused tests:

```text
python3 -m unittest \
  tests.goal5398_native_v7_status_stream_parity_gate_test \
  tests.goal5397_native_status_stream_frontdoor_test

Ran 11 tests in 0.503s
OK (skipped=1)
```

POD native build:

```text
make build-optix
succeeded
```

Local focused tests after artifact download:

```text
$env:PYTHONPATH='src'; py -m unittest \
  tests.goal5398_native_v7_status_stream_parity_gate_test \
  tests.goal5397_native_status_stream_frontdoor_test \
  tests.goal5396_v6_remap_no_go_test \
  tests.goal5395_native_status_stream_abi_gate_test

Ran 19 tests in 3.105s
OK
```

## Artifacts

Full-public POD gate:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5398_native_v7_status_stream_parity_gate_pod.json
```

Bounded POD smoke:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5398_native_v7_status_stream_parity_gate_bounded_pod.json
```

## Full-Public Result

The native v7 stream does not match the Goal5387 author trace v2 oracle.

```text
status = native_v7_status_stream_denominator_or_hash_mismatch__lb_remains_fail_closed
matched = false
active_query_count_parity = true
row_count_parity = false
hash_parity = false
status_count_offloading_parity = false

author rows = 27133990
RTDL v7 rows = 2600727
row_delta_author_minus_rtdl_v7 = 24533263
RTDL/author row ratio = 0.09584756978240207

author raw hash = 4333109858711462591
RTDL v7 raw hash = 12842101464127179321

author sample point ids = [11168, 210712, 437119]
author sample cell ids  = [2924, 17, 17]
RTDL sample source ids  = [3872, 219882, 437567]
RTDL sample cell ids    = [6145, 6292, 6292]
```

Timing for the full-public Goal5398 gate:

```text
load_inputs = 0.34794603288173676 s
grid_cell_mbrs = 0.46031779795885086 s
initial_seed = 0.14132925122976303 s
native_v7_status_stream = 3.873375818133354 s
total = 7.417583808302879 s
```

## Bounded Smoke Result

The bounded smoke with `source_limit=64` also intentionally does not match the
full author trace oracle.

```text
point_count_a = 64
point_count_b = 3609600
RTDL rows = 384
author rows = 27133990
active_query_count_parity = false
row_count_parity = false
hash_parity = false
```

This smoke is useful only for proving the script and native v7 call path run
and produce a valid summary.

## Interpretation

Goal5398 is a negative but useful result.

It proves:

- the native v7 status-stream front door builds and runs on POD;
- full-public active query count matches the author oracle;
- the row denominator and row hash do not match the author explicit `-lb`
  status stream;
- explicit `-lb` support must remain fail-closed.

It does not prove:

- explicit X-HD `-lb` support;
- row-count parity;
- row hash or sample parity;
- Figure 7 reproduction;
- Figure 11 reproduction;
- performance parity;
- exact paper dataset reproduction;
- full X-HD paper reproduction.

## Next Gate

The next useful work is not another syntactic ABI smoke. The gap is semantic:

```text
author status stream: 27133990 rows = 62 rows per active query
RTDL v7 status stream: 2600727 rows ~= 5.94 rows per active query
```

Goal5399 should inspect the author status-machine semantics and decide whether
to build a generic native status-state machine that can emit the same explicit
load-balance/offloading stream, or to stop the explicit `-lb` parity line and
close the current X-HD work as Level-B scalar correctness plus partial
algorithm evidence.

## Status Label

```text
completed_native_v7_status_stream_parity_gate__denominator_hash_mismatch__explicit_lb_fail_closed
```
