# Goal5381 Active-Query Frontier Bridge POD Probe Result

Date: 2026-07-10

Status:

```text
implemented_review_pending
```

Exit label:

```text
active_query_bridge_mismatch_classified__native_author_status_machine_needed
```

## Purpose

Goal5374 produced an author-side oracle for the X-HD Dragon -> AsianDragon
`lb=256` status-machine denominator:

```text
ActiveInQueueSize              = 437645
RawOffloadRowsBeforeSortReduce = 27133990
RawOffloadRowsAuthorWidthBytes = 217071920
```

Goal5379 then introduced a generic active-query/status-machine CPU reference.
Goal5380 connected generic cell-MBR frontier row tables into that reference.

Goal5381 is the first POD probe that feeds real native/OptiX frontier rows
through the Goal5380 bridge and compares the resulting offload rows to the
Goal5374 author oracle.

## What Was Implemented

New app-owned probe runner:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_active_query_frontier_bridge_probe.py
```

New focused test:

```text
tests/goal5381_active_query_frontier_bridge_probe_test.py
```

POD result artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5381_source64_bridge_smoke_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5381_source4096_bridge_smoke_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5381_full_bridge_probe_pod.json
```

The runner is deliberately app-owned because it chooses X-HD inputs and compares
against the X-HD author oracle. It uses generic RTDL system contracts internally:

```text
native cell-MBR frontier rows
-> active_query_status_from_frontier_row_table_numpy_columns
-> generic_active_query_status_machine_reference_v1
```

It does not expose or claim a public X-HD `-lb` option.

## Important Semantic Correction

While preparing Goal5381, the Goal5379 active-query reference was corrected to
preserve **multiple offload rows for one active query**.

That correction matters because author `OffloadingSize` is a raw appended row
count, not merely one terminal offload status per active query. A focused test
now verifies that one query with two heavy candidates emits two offload rows.

## Validation

Local validation:

```text
py -m py_compile src/rtdsl/active_query_status.py src/rtdsl/__init__.py \
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_active_query_frontier_bridge_probe.py

py -m unittest \
  tests.goal5381_active_query_frontier_bridge_probe_test \
  tests.goal5380_active_query_frontier_bridge_test \
  tests.goal5379_active_query_status_machine_reference_test \
  tests.goal5279_generic_heavy_offload_worklist_test \
  tests.goal5280_heavy_offload_non_xhd_consumer_gate_test
```

Observed:

```text
Ran 19 tests OK
```

POD wrapper preflight:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
```

Observed:

```text
POD_OK
container = 45c502cfccb5
GPU       = NVIDIA RTX 4000 Ada Generation
driver    = 550.127.05
```

Remote semantic smoke:

```text
OFFLOAD_ROWS 2
BRIDGE True
```

This confirms the remote POD used the corrected multiple-offload-row reference
and exposed the frontier bridge.

## POD Probe Matrix

All probes used:

```text
input1 = /tmp/xhd_goal5234/data/dragon.ply
input2 = /tmp/xhd_goal5234/data/asian_dragon.ply
radius = 79.2156982421875
grid_shape = 96,60,72
grid_cell_builder = native_cuda
max_inline_points = 256
inline_nearest = true
emit_pruned_rows = false
```

### Bounded Smoke: 64 Sources

```text
active_query_count  = 64
candidate_row_count = 1920
offload_row_count   = 320
total_sec           = 2.542511560022831
```

This proves the real native frontier -> active-query bridge path runs on POD,
but it is source-limited and cannot establish author row parity.

### Bounded Smoke: 4096 Sources

```text
active_query_count  = 4096
candidate_row_count = 122880
offload_row_count   = 20480
total_sec           = 2.1508705019950867
```

This shows the same scaling pattern at a larger bounded size.

### Full Dragon -> AsianDragon Probe

```text
active_query_count       = 437645
candidate_row_count      = 13129392
bridge_offload_row_count = 2188225
author_offload_rows      = 27133990
row_count_parity         = false
row_ratio_rtdl_div_author = 0.08064516129032258
row_delta_author_minus_rtdl = 24945765
```

Author-width bytes:

```text
author raw offload bytes = 217071920
RTDL bridge bytes        = 17505800
byte parity              = false
```

Timings:

```text
load_inputs          = 0.3800610303878784s
grid_cell_mbrs       = 1.0808746218681335s
frontier_rows        = 11.371281310915947s
active_query_bridge  = 19.95744337886572s
total                = 32.79359517246485s
```

## Interpretation

Goal5381 is valuable precisely because it moves the `-lb` discussion from
guesswork to a concrete author-oracle comparison.

The result is negative:

```text
current native frontier rows + generic active-query bridge do not match author
OffloadingSize.
```

The active query count matches the author active queue size:

```text
437645 == 437645
```

But the offload row denominator is far too small:

```text
2,188,225 vs 27,133,990
```

This is not a small tolerance issue. It is a different denominator / execution
model issue.

The likely missing piece is not the CPU bridge itself. The larger issue is that
the native row stream being fed to the bridge is not the author's raw status
machine stream. It is the current RTDL frontier stream after inline-nearest /
active-row filtering under `emit_pruned_rows=false`.

In other words:

```text
Goal5381 proves the bridge can run,
but it also proves the current frontier stream is not author-compatible -lb.
```

## What This Does Not Prove

Goal5381 does not prove:

```text
explicit author-compatible -lb support;
row-count parity against author OffloadingSize;
same-denominator Figure 11 memory parity;
Figure 7 reproduction;
Figure 11 reproduction;
author RT-core algorithm parity;
performance improvement;
native status-machine backend completion;
exact paper dataset reproduction;
full X-HD paper reproduction.
```

## Claim Boundary

Allowed:

```text
RTDL has a generic active-query/status-machine reference and a generic
frontier-row bridge.
The bridge has been exercised on real POD native frontier rows.
The full Dragon -> AsianDragon probe does not match the Goal5374 author oracle.
The next implementation must change the native status-machine stream or build a
native/vectorized active-query backend closer to the author semantics.
```

Not allowed:

```text
RTDL supports X-HD -lb.
RTDL matches author OffloadingSize.
RTDL reproduces Figure 7.
RTDL reproduces Figure 11.
RTDL matches author memory denominator.
RTDL has full X-HD paper reproduction.
```

## Next Work

Recommended next goal:

```text
Goal5382 - native author-status-machine stream design / vectorized bridge
decision.
```

Goal5382 should choose between:

```text
1. Native status-machine stream:
   modify the generic native cell-MBR traversal to emit the right status-shaped
   raw stream before the current active-row filtering collapses the denominator.

2. Vectorized active-query bridge:
   keep the current native frontier stream but move the active-query transition
   work out of Python loops. This would reduce bridge runtime, but by itself it
   will not solve the row-parity mismatch.

3. Fail-closed explicit -lb closeout:
   if the project chooses not to implement a native status-machine stream, keep
   explicit -lb unsupported and document the remaining denominator gap.
```

The current evidence points most strongly to option 1. The CPU bridge runtime is
not ideal, but the decisive problem is row denominator mismatch, not only speed.
