# Goal5410 X-HD Statused Large-Cell Deferral Stream Probe Result

Date: 2026-07-10

Status:

```text
synthetic_app_neutral_status_stream_gate_passed__bounded_xhd_gate_pending
```

## Purpose

Goal5409 authorized exactly one more generic semantic probe:

```text
statused_large_cell_deferral_stream
```

Goal5410 starts with the first required gate only:

```text
synthetic app-neutral status stream gate
```

It does not attempt the bounded X-HD sample-row gate or the full Goal5387
author parity gate yet.

## Artifacts

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5410_statused_large_cell_deferral_stream_probe.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5410_statused_large_cell_deferral_stream_probe.json
tests/goal5410_statused_large_cell_deferral_stream_probe_test.py
```

## Implementation

Goal5410 reuses the existing RTDL generic API:

```text
rtdsl.active_query_status_machine_reference_numpy_columns
rtdsl.active_query_status_trace_summary_numpy_columns
```

It does **not** introduce a new X-HD primitive.

Synthetic fixture:

```text
active queries       = 5
candidate rows       = 5
heavy_threshold      = 5
radius_sq            = 100.0
global_bound_sq      = 2.0
```

The fixture exercises all required generic status outcomes:

```text
offload rows         = 2
completed rows       = 2
miss rows            = 1
aborted rows         = 1
pruned rows          = 1
```

Offload rows:

```text
active_queue_indices = [11, 11]
source_ids           = [101, 101]
cell_ids             = [51, 52]
work_counts          = [9, 8]
```

These are deferred large-cell rows produced by the generic status machine.

## Result

Artifact:

```text
schema  = rtdl.paper_reproduction.xhd.goal5410.statused_large_cell_deferral_stream_probe.v1
status  = synthetic_app_neutral_status_stream_gate_passed__bounded_xhd_gate_pending
matched = true
```

Generic semantic:

```text
name          = statused_large_cell_deferral_stream
app_semantics = none
contract      = generic_active_query_status_machine_reference_v1
```

Decision:

```text
synthetic_app_neutral_gate_passed        = true
bounded_xhd_author_sample_row_gate_passed = false
full_goal5387_row_identity_gate_passed    = false
explicit_lb_support_authorized            = false
recommended_next_goal = Goal5411_bounded_xhd_statused_deferral_sample_row_gate
```

## Validation

Local focused regression:

```text
$env:PYTHONPATH='src'; py -m unittest `
  tests.goal5410_statused_large_cell_deferral_stream_probe_test `
  tests.goal5409_status_machine_semantics_decision_test `
  tests.goal5408_cell_namespace_reconciliation_test `
  tests.goal5407_full_cover_delta_membership_probe_test

Ran 23 tests OK
```

## Claim Boundary

This goal proves:

```text
The generic RTDL active-query status-machine reference can express a synthetic
statused large-cell deferral stream with offload/completed/miss/abort/prune
states and app-neutral trace summary.
```

This goal does **not** prove:

```text
bounded X-HD author sample-row recovery;
full Goal5387 row-count/hash/sample/status parity;
explicit -lb support;
Figure 7 or Figure 11 reproduction;
performance parity;
exact paper dataset reproduction;
full X-HD paper reproduction.
```

## Recommended Next Step

```text
Goal5411_bounded_xhd_statused_deferral_sample_row_gate
```

Goal5411 should use the generic statused deferral contract to attempt a bounded
X-HD author sample-row recovery. It must not hard-code the sampled source/cell
ids as a solution, and it must fail-close if row identity cannot be recovered by
generic semantics.
