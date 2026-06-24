# Goal4318: Claude External Review — Goal4317 Grouped Reduction Adapter Route

Date: 2026-06-11
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **accept**

---

## Scope of Review

Read-only inspection of five files against the four requested checks. No
execution; test result taken as reported (11 tests passed, 2 expected optional
CUDA/partner skips).

---

## Check 1 — Public `rtdsl` reduction exports route through `rtdsl.adapters.reductions`

**Confirmed.**

`src/rtdsl/__init__.py` lines 1232–1264 import all 20 named symbols from
`.adapters.reductions`, not from `.partner_adapters`:

| Category | Names |
|---|---|
| Key/value reductions | `partner_group_any_by_key`, `partner_group_count_by_key`, `partner_group_count_unique_pairs_by_key`, `partner_group_max_by_key`, `partner_group_min_by_key`, `partner_group_sum_by_key`, `partner_group_vector_sum_2d_by_key` |
| Metric-table reductions | `partner_metric_table_reduce_batch`, `partner_metric_table_reduce_by_key`, `partner_metric_table_reduce_repeated_pattern` |
| Unique-pair keys | `partner_unique_pair_keys` |
| Ranked reductions | `grouped_argmax_f64_partner_columns`, `grouped_argmin_f64_partner_columns`, `grouped_topk_f64_partner_columns` |
| Vector sums | `grouped_vector_sum_2d_partner_columns` |
| Prepared vector-sum sessions | `prepare_grouped_vector_sum_2d_partner_columns_session`, `run_grouped_vector_sum_2d_partner_columns_session` |
| Measured vector-sum selection | `measured_grouped_vector_sum_2d_partner_selection` |
| Argmin/global-argmax witness | `group_argmin_then_global_argmax_partner_columns`, `global_argmax_u32_f64_partner_columns` |

`src/rtdsl/adapters/reductions.py` declares all 20 in `__all__` and re-exports
each from `..partner_adapters`. The routing layer is a thin delegation module
with no implementation body. `rt.<name> is reductions.<name>` holds by
identity because both `__init__.py` and the test source the same object from
the same module.

The test `test_public_reduction_exports_route_through_generic_adapter_module`
checks `assertIn(f"from .adapters.reductions import {name}", init_source)` and
`assertNotIn(f"from .partner_adapters import {name}", init_source)` for each
symbol — mechanically enforcing the routing invariant in code.

---

## Check 2 — `v2_8_segmented_typed_stream_adapter.py` imports the four key operations via `rtdsl.adapters.reductions`

**Confirmed for the four in-scope operations.**

In `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`:

| Operation | Location | Route |
|---|---|---|
| `grouped_vector_sum_2d_partner_columns` | line 870 (lazy import inside `execute_grouped_vector_sum_typed_stream_partner_columns`) | `.adapters.reductions` ✓ |
| `grouped_argmin_f64_partner_columns` | line 1399 (lazy import inside `_execute_partner_front_door`) | `.adapters.reductions` ✓ |
| `grouped_argmax_f64_partner_columns` | line 1404 | `.adapters.reductions` ✓ |
| `grouped_topk_f64_partner_columns` | line 1409 | `.adapters.reductions` ✓ |

The test `test_segmented_stream_adapter_uses_reduction_adapter_route` verifies
both the positive imports and the absence of direct `.partner_adapters` imports
for all four.

**Observation (no finding):** `_execute_partner_front_door` still has inline
`from .partner_adapters import ...` for `partner_group_count_by_key`,
`partner_group_sum_by_key`, `partner_group_max_by_key`,
`partner_group_min_by_key`, `partner_group_vector_sum_2d_by_key`,
`bounded_collect_finalize_i64_partner_columns`, `partner_mask_indices`, and
`partner_take_columns_by_indices`. These are not in scope for Goal4317 (the
goal explicitly targets only the four grouped-reduction functions) and the
report does not claim otherwise. This is consistent with the incremental
monolith-split plan.

---

## Check 3 — Report honestly describes this as a route canonicalization, not a full monolith split

**Confirmed.**

`docs/reports/goal4317_grouped_reduction_adapter_route_2026-06-11.md`, line 29:

> "This does not move implementation bodies out of `partner_adapters.py`; that
> larger split remains future work."

`src/rtdsl/adapters/reductions.py` module docstring (lines 3–10) reinforces this:

> "The implementation still delegates to the legacy `partner_adapters` internals
> while the monolith is split incrementally, but new package exports and
> internal generic stream adapters should import from this module rather than
> directly from `partner_adapters`."

The implementation bodies remain entirely in `partner_adapters.py`; the adapter
module is a pure import-routing shim. The report is accurate.

---

## Check 4 — No unauthorized release, speedup, RT-core, true-zero-copy, package-install, paper-reproduction, automatic-partner-selection, or app-specific native-engine claims

**Confirmed absent.**

The report boundary section explicitly excludes all of: release action, public
speedup, broad RT-core, package-install, automatic partner selection,
true-zero-copy, paper reproduction, and app-specific native-engine logic.

The `V28SegmentedTypedStreamAdapterResult` dataclass in
`v2_8_segmented_typed_stream_adapter.py` enforces all claim-boundary fields at
construction time via `__post_init__` (lines 84–97): any of
`release_authorized`, `public_speedup_claim_authorized`,
`rt_core_speedup_claim_authorized`, `true_zero_copy_claim_authorized`,
`automatic_partner_selection_allowed`, `app_specific_engine_logic_allowed`, etc.
being `True` raises `ValueError`. The same check is present in
`validate_segmented_typed_stream_adapter` (lines 249–262).

`V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_CLAIM_BOUNDARY` (lines 43–50) explicitly
disavows device residency, true zero-copy, release readiness, public speedup,
broad RT-core acceleration, hidden dispatch, hidden partner selection, and
app-specific native-engine behavior.

---

## Summary

Goal4317 is a narrow, honest adapter-route canonicalization. The public
`rtdsl` surface now routes all 20 grouped/summary reduction symbols through
`rtdsl.adapters.reductions` rather than directly from `partner_adapters`. Four
lazy imports in `v2_8_segmented_typed_stream_adapter._execute_partner_front_door`
and one in `execute_grouped_vector_sum_typed_stream_partner_columns` also
switched to the canonical route. The report accurately describes the scope and
does not overstate what was done. No new behavioral claims are introduced. The
test suite mechanically enforces the routing invariant.

**Verdict: accept**
