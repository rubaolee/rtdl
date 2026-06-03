# Goal3165 - RTNN Ranked-Summary Typed-Stream Front Door

Date: 2026-06-03

Status: local implementation validated; pod validation pending.

## Purpose

Goal3165 turns the RTNN v2.8 runtime-gap item into a generic front-door slice:
caller-supplied grouped score columns can now be described and consumed as a
`ranked_summary_stream` with explicit partner continuation. This is the reusable
shape behind RTNN-style fixed-radius ranked-neighbor summaries, but the runtime
surface is not RTNN-specific.

## What Changed

- Added `rt.execute_ranked_summary_typed_stream_partner_columns(...)`.
- The helper accepts explicit `group_ids`, `item_ids`, `scores`,
  `group_count`, `operation`, `partner`, and `stream_id`.
- Supported operations are:
  - `grouped_argmin_f64`
  - `grouped_argmax_f64`
  - `grouped_topk_f64`
- The helper rejects `partner="auto"` and records
  `automatic_partner_selection_allowed: False`.
- The helper publishes a `ranked_summary_stream` typed result-stream contract,
  plans the grouped continuation through the existing v2.8 continuation planner,
  and uses the existing generic partner adapters for execution.
- Added RTNN benchmark app helpers:
  - `describe_rtnn_v2_8_ranked_summary_typed_stream(...)`
  - `run_rtnn_v2_8_ranked_summary_typed_stream_preview(...)`
- Added the CLI descriptor mode:
  `--mode rtnn_v2_8_ranked_summary_plan`.

## App-Agnostic Boundary

The core helper is generic. It uses stream/column names such as `group_ids`,
`item_ids`, and `scores`, and operations such as `grouped_topk_f64`. RTNN
vocabulary appears only in the benchmark app wrapper and this report.

This goal does not add an RTNN-specific native symbol, native continuation, or
engine branch. It also does not promote a native ranked-summary producer. The
source materialization remains:

`caller_supplied_partner_columns_no_hidden_host_rows`

## Partner Boundary

The user must choose the partner explicitly. The current partner adapter state
is:

- `grouped_argmin_f64`: `numba`, `torch`, `triton`
- `grouped_argmax_f64`: `numba`, `torch`, `triton`
- `grouped_topk_f64`: `torch`, `triton`

Numba top-k is not promoted by this goal. That is a future partner-adapter
extension if the RTNN path needs a Numba-first top-k reference.

## Claims Not Authorized

The new front door sets or preserves these boundaries:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`
- `automatic_partner_selection_allowed: False`
- `app_specific_engine_logic_allowed: False`

It does not claim full RTNN paper reproduction. It is a reusable continuation
surface for ranked summaries produced by fixed-radius or other caller-supplied
candidate streams.

## Local Validation

Compile check:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m py_compile `
  src\rtdsl\v2_8_segmented_typed_stream_adapter.py `
  src\rtdsl\__init__.py `
  examples\v2_0\research_benchmarks\rtnn\rtdl_rtnn_benchmark_app.py `
  tests\goal3165_rtnn_ranked_summary_typed_stream_front_door_test.py
```

Result: pass.

Focused regression:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3165_rtnn_ranked_summary_typed_stream_front_door_test `
  tests.goal3111_v2_8_segmented_typed_stream_adapter_test `
  tests.goal2585_rtnn_benchmark_front_door_test
```

Result: 27 tests pass, 1 skipped.

Wider v2.8 front-door slice:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3165_rtnn_ranked_summary_typed_stream_front_door_test `
  tests.goal3162_raydb_grouped_reduction_typed_stream_front_door_test `
  tests.goal3164_v2_8_front_door_chain_review_packet_test `
  tests.goal3108_v2_8_typed_result_stream_contract_test `
  tests.goal3111_v2_8_segmented_typed_stream_adapter_test
```

Result: 37 tests pass, 2 skipped.

CLI descriptor check:

```powershell
$env:PYTHONPATH='src;.'; py -3 `
  examples\v2_0\research_benchmarks\rtnn\rtdl_rtnn_benchmark_app.py `
  --mode rtnn_v2_8_ranked_summary_plan `
  --operation grouped_topk_f64 `
  --partner torch `
  --k 2
```

Result: JSON payload reports `ranked_summary_stream`, explicit partner
`torch`, operation `grouped_topk_f64`, and all release/speedup/zero-copy flags
as false.

Pod validation should fetch/reset to `origin/main`, set `PYTHONPATH=src:.`, and
run the same slice. Executable top-k checks require `torch`; otherwise the
dry-run contract checks still validate the front-door metadata.
