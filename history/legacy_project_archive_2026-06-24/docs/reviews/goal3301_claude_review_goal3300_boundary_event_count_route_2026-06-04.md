# Goal3301 Claude Review — Goal3300 Boundary-Event Count Route
**Review date:** 2026-06-04
**Commit reviewed:** `0da3f427951460634a38f32daffc4873d42e9c73`
**Verdict:** `accept-with-boundary`

---

## Summary

Goal3300 wires the `boundary_event_point_id_count_device_columns` mode into
the app and runner. Contract disclosure is correct and enforced in multiple
layers. All claim-boundary flags remain False. Four issues — one medium
severity, three low/observability — must be resolved before this route is
cited as a standalone v2.8 benchmark data point.

---

## Findings by Severity

### Medium — Guard on non-membership disclosure only fires during `repeat`, not `warmup`

**File:** `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py:341-344`

The check:
```python
if count_mode == PIP_BOUNDARY_EVENT_COUNT_MODE and not summary.get(
    "boundary_event_contract_not_positive_membership"
):
    raise RuntimeError(...)
```
is inside the `for index in range(repeat):` loop. The preceding
`for index in range(warmup):` loop calls the same `one()` function without
the guard. If a future regression removes the `boundary_event_contract_not_positive_membership`
flag from the app payload, warmup calls would silently succeed and only the
first measured sample would raise.

The failure branch of the guard is also never exercised by tests. Both
`test_rtdl_pip_boundary_event_count_route_discloses_non_membership_contract`
(runner test, line 363) and `test_pip_boundary_event_route_uses_generic_device_columns_without_membership_claim`
(contract test, line 183) only exercise the positive case — they supply a payload
that already has the flag set correctly.

**Required fix:** Move the disclosure check above or outside the repeat/warmup
distinction so it fires on every call, and add a test that verifies `RuntimeError`
is raised when the flag is absent or False.

---

### Low / Observability — `prepared_query_sec` conflates both boundary-event phases

**File:** `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py:580-589`

The boundary event path calls `first_boundary_crossing_device_columns` and
then `grouped_count_by_point_id_device_columns` inside a single
`_phase_time(..., "prepared_query_sec", ...)` call. When this route is used
as a benchmark data point, artifacts will record one number for two distinct
GPU operations. If the grouped-count phase is significant, the timing cannot
be attributed correctly.

**Required before benchmark use:** Either split the timing into
`boundary_event_device_columns_sec` and `grouped_count_device_columns_sec`,
or explicitly document in the interpretation block that `prepared_query_sec`
is a fused two-phase time for this mode.

---

### Low — Event capacity is tight; overflow on degenerate geometry is undocumented

**File:** `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py:586`

```python
event_capacity=max(1, packed_points.count),
```

This sets capacity equal to the number of probe points, assuming each point
crosses at most one boundary segment. For inputs where points land exactly on
shared boundary edges (grid-aligned polygons, coincident vertices), a single
point may produce more than one crossing event and the overflow guard at
line 315 will raise `RuntimeError`. The overflow path is tested structurally
(`_FakeBoundaryEventColumns.overflow = False` keeps tests green) but the
scenario that triggers it is not documented anywhere in the app or runner.

**Required before benchmark use:** Add a note to `_run_prepared_boundary_event_grouped_count_device_columns`
and to the runner's interpretation block explaining the tight-capacity
assumption and that `event_capacity` must be increased for inputs with
coincident or shared-edge geometry.

---

### Low — Spatial point-ordering + boundary event combination path is not unit-tested

**File:** `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py:555-558, 576-579`

Both the validated device-count path and the boundary event path compute
`point_id_group_capacity` from `ordered_points` (after spatial reordering):
```python
point_id_group_capacity = max(
    1,
    max(_record_id(point) for point in ordered_points) + 1,
)
```
The unit tests for the boundary event route always use `point_order_mode="natural"`.
No test exercises `count_mode=boundary_event_point_id_count_device_columns` with
a non-natural `point_order_mode`. A regression where spatial reordering corrupts
IDs or changes the record structure would only be detected on the pod.

**Required before benchmark use:** Add a unit test with
`count_mode="boundary_event_point_id_count_device_columns"` and
`point_order_mode="x_then_y"` (or any non-natural mode) to confirm that
`_record_id` correctly resolves IDs from the reordered representation.

---

## Review Answers

### Q1 — Does Goal3300 preserve the app-agnostic native-engine boundary?

