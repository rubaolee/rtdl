# Independent Gemini Review for Goal2772: Hit Stream Event Ordered Grouped Richer Reductions

Date: 2026-05-31

## Verdict: accept-with-boundary

Goal2772 is accepted with boundary. This is a bounded v2.5 primitive/runtime step, not a release gate and not a public performance claim.

## Review Questions and Answers

### 1. Does Goal2772 keep the generic engine/app boundary intact by reducing only generic hit-stream columns grouped by `ray_id`?

**Answer:** Yes.

**Evidence:**
The report `docs/reports/goal2772_hit_stream_event_ordered_grouped_richer_reductions_2026-05-31.md` explicitly states: "This is still a primitive/runtime step, not an app workload. The grouping key is still `ray_id`, and every reduced value comes from generic hit-stream columns." The test `tests/goal2772_hit_stream_event_ordered_grouped_richer_reductions_test.py` further confirms this in `test_public_method_records_richer_reduction_fields` by asserting `grouping_key: "ray_id"`.

### 2. Does the richer grouped kernel correctly add min/max and first/last row-order outputs without introducing app-specific semantics?

**Answer:** Yes.

**Evidence:**
The report `docs/reports/goal2772_hit_stream_event_ordered_grouped_richer_reductions_2026-05-31.md` lists the newly added columns: `group_primitive_id_min`, `group_primitive_id_max`, `group_first_hit_row_index`, `group_last_hit_row_index`, `group_first_primitive_id`, and `group_last_primitive_id`. It clarifies that these are "Generic primitive-id count/sum/xor/min/max/first/last reductions."
The test `tests/goal2772_hit_stream_event_ordered_grouped_richer_reductions_test.py` contains `test_grouped_kernel_adds_min_max_first_last_fields`, which asserts the presence of these new fields and their atomic update logic within the CuPy kernel source. The `test_runtime_smoke_richer_grouped_reductions` further validates the correct numerical outputs for these new fields during a smoke test.

### 3. Does the helper still wait on the producer CUDA event before the CuPy kernel launch, and does it avoid host materialization of hit rows or grouped output columns before the consumer completes?

**Answer:** Yes.

**Evidence:**
The report `docs/reports/goal2772_hit_stream_event_ordered_grouped_richer_reductions_2026-05-31.md` describes the execution flow: "A separate CuPy consumer stream waits on that CUDA event. The CuPy RawKernel reduces the stored hit rows by `ray_id` and writes grouped output columns on device. Only the small summary is materialized after the consumer stream completes."
The `test_helper_keeps_richer_outputs_device_resident_until_consumer_finishes` in `tests/goal2772_hit_stream_event_ordered_grouped_richer_reductions_test.py` verifies the presence of `streamWaitEvent` before the kernel launch and confirms the use of `cp.asarray` (device arrays) for grouped buffers, with no `cp.asnumpy` (host arrays) calls for these buffers before `consumer_stream.synchronize()`.

### 4. Does the first/last row-order contract honestly reflect the observed hit stream order rather than implying sorted-by-ray ordering?

**Answer:** Yes.

**Evidence:**
The report `docs/reports/goal2772_hit_stream_event_ordered_grouped_richer_reductions_2026-05-31.md` provides an example of observed hit-stream row order (`ray_ids = [0, 2, 0, 2]`, `primitive_ids = [0, 0, 1, 1]`) and then shows the corresponding `group_first_hit_row_index = [0, -1, 1]` and `group_last_hit_row_index = [2, -1, 3]`. These indices directly map to the original, unsorted hit-stream, confirming that the order is preserved. The `test_runtime_smoke_richer_grouped_reductions` in `tests/goal2772_hit_stream_event_ordered_grouped_richer_reductions_test.py` explicitly sets up a test case to validate this exact behavior.

### 5. Are the metadata/report boundaries honest: no true-zero-copy, no public speedup, no arbitrary continuation, no unbounded stream, and query rays still packed on host?

**Answer:** Yes.

**Evidence:**
The report `docs/reports/goal2772_hit_stream_event_ordered_grouped_richer_reductions_2026-05-31.md` clearly lists "Explicit non-claims" covering all these points, e.g., "This does not authorize true zero-copy," "This does not authorize public speedup claims," etc. The `test_public_method_records_richer_reduction_fields` in `tests/goal2772_hit_stream_event_ordered_grouped_richer_reductions_test.py` asserts that the `metadata` dictionary contains `"true_zero_copy_authorized": False` and `"public_speedup_claim_authorized": False`.

### 6. Are the tests and pod evidence sufficient for this narrow runtime primitive, including the fixed `group_last_hit_row_index` initializer bug?

**Answer:** Yes.

**Evidence:**
The report `docs/reports/goal2772_hit_stream_event_ordered_grouped_richer_reductions_2026-05-31.md` details comprehensive "Focused validation" and "Corrected v2.5 hit-stream regression" tests, all passing. Crucially, it notes: "During initial pod testing, the `group_last_hit_row_index` initializer bug was found and fixed: it must initialize to `0`, not the `-1` sentinel, before the `atomicMax` pass. Empty groups are still finalized back to `-1`." The `test_runtime_smoke_richer_grouped_reductions` within `tests/goal2772_hit_stream_event_ordered_grouped_richer_reductions_test.py` provides specific, detailed assertions validating the output of all new grouped reduction fields, demonstrating sufficient test coverage for this primitive.
