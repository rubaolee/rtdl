# Goal4164: RT-DBSCAN All-Predicate-Only Candidate Mode

Status: accepted locally; pod validation pending.

## Purpose

Goal4158 proved that the predicate direct-status route has a strong fast path
when every predicate flag is true. Goal4159 and Goal4160 also showed that the
same route must not be promoted for mixed predicate rows yet: the current
generic border-assignment policy can disagree with the grouped-stream reference
on component-size signatures for `road_sparse_many_noise`.

Goal4164 therefore exposes a narrower all-predicate-only candidate mode instead
of broadening the route. The new mode is:

`optix_rt_core_flags_cupy_predicate_direct_status_all_true_column_signature_3d`

It uses the same generic OptiX count-threshold plus CuPy predicate direct-status
continuation, but it requires runtime metadata proving that
`all_predicate_fast_path` fired.

In short: it is an all-predicate-only candidate mode that fails closed on mixed predicate rows.

## What Changed

- Added `RT_DBSCAN_PREDICATE_DIRECT_STATUS_ALL_TRUE_APP_MODE`.
- Added the mode to the RT-DBSCAN benchmark app CLI and signature-mode row
  materialization guard.
- Added an advisor option that explicitly marks:
  - `all_predicate_fast_path_required`
  - `mixed_predicate_fail_closed`
  - `mixed_predicate_fallback_route`
  - `border_assignment_policy = not_needed_all_predicate_true`
- Hardened the runtime branch so this mode raises `ValueError` when the
  predicate continuation does not report `all_predicate_fast_path`.
- Added metadata fields on successful rows:
  - `all_predicate_only_mode`
  - `all_predicate_fast_path_required`
  - `all_predicate_fast_path_observed`
  - `mixed_predicate_fail_closed`
  - `mixed_predicate_fallback_route`
  - `hidden_dispatch_allowed = False`
  - `route_promotion_authorized = False`

## Boundary

This is an explicit user-selected candidate route. It does not promote the predicate direct-status route, does not auto-select a route, does not auto-select a partner, and does not authorize release or public speedup wording.

No release or public speedup claim is authorized.

For mixed predicate rows, users should use:

`optix_rt_core_grouped_stream_numba_column_signature_3d`

until a `reference_grouped_stream_compatible` generic border-assignment policy is
implemented and remeasured.

## Validation

Local validation:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal4164_rt_dbscan_all_predicate_only_mode_test \
  tests.goal4163_rt_dbscan_route_advisor_after_predicate_gap_test \
  tests.goal4162_predicate_border_assignment_policy_metadata_test \
  tests.goal4161_rt_dbscan_canonical_signature_contract_test \
  tests.goal4159_mixed_predicate_direct_status_gap_test
```

Pod validation remains the next step:

1. Run an all-predicate row and confirm success with
   `all_predicate_fast_path_observed = True`.
2. Run a mixed-predicate row and confirm the new mode fails closed with the
   documented fallback message.