**Yes.** The native layer sees only `first_boundary_crossing_device_columns`
and `grouped_count_by_point_id_device_columns` — both generic closed-shape
primitives. The `_PIP_BOUNDARY_EVENT_COUNT_MODE` constant and the routing
logic that chooses it live entirely in Python. The `native_engine_boundary`
payload field correctly states the boundary. No RayJoin-specific logic is
visible in `optix_runtime.py` at the call sites.

### Q2 — Does the new route correctly disclose the non-membership contract?

**Yes, in all relevant places:**

- `_run_prepared_boundary_event_grouped_count_device_columns` returns
  `"positive_membership_equivalent": False` and uses the contract string
  `"point_closed_shape_first_boundary_event_count_by_point_id"`.
- The app summary sets `positive_hit_row_count = None`,
  `positive_assignment_count = None`, `boundary_event_row_count = row_count`,
  and `boundary_event_contract_not_positive_membership = True`.
- `output_contract` uses the unambiguous string
  `"point_closed_shape_first_boundary_event_count_by_point_id_device_columns"`,
  not any positive-hit variant.
- `device_resident_continuation_status` explicitly contains "this is not a
  PIP membership contract".
- The runner's `interpretation.rtdl_pip_count_mode` block documents the
  distinction in prose.

The only disclosure gap is the warmup-loop guard omission described under
the medium finding above.

### Q3 — Does the runner avoid treating this as paper reproduction or `rtdl_beats_rayjoin` evidence?

**Yes.** `CLAIM_BOUNDARY` is all-False. `build_comparison_rows` labels the
boundary event PIP row as `"rtdl_boundary_event_count_not_pip_membership"`
rather than `"matching_visible_pip_count"`. The runner `status` is set to
`"pass_with_optimization_gap"` — not `"pass"`. The interpretation block
explicitly states the route is not a positive membership-count contract. The
test at line 123 programmatically asserts every value in `CLAIM_BOUNDARY` is
False via `self.assertTrue(all(value is False for value in MODULE.CLAIM_BOUNDARY.values()))`.

### Q4 — Are the tests strong enough to prevent accidental claim-boundary regression?

**Mostly yes, with one meaningful gap.** The following regressions would be
caught immediately:

- Removing `boundary_event_contract_not_positive_membership` from the payload
  (runner raises `RuntimeError` on repeat, contract test asserts `assertTrue`).
- Setting `positive_assignment_count` to a non-None value in the boundary
  event path (contract test asserts `assertIsNone`).
- Using the wrong `output_contract` string (contract test asserts equality).
- Setting any `CLAIM_BOUNDARY` flag to True (runner test asserts all-False).

The meaningful gap: the guard's failure branch is untested, and the guard
does not apply to warmup calls. A regression that silently omits the flag
would pass all tests if the omission only occurred on warmup samples.

### Q5 — What must be fixed before using this as a v2.8 benchmark data point?

In priority order:

1. **Extend the disclosure guard to warmup calls and test its failure branch.**
   Without this, warmup regressions are invisible.

2. **Split or document the two-phase `prepared_query_sec` timing.** Benchmark
   artifacts with a single timing number for two GPU operations cannot support
   a per-phase claim.

3. **Document the tight event-capacity assumption and the overflow behavior
   for coincident-edge geometry.** Any real-world dataset with grid-aligned
   polygons could trigger the overflow guard unexpectedly.

4. **Add a unit test for the `point_order_mode` + boundary event combination.**
   The pod validates correctness for the default ordering only; a reorder
   regression is currently test-blind.

---

## What is Well Done

- The contract string is unique and unambiguous. It cannot be confused with
  any positive-hit contract by string matching.
- `positive_hit_row_count` and `positive_assignment_count` are explicitly `None`
  rather than omitted or zero, which is the correct signal for "not applicable."
- The runtime-level `to_metadata()` and `grouped_count_by_point_id_device_columns`
  correctly propagate the `device_resident_dense_grouped_count_column` residency
  tag and `true_zero_copy_authorized: False`.
- The runner's `build_comparison_rows` correctly branches on `count_mode` to
  label the boundary event row without requiring the count to match RayJoin's
  intersection count.
- The 28-test pod run with no skips confirms the route executes without regression
  on the existing suite.
- All three `claim_boundary` dictionaries — in the app payload, the app's
  `run_rayjoin_suite`, and the runner — are consistently all-False and are
  tested programmatically, not just by inspection.
