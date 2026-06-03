# Goal3141: Independent Claude Review — Numba Cache and Schema Closure

Date: 2026-06-03
Reviewer: Claude Sonnet 4.6 (independent, read-only)
Scope: Goals 3139 and 3140
Verdict: **accept**

---

## Findings by Severity

### No critical issues

### Minor observation (informational, no action required)

**Segmented-count and segmented-sum kernel factories are still uncached.**

`run_numba_segmented_count_i64` (line 195) and `run_numba_segmented_sum_f64` (line 237)
call their kernel factories directly rather than via `_cached_numba_kernel`. Both operations
are in `V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_SUPPORTED_OPERATIONS`, so if either
became a steady-state hot path, they would rebuild their Numba dispatcher on each call.
Goal3139 targeted grouped-arg ops only, so this is pre-existing and outside the stated scope.
No action needed now; log as a candidate for a future performance pass if these operations
are exercised on a CUDA pod.

### Review confirmation notes (no issues)

- `_run_numba_segmented_extreme_f64` (line 727) also calls its factory directly, but
  `segmented_min_f64` and `segmented_max_f64` are deferred from the v2.8 front door, so
  this does not affect the production surface.
- Cache key uniqueness: all factory functions have descriptive module-level names (e.g.,
  `_numba_grouped_argmin_score_f64_kernel`). The key `(id(cuda), factory.__name__)` produces
  no collisions across the current factory set.
- The test in `goal3139_numba_kernel_cache_contract_test.py` saves and restores the global
  cache dict in a `finally` block, leaving no cross-test state.
- All eleven claim-boundary boolean fields are enforced to `False` at construction time by
  `V28SegmentedTypedStreamAdapterResult.__post_init__` and independently re-checked by
  `validate_segmented_typed_stream_adapter`. Identical enforcement exists in
  `V28TypedResultStreamContract.__post_init__` and `V28GroupedContinuationPlan.__post_init__`.

---

## Review Question Responses

### Q1: Does Goal3139 correctly identify repeated Numba dispatcher construction as the main grouped-arg performance issue, based on the Goal3136/3139 timing delta?

**Yes.** The evidence is internally consistent:

- Goal3136 reported a nearly constant ~0.19–0.20 s floor for the default-compact path
  regardless of row count, which is the signature of a fixed per-call overhead (compilation)
  rather than a compute-scaling cost.
- Goal3139's JSON artifact (`numba_kernel_cache_timing_2026-06-03.json`) shows a warm time
  of ~0.30 s for the very first call (Numba JIT compilation, confirmed by the single spike
  before the cache entry exists) and a steady-state median of ~0.0018 s for the same path.
- The `_NUMBA_KERNEL_CACHE` module dict is populated on first call and reused on all
  subsequent calls; the steady-state numbers are consistent with actual GPU kernel launches
  rather than any compilation overhead.
- The interpretation stated in the report — "dispatcher construction, not the v2.8 front-door
  contract itself" — is confirmed by the `layer: direct` and `layer: partner_adapter` rows
  being within ~100–200 µs of each other at steady state, showing the front-door wrapper
  overhead is small once the kernels are cached.

### Q2: Is the kernel cache implementation app-agnostic and safe for the current preview partner surface?

**Yes.** `_cached_numba_kernel` is a ten-line utility that:

- Holds no operation semantics, partner choices, validation policy, or output schema.
- Is keyed on `(id(cuda), factory_name)`. The `cuda` module is a process-level singleton;
  `id()` reuse after GC is not a risk for a module imported once at startup. If multiple CUDA
  contexts were ever in scope, different `id` values would produce separate entries — correct
  behavior.
- Is applied only to grouped-arg ops and the shared `_numba_group_id_validation_kernel` and
  `_numba_gather_group_arg_outputs_kernel` helpers inside `_run_numba_grouped_arg_reduce_f64`
  and `_validate_group_run_shape`. No other paths are changed.
- Does not alter the metadata written to `_numba_run_result` or any claim-boundary flag.

The single contract test (`test_cache_reuses_kernel_for_same_cuda_module_and_factory`) is
sufficient to verify reuse behavior without requiring CUDA. It is isolated and correct.

### Q3: Does Goal3140 close the Goal3138 low debts for canonical ranked-summary pod evidence, `compact_mask_i64` rationale, and min/max deferral rationale?

**Yes, all three debts are closed.**

**Debt 1 — canonical ranked-summary schema pod evidence:**
`v2_8_canonical_schema_pod_smoke_2026-06-03.json` records three pod cases all marked
`"status": "passed"` at commit `a44de908`:
- `grouped_argmin_f64_numba`: keys `group_ids, item_ids, scores, missing_group_ids` — correct.
- `grouped_argmax_f64_numba`: same key set — correct.
- `grouped_topk_f64_torch`: keys `group_ids, item_ids, scores, ranks, row_offsets, missing_group_ids` — correct.

