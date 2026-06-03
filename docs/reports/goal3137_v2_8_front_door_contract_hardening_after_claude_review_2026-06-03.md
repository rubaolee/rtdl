# Goal3137: v2.8 Front-Door Contract Hardening After Claude Review

Date: 2026-06-03

Status: focused contract hardening implemented and tested

## Purpose

Goal3133 delivered a fresh Claude review of Goals3108-3131. The review accepted
the v2.8 partner-front-door chain with boundaries, then flagged several small
contract gaps that should be closed before any operation-surface or
partner-coverage claim is made.

Goal3137 addresses the mechanical contract gaps without expanding the supported
surface and without changing the native engine.

## Changes

1. `grouped_topk_f64` semantics are now explicit in
   `V2_8_TYPED_RESULT_STREAM_CONTINUATION_SEMANTICS`: it selects the k lowest
   scores per group, ordered by ascending score and then ascending item id.
   `grouped_argmin_f64` and `grouped_argmax_f64` also carry explicit tie-break
   semantics.

2. The placeholder partner value `explicit_user_choice_required` is now rejected
   for actual grouped continuation plans, matching the existing rejection of
   `""` and `auto`.

3. The v2.8 partner front door now canonicalizes ranked-summary outputs:
   `grouped_argmin_f64` and `grouped_argmax_f64` expose only
   `group_ids`, `item_ids`, `scores`, and `missing_group_ids`.
   `grouped_topk_f64` exposes only `group_ids`, `item_ids`, `scores`, `ranks`,
   `row_offsets`, and `missing_group_ids`.

4. Helper-only columns such as dense arrays and `counts` are filtered at the
   front door, matching the earlier bounded-collect schema filter.

## Deliberate Non-Changes

`segmented_min_f64` and `segmented_max_f64` remain declared lower-level partner
continuation operations, but they are not added to the v2.8 front-door supported
set in this goal. Adding them would require explicit partner-front-door smoke
evidence, not just a metadata edit.

`compact_mask_i64` also remains reference-only at this layer.

## Validation

Focused local validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3108_v2_8_typed_result_stream_contract_test tests.goal3111_v2_8_segmented_typed_stream_adapter_test
Ran 24 tests in 0.013s
OK
```

Touched Python compile check:

```text
py -3 -m py_compile src\rtdsl\v2_8_typed_result_stream.py src\rtdsl\v2_8_segmented_typed_stream_adapter.py src\rtdsl\__init__.py
OK
```

An intermediate local command attempted to run three guessed test modules that
do not exist in this checkout; those import errors were command-selection
noise, not code failures. The actual v2.8 test modules present in the checkout
are the two listed above.

## Claim Boundary

Goal3137 is contract hardening only. It authorizes no release, public speedup
wording, broad RT-core wording, true-zero-copy wording, hidden dispatch,
automatic partner selection, app-specific native-engine behavior, or
user-defined shader injection.
