# Goal5384 X-HD Multi-Round Active-Query Status Result

Date: 2026-07-10

Status:

```text
implemented_review_pending
```

Exit label:

```text
multiround_status_reference_ready__native_or_author_trace_required_for_lb_parity
```

## Purpose

Goal5383 showed that another single-pass native prune-mode variant does not
move the X-HD `-lb` denominator:

```text
author offload rows = 27133990
RTDL active-initial-best bridge rows = 2188225
row_count_parity = false
```

Goal5384 stops adding local prune-mode guesses and introduces a generic
multi-round active-query status reference contract.  The goal is to make the
next valid `-lb` work concrete:

```text
active query state
-> per-round candidate/status rows
-> raw offload rows
-> continuation feedback keyed by active_queue_index
-> next active queue
-> cumulative telemetry
```

This is a generic RTDL reference contract, not X-HD `-lb` support.

## What Was Implemented

New generic RTDL contract:

```text
ACTIVE_QUERY_MULTIROUND_STATUS_CONTRACT =
  generic_active_query_multiround_status_reference_v1
```

New public helper:

```text
active_query_status_multiround_reference_numpy_columns
```

Files changed:

```text
src/rtdsl/active_query_status.py
src/rtdsl/__init__.py
tests/goal5384_multiround_active_query_status_test.py
tests/goal5384_multiround_status_requirements_test.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5384_multiround_status_requirements.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5384_multiround_status_requirements.json
```

## Contract Semantics

The helper runs a sequence of app-neutral rounds.  Each round calls the existing
single-round active-query status reference, then optionally applies continuation
feedback keyed by `active_queue_index`, and carries selected status kinds into
the next round.

Current default carry-forward:

```text
continue_status_kinds = ("offload",)
```

The reference emits:

```text
offload_rows
completed_rows
miss_rows
aborted_rows
final_active_state
per-round telemetry
cumulative raw_offload_rows_before_sort_reduce
```

The metadata deliberately says:

```text
app_semantics = none
native_engine_row_contract = not_called_cpu_reference_only
explicit_app_option_support_claimed = false
rt_core_speedup_claim_authorized = false
whole_app_speedup_claim_authorized = false
```

## Synthetic Behavior Gate

The new test fixture proves actual multi-round behavior:

1. Round 0 has three active queries.
2. Query 0 completes.
3. Query 1 emits one heavy/offload row.
4. Query 2 has a finite existing best and completes.
5. Feedback updates query 1's current best by `active_queue_index`.
6. Round 1 carries only query 1 and completes it.

Expected synthetic telemetry:

```text
round_count = 2
initial_active_query_count = 3
final_active_query_count = 0
raw_offload_rows_before_sort_reduce = 1
completed_row_count = 3
miss_queue_count = 0
feedback_row_count = 1
feedback_updates_applied = 1
```

This tests the missing shape that Goal5381/5383 did not have: state flows across
rounds instead of classifying one native stream once.

## Artifact

Generated artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5384_multiround_status_requirements.json
```

It carries forward the two decisive numbers:

```text
Goal5374 author offload rows = 27133990
Goal5383 RTDL probe rows     = 2188225
row_ratio                    = 0.08064516129032258
row_count_parity             = false
```

It also records the next required fields:

```text
active_query_count
active_in_queue_indices
current_best_state_source
status_count_init
status_count_offloading
status_count_aborted
miss_queue_count
cmax2_mbr_abort_count
raw_offload_rows_before_sort_reduce
offload_row_count
author_width_bytes
row_count_parity_against_goal5374
```

## Validation

Artifact generation:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5384_multiround_status_requirements.py
```

Focused tests:

```text
py -m unittest \
  tests.goal5384_multiround_active_query_status_test \
  tests.goal5384_multiround_status_requirements_test \
  tests.goal5383_active_initial_best_status_probe_test \
  tests.goal5382_status_machine_stream_design_test \
  tests.goal5381_active_query_frontier_bridge_probe_test \
  tests.goal5379_active_query_status_machine_reference_test \
  tests.goal5380_active_query_frontier_bridge_test
```

Observed:

```text
Ran 27 tests in 3.183s
OK
```

The local Windows `py` launcher also printed:

```text
Could not find platform independent libraries <prefix>
```

This is the known noisy local Python environment output; tests still passed.

## Claim Boundary

Allowed:

```text
RTDL now has a generic CPU/reference multi-round active-query status contract.
The contract can model offload feedback and next-active-queue flow.
The artifact identifies the fields required for the next native/oracle gate.
```

Not allowed:

```text
explicit -lb support;
row-count parity;
Figure 7 reproduction;
Figure 11 reproduction;
author RT-core algorithm parity;
RTDL/author performance ratio;
exact paper dataset reproduction;
full X-HD paper reproduction.
```

## Interpretation

Goal5384 is forward progress because it changes the work from local
single-pass probes to the correct multi-round execution model.  It does not
solve the author denominator yet.

The next technical gate must choose one:

```text
1. Native generic multi-round status stream against the Goal5374 author oracle.
2. Stronger author trace with per-round cmin2/current-best and raw offload rows.
3. Explicit fail-closed closeout for author -lb if parity is not feasible under
   the generic contract.
```

Bridge vectorization remains the wrong next target until the native row stream
denominator matches or is formally rejected.