The `_canonical_ranked_summary_columns` helper enforces these exact key sets at execution time,
so the schema is validated by the smoke run, not just declared.

**Debt 2 — `compact_mask_i64` deferral rationale:**
Added to `V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_DEFERRED_OPERATIONS` with the
rationale "reference-only in v2.8 because it is an order-preserving mask compaction
continuation, not a grouped partner-consumer operation; adding a partner front door requires
separate mask-compaction smoke evidence." This is accurate: `compact_mask_i64` is structurally
different from the grouped-continuation operations (no group_count, different signature) and
warrants distinct smoke evidence before promotion. The dry-run test
`test_partner_consumer_dry_run_marks_unsupported_operation` verifies the reason string is
surfaced via `unsupported_operation_reason`.

**Debt 3 — segmented_min/max deferral rationale:**
Both added to the deferred dict with "lower-level partner operation exists, but v2.8 front-door
support is deferred until explicit partner-consumer smoke evidence exists." The lower-level
operations (`run_numba_segmented_min_f64`, `run_numba_segmented_max_f64`) exist and compile
correctly but lack a partner-consumer smoke run. The rationale is honest and complete.

### Q4: Is the documented one-based `grouped_topk_f64` rank convention consistent with the reference and Torch implementation?

**Yes.** Consistency confirmed from three independent sources:

- `V2_8_TYPED_RESULT_STREAM_CONTINUATION_SEMANTICS["grouped_topk_f64"]` states "ranks are
  one-based within each group."
- The pod JSON shows `"ranks": [1, 1]` for k=1 with two groups, each having a single winner.
  Under one-based convention, the best item in a group gets rank 1 — correct.
- The script (`goal3140_v2_8_canonical_schema_pod_smoke.py`, line 136) hardcodes the expected
  ranks as `[1, 1]` and the `_check` function raises on any mismatch, so the Torch
  implementation produced rank 1 for each group's top-1 item at execution time.

The reference consumer test `test_reference_consumer_requires_k_for_topk` exercises k=1 and
checks `item_ids == [10]` (the lowest-score item for group 0), confirming "lowest score =
rank 1" semantics are consistent end to end.

### Q5: Are all release/speedup/zero-copy/hidden-dispatch/auto-partner/app-specific native-engine/user-shader-injection claim boundaries still intact?

**Yes.** Boundary integrity verified at four levels:

1. **`numba_partner_continuation.py`**: `_numba_run_result` emits
   `rt_core_speedup_claim_authorized: False`, `replaces_rt_traversal: False`,
   `promoted_performance_path: False` on every call path. The `_base_numba_descriptor`
   similarly sets `raw_kernel_required: False`, `replaces_rt_traversal: False`,
   `promoted_performance_path: False`. The JSON artifact confirms
   `"rt_core_speedup_claim_authorized": false` in the warm metadata.

2. **`v2_8_typed_result_stream.py`**: `V28TypedResultStreamContract.__post_init__` and
   `V28GroupedContinuationPlan.__post_init__` each `raise ValueError` if any claim field is
   `True`. `validate_typed_result_stream_contract` and `validate_grouped_continuation_plan`
   independently check all fields are `False`.

3. **`v2_8_segmented_typed_stream_adapter.py`**: `V28SegmentedTypedStreamAdapterResult.__post_init__`
   iterates all eleven boundary fields and raises if any is `True`. All three of
   `execute_segmented_typed_stream_reference_continuation`,
   `execute_segmented_typed_stream_partner_continuation`, and
   `plan_segmented_typed_stream_partner_continuation` explicitly set all flags to `False` in
   their returned dicts. `_partner_bridge_metadata` sets its own subset to `False`. The
   `validate_segmented_typed_stream_adapter` function checks each field is `is not False` and
   errors if so.

4. **Report claim boundaries**: Both Goal3139 and Goal3140 reports end with explicit "Claim
   Boundary" sections listing no release, public speedup wording, broad RT-core wording,
   true-zero-copy wording, hidden dispatch, automatic partner selection, app-specific
   native-engine behavior, or user-defined shader injection is authorized. The pod artifact
   JSON files carry `"claim_boundary": "diagnostic_timing_not_speedup_claim"` and
   `"claim_boundary": "schema_smoke_not_release_or_speedup_claim"` respectively.

---

## Summary

Goal3139's kernel cache is a narrow, app-agnostic fix correctly scoped to grouped-arg
dispatcher reconstruction. The pod timing delta validates the hypothesis. Goal3140 closes all
three Goal3138 low debts with real pod evidence and explicit machine-readable rationale. Rank
convention is consistent across the semantics string, pod output, and reference consumer.
Claim boundaries are enforced in code, not just documentation.

**Verdict: accept**

The one informational note (segmented-count/sum kernel factories not yet cached) is outside
this goal's scope and does not affect correctness or the current partner surface.
