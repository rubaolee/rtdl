# Goal5374 - X-HD Author `-lb` Status-Trace Oracle Result

Date: 2026-07-10

Status:

```text
author_lb_status_trace_oracle_ready__rtdl_status_machine_counterpart_missing
```

Exit label:

```text
author_oracle_ready__next_rtdl_status_machine_counterpart
```

## Purpose

Goal5374 instruments the author X-HD RT path to expose the missing `-lb`
status-machine denominator fields identified by Goals5369-5373.

This is the author-oracle path, not RTDL `-lb` support. The goal answers:

```text
What does the author program itself count as raw lb offload rows, status counts,
and author-width queue bytes on the Dragon -> AsianDragon lb=256 diagnostic?
```

## Inputs

POD:

```text
host = 213.173.108.24
port = 13502
wrapper = scripts/current_pod_ssh.py
gpu = NVIDIA RTX 4000 Ada Generation
```

Author source/build used for instrumentation:

```text
author source = /tmp/xhd-goal5112/author
author binary = /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec
```

Input pair:

```text
input1 = /tmp/xhd_goal5234/data/dragon.ply
input2 = /tmp/xhd_goal5234/data/asian_dragon.ply
variant = rt
execution = gpu
lb = 256
normalize = false
check = true
```

Local artifacts:

```text
Paper-reproduction-apps/x-hd-paper/scripts/instrument_xhd_author_lb_status_trace.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5374_author_lb_status_trace_oracle.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5374_author_instrument_patch_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5374_author_lb256_status_trace_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5374_author_lb_status_trace_oracle.json
tests/goal5374_author_lb_status_trace_instrumentation_test.py
tests/goal5374_author_lb_status_trace_oracle_test.py
```

## What Was Implemented

An app-owned author instrumentation patcher was added:

```text
Paper-reproduction-apps/x-hd-paper/scripts/instrument_xhd_author_lb_status_trace.py
```

The patcher modifies only the external author source tree on the POD. It does
not modify RTDL core. It adds marker:

```text
RTDL_GOAL5374_LB_STATUS_TRACE
```

POD patch summary:

```text
patched = true
changed.launch_parameters = true
changed.shader = true
changed.rt_impl = true
```

The instrumentation adds author-side counters for:

```text
active in_queue size
raw offload rows before sort/reduce
author-width raw offload queue bytes
status init count
status offloading append count
cmax2 MBR abort count
point-loop early-break count
```

The patched author binary was rebuilt and run on the Dragon -> AsianDragon
`lb=256` diagnostic.

## Result

Goal5374 produced:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5374_author_lb_status_trace_oracle.json
```

Key author iteration-3 fields:

```text
NumInputPoints = 437645
NumOutputPoints = 0
Radius = 79.2156982421875
OffloadingSize = 27133990
RTTime = 46.679 ms
CUDATime = 77.58 ms
ComparedPoints = 1241945719
Hits = 896287932
```

Author `LBTrace`:

```text
ActiveInQueueSize = 437645
RawOffloadRowsBeforeSortReduce = 27133990
RawOffloadRowsAuthorWidthBytes = 217071920
StatusInitCount = 437645
StatusOffloadingAppendCount = 27133990
StatusCmax2MbrAbortCount = 0
StatusPointLoopEarlyBreakCount = 0
```

Internal oracle parity:

```text
RawOffloadRowsBeforeSortReduce == OffloadingSize == 27133990
StatusOffloadingAppendCount == OffloadingSize == 27133990
RawOffloadRowsAuthorWidthBytes == 27133990 * 2 * sizeof(uint32_t)
RawOffloadRowsAuthorWidthBytes == 217071920
ActiveInQueueSize == StatusInitCount == NumInputPoints == 437645
```

This is the first concrete author-side oracle for the missing `-lb`
status-machine denominator.

## Comparison With Existing RTDL Evidence

The current RTDL evidence still does not match the author oracle:

```text
Author raw offload rows / OffloadingSize      = 27133990
RTDL author-radius inline kind2 rows          = 21006960
RTDL author-radius no-inline raw kind2 rows   = 304981889
```

Therefore:

```text
rtdl_counterpart_row_parity = false
rtdl_surface_ready_from_goal5373 = false
explicit_lb_support_authorized = false
```

The author oracle is ready. The RTDL status-machine counterpart is not ready.

## Validation

Commands:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5374_author_lb_status_trace_oracle.py
py -m unittest tests.goal5374_author_lb_status_trace_instrumentation_test tests.goal5374_author_lb_status_trace_oracle_test tests.goal5373_rtdl_status_machine_telemetry_surface_test tests.goal5372_author_shader_status_machine_gap_test tests.goal5371_inline_global_bound_lb_probe_test
```

Observed:

```text
Ran 17 tests OK
```

The local Python warning:

```text
Could not find platform independent libraries <prefix>
```

is the known Windows Python environment noise and did not affect test success.

## Claim Boundary

Allowed:

```text
Author-side status-machine oracle is ready for Dragon -> AsianDragon lb=256.
Author raw offload rows equal author OffloadingSize on this instrumented run.
Author-width raw offload bytes equal OffloadingSize * 2 * sizeof(uint32_t).
Next valid step is an RTDL status-machine counterpart against this oracle.
```

Not allowed:

```text
explicit -lb support
RTDL row-count parity
same-denominator Figure 11 memory parity
Figure 7 reproduction
Figure 11 reproduction
author RT-core algorithm parity
RTDL/author performance ratio
exact paper dataset reproduction
full X-HD paper reproduction
```

The instrumented author timing is not a performance headline. Instrumentation
changes the author code path and is used only to expose oracle fields.

## Next Goal

Recommended next goal:

```text
Goal5375 - RTDL status-machine counterpart against Goal5374 author oracle
```

Minimum Goal5375 fields:

```text
active_in_queue_size
raw_offload_rows_before_sort_reduce
raw_offload_rows_author_width_bytes
status_count_init
status_count_offloading
status_count_aborted
miss_queue_count
cmax2_mbr_abort_count
point_loop_early_break_count
current_best_state_source
row_count_parity_against_author_offloading_size
```

Goal5375 must either establish row-count parity against the Goal5374 oracle or
produce a precise denominator mismatch explanation. Until then, explicit `-lb`
must remain unsupported.
