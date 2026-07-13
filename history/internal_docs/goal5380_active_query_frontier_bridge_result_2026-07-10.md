# Goal5380 Active-Query Frontier Bridge Result

Date: 2026-07-10

Status:

```text
implemented_review_pending
```

Exit label:

```text
active_query_frontier_bridge_ready__native_author_oracle_probe_next
```

## Purpose

Goal5379 created a generic CPU/NumPy active-query status-machine reference, but
that reference was still disconnected from the existing native cell-MBR
frontier row producer.

Goal5380 adds the missing bridge:

```text
generic cell-MBR frontier row table
  -> active-query candidate stream
  -> generic active-query status-machine reference
```

This is still not author-compatible explicit `-lb` support. It is the
app-neutral connection needed before a native/OptiX author-oracle row-parity
probe can be meaningful.

## What Was Implemented

New public contract:

```text
ACTIVE_QUERY_FRONTIER_BRIDGE_CONTRACT =
  "generic_active_query_status_from_frontier_rows_v1"
```

New public helper:

```text
active_query_status_from_frontier_row_table_numpy_columns(...)
```

Files changed:

```text
src/rtdsl/active_query_status.py
src/rtdsl/__init__.py
tests/goal5380_active_query_frontier_bridge_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5380_active_query_frontier_bridge.json
```

## Contract

The bridge consumes a generic cell-MBR frontier row table:

```text
query_row_ids
cell_ids
point_counts
min_distances
max_distances
optional frontier_kind_codes for metadata
```

It lowers those rows into Goal5379's active-query reference shape:

```text
candidate_query_row_ids = frontier query_row_ids
candidate_cell_ids      = frontier cell_ids
candidate_work_counts   = frontier point_counts
candidate_min_sq        = min_distances^2
candidate_max_sq        = max_distances^2
```

Optional per-row exact nearest results can be supplied:

```text
candidate_exact_best_sq
candidate_exact_item_ids
```

The reference then emits app-neutral rows:

```text
offload_rows
completed_rows
miss_rows
aborted_rows
updated_state
telemetry
```

## Validation

Commands:

```text
py -m py_compile src/rtdsl/active_query_status.py src/rtdsl/__init__.py

py -m unittest \
  tests.goal5380_active_query_frontier_bridge_test \
  tests.goal5379_active_query_status_machine_reference_test \
  tests.goal5279_generic_heavy_offload_worklist_test \
  tests.goal5280_heavy_offload_non_xhd_consumer_gate_test
```

Observed:

```text
Ran 16 tests OK
```

The known local Windows Python warning appeared:

```text
Could not find platform independent libraries <prefix>
```

It did not affect test success.

## What The Tests Cover

The focused Goal5380 tests verify:

```text
frontier rows lower into completed rows;
frontier rows lower into offload rows;
frontier rows lower into aborted rows under a global bound;
queries with no usable candidate lower into miss rows;
bad frontier tables fail closed;
frontier max distance < min distance fails closed;
the public API is exported;
the helper source remains app-neutral.
```

The app-neutral scan checks that the bridge helper does not contain:

```text
xhd
x-hd
hausdorff
paper
hd_exec
figure
```

## POD Preflight

The bridge itself is CPU/NumPy and does not require a native rebuild. However,
the next native row-parity probe does require POD, so a wrapper preflight was
run:

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

## Relationship To The Author `-lb` Oracle

Goal5374 remains the author oracle:

```text
ActiveInQueueSize              = 437645
RawOffloadRowsBeforeSortReduce = 27133990
RawOffloadRowsAuthorWidthBytes = 217071920
```

Goal5380 does not compare against those numbers yet. It creates the generic
frontier-to-status bridge required for the next comparison.

## What This Does Not Prove

Goal5380 does not prove:

```text
explicit author-compatible -lb support;
row-count parity against author OffloadingSize;
same-denominator Figure 11 memory parity;
Figure 7 reproduction;
Figure 11 reproduction;
author RT-core algorithm parity;
performance improvement;
native backend completion;
exact paper dataset reproduction;
full X-HD paper reproduction.
```

## Next Goal

Recommended next goal:

```text
Goal5381 native/OptiX active-query row-parity probe against Goal5374 author
oracle.
```

Goal5381 must:

```text
use app-neutral names;
use Goal5379/5380 contracts as semantic baselines;
compare raw offload rows against 27133990;
compare author-width bytes against 217071920;
report row parity explicitly;
keep explicit -lb unsupported unless parity is proven and reviewed.
```
