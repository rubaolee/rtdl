# Goal5412 X-HD Fail-Close Or Native Trace Semantics Decision

Date: 2026-07-10

Status:

```text
current_statused_bridge_fail_closed__generic_native_payload_transition_trace_design_authorized
```

## Purpose

Goal5411 tested the last authorized bridge from the current RTDL execution
model:

```text
current native frontier rows -> generic active-query status bridge
```

It failed the bounded X-HD author sample-row gate. Goal5412 decides what this
means before any new full Goal5387 row/hash parity attempt.

## Inputs

Goal5387 author oracle:

```text
active queries                       = 437,645
raw offload rows before sort/reduce  = 27,133,990 = 62 * active_count
raw offload row hash                 = 4333109858711462591
sample source ids                    = [11168, 210712, 437119]
sample cell ids                      = [2924, 17, 17]
feedback_update_count                = 294
```

Goal5406 RTDL full-cover surface:

```text
RTDL full-cover rows = 24,508,120 = 56 * active_count
author raw rows      = 27,133,990
row count parity     = false
row hash parity      = false
```

Goal5407:

```text
classification = author_sample_rows_not_subset_of_rtdl_full_cover__row_identity_gap
```

Goal5408:

```text
classification = author_sample_cell_ids_exist_globally_but_not_for_author_sources
compact/original namespace remap explains author samples = false
```

Goal5410:

```text
synthetic app-neutral statused deferral stream passed
offload/completed/miss/aborted/pruned statuses all exercised
```

Goal5411:

```text
bounded X-HD author sample-row recovery failed
observed cells for sampled sources = [1554, 1554, 1554]
author sample cells                = [2924, 17, 17]
```

## Decision

The current bridge is fail-closed:

```text
explicit_lb_support_authorized = false
explicit_lb_current_model_fail_closed = true
recommended_current_branch = fail_close_current_explicit_lb
full_goal5387_row_identity_gate_authorized = false
direct_native_fix_authorized = false
```

Do not proceed to a full Goal5387 row/hash/status/feedback gate under the
current RTDL frontier-to-status bridge. It has already failed the bounded sample
row identity test.

However, the project goal still requires moving toward same-functionality X-HD
where possible. Therefore Goal5412 authorizes **design only** for a new generic
native trace semantic:

```text
native_payload_transition_trace_stream
```

This is not an implementation authorization. It is a contract/design gate for a
native trace stream emitted closer to traversal payload-state transitions.

This continuation is not an equal-weight default branch. It is a narrow
exception to the recommended fail-close decision, and it is justified only if
the next goal can state an app-neutral contract and a non-X-HD synthetic
behavior gate before any X-HD bounded sample-row comparison.

## Why The Current Model Fails

The evidence rules out the cheap explanations:

1. It is not just missing six terminal rows per active query. Goal5407 shows
   sampled author source/cell rows are absent from the RTDL full-cover surface.
2. It is not a simple compact/original cell namespace issue. Goal5408 shows the
   sampled author cell ids exist globally as compact ids but not for the
   sampled source rows.
3. It is not solved by the current generic status bridge. Goal5411 emits one
   statused deferral row per sampled source, but all three cells are `1554`,
   not the author cells `2924`, `17`, and `17`.

Therefore full parity under the current bridge would knowingly run a false
path.

## Authorized Generic Design

Name:

```text
native_payload_transition_trace_stream
```

Description:

```text
A generic native trace stream emitted at traversal payload transition points
before frontier lowering, row collapse, sort/unique, or continuation feedback.
```

Required row schema:

```text
active_queue_index
query_row_id
source_id
primitive_or_cell_id
cell_namespace_code
status_code
transition_phase_code
current_best_before_sq
current_best_after_sq
lower_bound_sq
upper_bound_sq
work_count
payload_event_ordinal
```

Required telemetry:

```text
active_query_count
raw_transition_row_count
raw_transition_row_hash_or_deterministic_samples
status_count_offloading
status_count_completed
status_count_miss
status_count_aborted
feedback_update_count_or_not_applicable
row_capacity
overflowed
```

Required semantic points:

```text
rows are emitted at native traversal or payload state-transition time;
rows are emitted before app-level continuation, grouped reduction, or row collapse;
cell namespace is explicit and app-neutral;
row ordering is deterministic or has deterministic hash/sample policy;
overflow fails closed with no partial success claim.
```

Evidence ladder:

```text
1. synthetic non-X-HD fixture;
2. bounded X-HD sample-row gate;
3. full Goal5387 row-count/hash/sample/status/feedback gate.
```

## Not Authorized

Goal5412 does not authorize:

```text
explicit -lb support;
new native backend implementation;
full Goal5387 row identity parity;
Figure 7 reproduction;
Figure 11 reproduction;
author-vs-RTDL performance ratio;
exact paper dataset reproduction;
full X-HD paper reproduction.
```

Forbidden shortcuts:

```text
hard-code 6 rows per active query;
hard-code 62 rows per active query;
hard-code Goal5387 sample source/cell pairs;
hard-code author raw offload hash;
add xhd, paper, figure, or lb option names to RTDL core/native symbols;
declare explicit -lb support from a design-only contract;
run full Goal5387 row identity parity before a bounded sample-row gate passes.
```

## Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5412_fail_close_or_native_trace_semantics_decision.json
tests/goal5412_fail_close_or_native_trace_semantics_decision_test.py
```

## Recommended Next Goal

```text
Goal5413_generic_native_payload_transition_trace_contract
```

Goal5413 should be a contract/schema goal, not a backend implementation goal.
It should decide whether the proposed trace stream can be represented in RTDL
as a generic native contract, and it should include a non-X-HD synthetic test
plan before any X-HD bounded sample-row gate.
