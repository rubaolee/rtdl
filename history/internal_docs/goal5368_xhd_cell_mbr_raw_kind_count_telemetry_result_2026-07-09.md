# Goal5368 - X-HD Cell-MBR Raw Kind-Count Telemetry Result

Date: 2026-07-09

## Verdict Label

```text
raw_kind_count_telemetry_ready__author_lb_denominator_still_unmatched
```

Exit label:

```text
raw_kind2_denominator_probe_shows_author_queue_state_gap
```

## Purpose

Goal5367 proved that simply forcing RTDL's `lb256` route radius to the author
iteration radius preserves the HD value but does not close the offload row
denominator gap.

Goal5368 adds the missing generic telemetry needed for the next question:

```text
When row materialization is disabled, how many raw native frontier rows are
kind2/offload rows before host download and host sort/unique?
```

This is a generic RTDL system telemetry improvement.  It is not an X-HD-specific
native primitive.

## Implementation

Native OptiX cell-MBR frontier telemetry now includes a v3 memory telemetry
getter:

```text
rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry_v3
```

New generic fields:

```text
raw_frontier_kind_counts
raw_frontier_kind1_rows
raw_frontier_kind2_rows
raw_frontier_kind3_rows
```

The counters are incremented in the generic `cell_mbr_nearest_frontier_3d`
any-hit path after the row kind is determined and before row output capacity is
checked.  They therefore remain available even when `row_capacity=0` and no
rows are downloaded.

Python now supports:

```text
allow_overflow_telemetry=True
```

Default behavior remains fail-closed.  Only an explicit diagnostic request
returns an overflow telemetry result without rows.

## POD Validation

POD:

```text
host = 213.173.108.24
port = 13502
remote workspace = /tmp/rtdl_goal5364
GPU = NVIDIA RTX 4000 Ada Generation
```

Validation steps:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
make build-optix
```

Small smoke:

```text
row_capacity = 0
allow_overflow_telemetry = true
expected raw kinds = one kind1, one kind2, one kind3
```

Observed:

```json
{"raw_frontier_kind_counts": {"1": 1, "2": 1, "3": 1}, "overflowed": true}
```

## Dragon -> AsianDragon Count-Only Probe

Command shape:

```text
input1 = /tmp/xhd_goal5234/data/dragon.ply
input2 = /tmp/xhd_goal5234/data/asian_dragon.ply
preprocessing = translate_each_input_to_min_bound
grid_shape = 96,60,72
grid_cell_builder = native_cuda
radius = 79.2156982421875
max_inline_points = 256
frontier_row_capacity = 0
inline_nearest = false
```

Downloaded POD artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5368_dragon_asian_lb256_author_radius_noinline_kind_count_pod.json
```

Summary artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5368_cell_mbr_raw_kind_count_telemetry.json
```

## Key Numbers

Author `lb256`:

```text
HDResult       = 52.453487396240234
OffloadingSize = 27133990
Radius         = 79.2156982421875
WL Heavy Peak  = 217071920
```

RTDL author-radius inline/materialized route from Goal5367:

```text
HDResult                = 52.453491321261296
heavy_offload_peak_rows = 21006960
```

RTDL author-radius no-inline/count-only raw frontier telemetry:

```text
attempted all kinds       = 589961522
raw_frontier_kind1_rows   = 284979633
raw_frontier_kind2_rows   = 304981889
raw_frontier_kind3_rows   = 0
```

Comparison:

```text
author OffloadingSize       = 27133990
RTDL raw kind2/offload rows = 304981889
RTDL / author               = 11.239846738352892
author - RTDL               = -277847899
row_count_parity            = false
```

## Interpretation

Goal5368 answers the immediate denominator question:

```text
The author OffloadingSize is not simply "all raw cell-MBR frontier rows whose
cell point_count > lb under the same scalar radius".
```

If it were, the no-inline raw kind2 count would be close to author
`27133990`.  Instead it is `304981889`, roughly `11.24x` author.

This also separates three denominators:

```text
author OffloadingSize rows                  = 27133990
RTDL author-radius inline materialized rows = 21006960
RTDL author-radius no-inline raw kind2 rows = 304981889
```

The remaining gap is therefore not:

- host row materialization;
- host sort/unique;
- scalar radius mismatch alone.

The next parity target is author iterative queue state:

```text
in_queue_idx
per-iteration cmin2 / current best state
radius schedule
raw offload emission semantics
```

## Claim Boundary

Allowed:

```text
Goal5368 adds generic raw frontier kind-count telemetry and shows that RTDL can
measure raw kind2/offload rows without materializing huge row tables.

The no-inline raw kind2 denominator is about 11.24x the author OffloadingSize
on the Dragon -> AsianDragon lb256 probe.
```

Not allowed:

```text
claiming explicit -lb support;
claiming row-count parity;
claiming same-denominator Figure 11 memory parity;
claiming Figure 7 or Figure 11 reproduction;
claiming author RT-core algorithm parity;
claiming a fair performance ratio;
claiming exact paper dataset reproduction;
claiming full X-HD paper reproduction.
```

## Validation

Local:

```text
py -m py_compile src/rtdsl/optix_runtime.py
py -m py_compile src/rtdsl/partner_continuations.py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_kind_count_probe.py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5368_cell_mbr_raw_kind_count_telemetry.py
py -m unittest tests.goal5368_cell_mbr_frontier_kind_count_telemetry_test tests.goal5368_lb_raw_kind_count_artifact_test tests.goal5367_lb_author_radius_probe_test tests.goal5366_lb_denominator_reconciliation_test tests.goal5365_rtdl_lb_counterpart_gate_test tests.goal5364_lb_trace_gate_author_pair_contract_test tests.goal5363_lb_heavy_offload_semantics_audit_test
```

Result:

```text
Ran 22 tests OK
```

POD:

```text
preflight OK
make build-optix OK
small raw-kind smoke OK
Dragon -> AsianDragon count-only probe OK
```

## Files

```text
src/native/optix/rtdl_optix_workloads.cpp
src/native/optix/rtdl_optix_prelude.h
src/rtdsl/optix_runtime.py
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_kind_count_probe.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5368_cell_mbr_raw_kind_count_telemetry.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5368_dragon_asian_lb256_author_radius_noinline_kind_count_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5368_cell_mbr_raw_kind_count_telemetry.json
tests/goal5368_cell_mbr_frontier_kind_count_telemetry_test.py
tests/goal5368_lb_raw_kind_count_artifact_test.py
```

## Next Work

Build an author-queue-aligned `lb` diagnostic that carries or reconstructs:

```text
in_queue_idx
cmin2/current best
per-iteration radius
raw offload queue rows
```

Goal5368 strongly suggests that matching the author denominator requires
matching author iteration state, not merely matching the scalar radius or
counting generic cells above the threshold.
