# Goal2370 - Gemini Review: Goal2369 RTNN Prepared Pod Results

**Reviewer:** Gemini Agent
**Date:** 2026-05-19

## Context

This independent review assesses the Goal2369 RTNN prepared column pod result intake. Goal2368 introduced a pod runner for the v2.2 RTNN campaign, comparing `records` + `run-optix`, `packed-columns` + `run-optix`, and `packed-columns` + `prepared-optix` at 65,536 and 262,144 synthetic 3D points on an RTX A5000 with driver 570.211.01. All rows completed successfully.

## Review Questions & Verdicts

### 1. Do the report tables accurately reflect the JSON artifacts?
**Verdict:** accept
**Evidence:** A spot-check of `rtdl_records_run_optix_3d_65536_r002_k50.json`, `rtdl_packed_run_optix_3d_65536_r002_k50.json`, and `rtdl_packed_prepared_optix_3d_65536_r002_k50.json` confirms that the `Pack sec`, `Prepare sec`, `Runs sec` (specifically the warm run time which corresponds to `elapsed_sec`), and `Rows` values in the report's "Results" table accurately reflect the corresponding fields in the JSON artifacts. The calculation of "Ratios" also appears correct based on these values.

### 2. Is the interpretation correct that packed columns are the current large performance win, while current `prepared-optix` does not improve warm steady-state time over packed `run-optix`?
**Verdict:** accept
**Evidence:** The report's "Interpretation" section states: "The packed-column path is the real performance fix on the current v2.2 basis." and "The current `prepared-optix` path is not faster than packed `run-optix` at steady state."
The "Ratios" table clearly shows "Record warm / packed warm" ratios of 61.22x and 28.70x, indicating a significant performance win for packed columns.
Conversely, "Packed warm / prepared warm" ratios are 0.94x and 0.97x, demonstrating that `prepared-optix` is not faster than packed `run-optix` in warm steady-state.
The `tests/goal2369_rtnn_prepared_column_pod_results_test.py` also explicitly verifies these performance characteristics in `test_packed_columns_are_the_current_large_performance_win`, asserting `assertGreater(records_65["elapsed_sec"] / packed_65["elapsed_sec"], 50.0)` and `assertLess(packed_65["elapsed_sec"] / prepared_65["elapsed_sec"], 1.05)`.

*Self-correction:* I was unable to inspect the `goal2368_pod.log` due to ignore patterns, but the explicit `ok: true` values within the JSON artifacts and the `test_all_pod_artifacts_are_present_and_successful` test provide sufficient confidence that the runs completed successfully.

### 3. Is the design conclusion justified: future `prepared_bounded_neighbor_search_3d` needs a native/device-resident search structure, not only Python packed-input reuse?
**Verdict:** accept
**Evidence:** The report's "Interpretation" explicitly states: "The phase timings still show per-run native `prepare` and `upload` work... So the next v2.x primitive work is precise: `prepared_bounded_neighbor_search_3d` must prepare and reuse the native/device search structure, not just reuse Python packed records."
This is directly corroborated by `docs/research/future_version_to_do_list.md` under "RTNN-Informed 3D Bounded Neighbor Search": "Goal2369 pod results showed that current prepared execution reuses Python packed inputs but not a native/device-resident 3D neighbor search structure: packed `run-optix` and packed `prepared-optix` have similar warm times. The next real prepared step must retain the native search structure/device buffers across query runs."

### 4. Are the claim boundaries correct? The report must not authorize RTNN paper equivalence, RT-core acceleration, broad speedup, or release readiness.
**Verdict:** accept-with-boundary
**Evidence:** The "Boundary" section in the report explicitly states: "This evidence does not authorize RTNN paper equivalence, RT-core acceleration, broad speedup, or release readiness."
The JSON artifacts themselves contain `claim_boundary` fields with `false` values for `broad_rt_core_speedup_claim_authorized`, `paper_equivalent_rtnn_row`, and `rtdl_speedup_claim_authorized`.
The `test_all_pod_artifacts_are_present_and_successful` test verifies these `false` claims directly.
The `test_report_states_current_prepared_boundary` test also asserts the presence of boundary-related text in the report markdown.
The `docs/research/future_version_to_do_list.md` also consistently maintains similar boundary conditions for related future work.

The "accept-with-boundary" verdict is used here to acknowledge that the claim boundaries are correctly stated and reinforced across multiple artifacts, indicating a strong adherence to conservative claim management.

### 5. Are the tests sufficient for this pod-artifact intake?
**Verdict:** accept
**Evidence:** The `tests/goal2369_rtnn_prepared_column_pod_results_test.py` file contains comprehensive tests that:
- Verify the presence and success (`ok: true`) of all expected JSON artifacts.
- Validate the specific performance ratios (packed vs. records, prepared vs. packed).
- Confirm the inclusion of critical interpretive and boundary statements within the main report markdown file.
These tests effectively cover the critical aspects of data integrity, performance interpretation, and adherence to claim boundaries, making them sufficient for this intake.

## Overall Conclusion

The Goal2369 RTNN prepared column pod results are well-documented, and the interpretation is strongly supported by the provided data and verified by automated tests. The report accurately reflects the JSON artifacts, and the design conclusions regarding the need for a native/device-resident search structure for future `prepared_bounded_neighbor_search_3d` are justified. The claim boundaries are appropriately conservative and clearly stated across all relevant documents and artifacts. The provided tests are thorough and sufficient for validating this intake.

## Next Steps from Report

- Promote packed-column inputs as the serious-performance path in RTNN-facing tutorials and benchmark docs.
- Build a true native prepared 3D bounded-neighbor handle that keeps the search-point structure/device buffers alive across queries.
- Only after that, retest prepared execution against RTNN at larger scales and with separate query/search sets.
