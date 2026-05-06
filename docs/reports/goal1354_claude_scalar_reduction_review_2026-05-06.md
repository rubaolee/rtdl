Now I have a complete picture. Here is the review.

---

## Verdict: ACCEPT

The scalar-reduction wiring is bounded, coherent, and non-overclaiming. No blocking issues found.

---

## Findings: No blocking findings

All claim-boundary checks pass:

- `run_generic_scalar_reduction` embeds `"not native backend acceleration"` in its `claim_boundary` output key, and every call site propagates it via `_scalar_reduction_metadata`.
- `public_wording_authorized: False` is enforced by the inventory validator (`_validate_v1_5_generic_migration_inventory_rows`, line 263); raising if `True` is a hard invariant, not documentation.
- `V1_5_GENERIC_SCALAR_REDUCTION_PRIMITIVES` in `reduction_runtime.py` and `V1_5_STABLE_SUMMARY_PRIMITIVES` in `v1_5_migration_inventory.py` are identical six-element tuples; cross-module drift is impossible at this state.
- Frozen backends (`vulkan`, `hiprt`, `apple_rt`) are rejected by name at every entry point; no test exercises the cpu→inventory slot (cpu is legitimately absent from `ACTIVE_V1_5_BACKENDS`).
- v1.0 release claims are untouched: nothing in any modified file mentions v1.0 speedup wording.

---

## Remaining actionable gaps (prioritized)

**1. `count_threshold_reached` fast path silently drops `scalar_reduction` key**
`GenericPreparedFixedRadiusCountThreshold2D.count_threshold_reached` (`generic_primitives.py:590-622`) conditionally sets `scalar_summary = None` and then uses `if scalar_summary is not None: result["scalar_reduction"] = …`. When the native backend provides its own count, `scalar_reduction` is absent from the result dict. No test asserts that the key is absent (or present) in this path. A consumer using `result.get("scalar_reduction")` without checking would get `None` silently. Fix: either always populate the key (even as a sentinel `None`) and document it, or add a test that explicitly asserts `"scalar_reduction" not in result` in the fast path so the contract is locked.

**2. `result_layout: "grouped_threshold_bool"` is a loose unregistered string**
`grouped_count_threshold_bool` (`generic_primitives.py:448`) emits a `result_layout` that is not in `_scalar_result_layout()` and not in any registry. The goal1306 test asserts on the literal, which provides a canary, but a typo in production code would only be caught by that single test. Fix: add `"grouped_threshold_bool"` to `_scalar_result_layout` or a dedicated result-layout constant and validate it at the call site.

**3. No test covers the outer `row_count` vs scalar `row_count` distinction in `FIXED_RADIUS_COUNT_THRESHOLD_2D`**
`run_generic_fixed_radius_count_threshold_2d` reports outer `row_count = len(rows)` (all query points) and strips scalar `row_count` (only threshold-reached subset). A consumer could misread the outer count. Fix: add one assertion in goal1298 confirming `result["row_count"] > result["threshold_reached_count"]` in a case where some—not all—thresholds are reached.

**4. `REDUCE_FLOAT(MIN/MAX)` empty-input raise is tested in isolation (goal1350) but not through any primitive API**
If any future primitive uses `REDUCE_FLOAT(MIN)` as its summary primitive and emits zero rows, the runtime raises rather than returning an identity. This is correct per the spec, but there is no integration-level test confirming the error surfaces cleanly from a traversal primitive. Low risk now (no current primitive uses MIN/MAX at the summary layer), but worth a negative-path test before adding any float-min/max wired primitive.

**5. `_scalar_reduction_metadata` strips `result` but no test asserts `result` is absent from `scalar_reduction` sub-dict**
Purely a contract-asserting gap. If someone inadvertently stops stripping `result`, tests won't catch it. Fix: add one assertion `self.assertNotIn("result", result["scalar_reduction"])` to an existing test.

---

## Suggested next goal

**Goal1354 (or next available):** Lock the `count_threshold_reached` fast-path contract — add a test asserting `"scalar_reduction" not in result` when the native backend provides `count_threshold_reached`, and decide (in the same goal) whether the key should be a consistent `None` sentinel instead of absent. One narrow decision, one narrow test.
