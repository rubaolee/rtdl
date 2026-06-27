# Handoff: Gemini Review For Goal3804 And Goal3806 Typed Alias Inventory

Please perform a read-only independent review of Goal3804 and Goal3806 and write the review to:

`docs/reviews/goal3807_gemini_review_goal3804_3806_typed_alias_inventory_2026-06-07.md`

## Current Commits To Review

- `64b61ffd Goal3804 add current typed-stream aliases`
- `22487997 Goal3806 inventory active versioned helpers`

## Scope

Goal3804 added current aliases for Barnes-Hut grouped-vector typed-stream helpers and RTNN ranked-summary typed-stream helpers while preserving the v2.8 legacy helper/mode names.

Goal3806 inventoried the remaining active example versioned helper/function names and classified them into compatibility shims, preserved internal/protocol helpers, and remaining low-risk candidates.

## Files To Inspect

- `examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py`
- `examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py`
- `docs/reports/goal3804_typed_stream_benchmark_alias_cleanup_2026-06-07.md`
- `tests/goal3804_typed_stream_benchmark_alias_cleanup_test.py`
- `docs/reports/goal3806_active_example_versioned_helper_inventory_2026-06-07.md`
- `tests/goal3806_active_example_versioned_helper_inventory_test.py`

## Verification Already Run

Local Windows:

`PYTHONPATH=src;. py -3 -m unittest tests.goal3806_active_example_versioned_helper_inventory_test tests.goal3800_legacy_versioned_helper_alias_cleanup_test tests.goal3802_raydb_current_helper_alias_cleanup_test tests.goal3804_typed_stream_benchmark_alias_cleanup_test`

Result: 20 tests OK.

A5000 pod:

`PYTHONPATH=.pydeps_goal3788_numba:src:. python3 -m unittest tests.goal3806_active_example_versioned_helper_inventory_test tests.goal3800_legacy_versioned_helper_alias_cleanup_test tests.goal3802_raydb_current_helper_alias_cleanup_test tests.goal3804_typed_stream_benchmark_alias_cleanup_test`

Result: 20 tests OK at `22487997`.

## Review Questions

1. Do the Barnes-Hut and RTNN aliases make the current typed-stream helpers clearer without breaking v2.8 compatibility names?
2. Does Goal3806 honestly classify remaining versioned names instead of pretending the whole cleanup is done?
3. Do these changes avoid native engine app customization and avoid release, package-install, zero-copy, RT-core speedup, public speedup, or paper-reproduction claims?
4. Are the remaining candidate aliases correctly scoped as future low-risk cleanup rather than current blockers?
5. Are any fixes required before Goal3804/3806 can stand as small internal cleanup goals?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
