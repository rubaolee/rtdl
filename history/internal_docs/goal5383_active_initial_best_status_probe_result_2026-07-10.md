# Goal5383 Active-Initial-Best Status Probe Result

Date: 2026-07-10

Status:

```text
implemented_review_pending
```

Exit label:

```text
active_initial_best_probe_no_go__offload_denominator_still_mismatch
```

## Purpose

Goal5381 proved that current native cell-MBR frontier rows plus the generic
active-query bridge under-count author `-lb` offload rows:

```text
RTDL bridge offload rows = 2188225
author offload rows      = 27133990
ratio                    = 0.08064516129032258
```

Goal5383 tests one specific hypothesis:

```text
Maybe RTDL under-counts because native traversal keeps pruning with the
payload-updated nearest best, while author -lb classifies heavy/offload rows
against the active-query entry current-best state.
```

To test this without adding an X-HD-specific primitive, Goal5383 adds a generic
native probe mode:

```text
frontier_status_probe_mode = active-initial-best-prune
frontier_status_probe_contract = generic_active_query_initial_best_status_probe
```

## What Was Implemented

Native / runtime:

```text
src/native/optix/rtdl_optix_workloads.cpp
src/rtdsl/optix_runtime.py
```

App-owned probe runner update:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_active_query_frontier_bridge_probe.py
```

Focused tests:

```text
tests/goal5383_active_initial_best_status_probe_test.py
```

POD artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5383_source64_active_initial_best_probe_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5383_source64_seeded_active_initial_best_probe_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5383_full_seeded_active_initial_best_probe_pod.json
```

## Implementation Summary

The new native mode is app-neutral:

```text
active-initial-best-prune
generic_active_query_initial_best_status_probe
```

It changes the status probe semantics from:

```text
use traversal-updated payload best when deciding whether a candidate is pruned
or offloaded
```

to:

```text
use the active-query entry current_best_distance for the status/offload
classification probe
```

The X-HD probe runner also gained optional seeding:

```text
--initial-state none | local-grid-cell
--local-grid-seed-executor auto | numpy | numba | native_cuda
```

This matters because `active-initial-best-prune` with `current_best=inf`
degenerates toward a no-prune over-count. The seeded mode supplies a finite
generic local-grid current-best entry state.

## Validation

Local:

```text
py -m py_compile \
  src/rtdsl/optix_runtime.py \
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_active_query_frontier_bridge_probe.py \
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_kind_count_probe.py

py -m unittest \
  tests.goal5383_active_initial_best_status_probe_test \
  tests.goal5382_status_machine_stream_design_test \
  tests.goal5381_active_query_frontier_bridge_probe_test \
  tests.goal5377_frontier_status_probe_mode_test
```

Observed:

```text
Ran 15 tests OK
```

POD:

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

Native build:

```text
cd /tmp/rtdl_goal5364 && make build-optix
```

Remote focused test:

```text
python -m unittest tests.goal5383_active_initial_best_status_probe_test
Ran 3 tests OK
```

## POD Results

All POD probes use Dragon -> AsianDragon and compare against the Goal5374
author `lb=256` oracle.

### Source-Limited 64, No Seed

```text
active_query_count  = 64
candidate_row_count = 453696
offload_row_count   = 320
row_count_parity    = false
total_sec           = 2.3423210829496384
```

This confirms that `active-initial-best-prune` with `current_best=inf` is not a
valid full-route denominator probe. It greatly increases candidate rows and is
only a smoke test.

### Source-Limited 64, Local-Grid Seed

```text
active_query_count  = 64
candidate_row_count = 384
offload_row_count   = 320
row_count_parity    = false
total_sec           = 1.3199886083602905
```

Seeding prevents the no-prune explosion, but the offload pattern remains the
same as the earlier bridge surface for this bounded sample.

### Full Dragon -> AsianDragon, Local-Grid Seed

```text
active_query_count        = 437645
candidate_row_count       = 2600727
bridge_offload_row_count  = 2188225
author_offload_rows       = 27133990
row_count_parity          = false
row_ratio_rtdl_div_author = 0.08064516129032258
total_sec                 = 10.155782833695412
```

This is the decisive result:

```text
active-initial-best-prune does not change the full offload denominator.
```

The full seeded probe still emits:

```text
2188225 offload rows
```

which is the same offload count as Goal5381 and only about 8.06 percent of the
author denominator.

## Interpretation

Goal5383 is a no-go for the tested hypothesis.

Rejected explanation:

```text
The Goal5381 under-count is not fixed by switching the status/offload
classification from traversal-updated payload best to active-query entry
current-best.
```

What remains likely:

```text
the author denominator depends on state-machine iteration / queue feedback /
loadBalanceProcessing semantics not represented by a single-pass cell-MBR
frontier stream.
```

Therefore the next native work should not keep adding one-off prune modes.
It should implement the Goal5382 design more literally:

```text
generic active-query status stream with explicit raw status transitions and
continuation feedback, or close explicit -lb fail-closed.
```

## Claim Boundary

Allowed summary:

```text
Goal5383 adds and tests a generic active-initial-best status probe. It preserves
correct app/core boundaries and runs on POD, but it does not improve author
offload row parity. The full seeded probe still emits 2188225 offload rows
versus the author's 27133990, so explicit -lb remains unsupported.
```

Forbidden summaries:

```text
Goal5383 implements explicit -lb.
Goal5383 matches author OffloadingSize.
Goal5383 reproduces Figure 7 or Figure 11.
Goal5383 completes X-HD paper reproduction.
Goal5383 proves performance parity.
```

## Next Work

Goal5384 should be one of:

```text
1. a real generic multi-round active-query status-stream prototype with queue
   feedback and raw transition telemetry; or
2. an explicit fail-closed closeout for X-HD -lb in the current reproduction
   line.
```

Do not continue with local prune-mode variants unless new evidence identifies a
specific missing transition that the variant tests.
