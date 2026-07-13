# Antigravity Review Verdict: Goal4860 Planar-Map LSI Row Materialization Repair

**Date:** 2026-07-02
**Verdict Label:** `approve_goal4860_lsi_row_repair_and_resume_section57`

---

## 1. Call-for-Review Questions & Answers

### Question 1: Is this correctly classified as a Section 5.2 LSI row-materialization bug, rather than a Section 5.3/PIP bug?
**Answer:** Yes. The bug describes a mismatch between the LSI scalar counts and the materialized LSI rows (yielding `count == 2, rows == 0` on a minimal witness). This discrepancy occurs purely within the LSI primitive surface before any point-in-polygon (PIP) classifications or topological overlays are evaluated. Correcting LSI output correctness at its source is a Section 5.2 concern; attempting to work around LSI row omission at the Section 5.3/PIP stage would violate pipeline stage boundaries and introduce false logic.

### Question 2: Does the implementation repair a generic public planar-map LSI row contract, rather than hiding a RayJoin application shortcut?
**Answer:** Yes. The implementation introduces a generic C/C++ ABI endpoint:
`rtdl_optix_run_prepared_segment_pair_intersection_prepared_left_grouped_range_direct_intersection_with_predicate_mode`
which is parameterized by a generic `predicate_mode`. In Python, the repair exposes generic `run_raw` and `run` APIs on `PreparedOptixPlanarMapLsi2D`, which does not import or depend on `rtdsl.rayjoin_overlay` or any application-layer modules. No RayJoin dataset-specific logic or application heuristics are embedded in the native C++ or GPU kernels; the repair operates entirely on generic coordinate sets and standard predicate parameters.

### Question 3: Is it acceptable that row materialization now uses the same grouped-range predicate route as the scalar count path?
**Answer:** Yes. In fact, this is the principal correct architectural design. In the previous implementation, count and row paths diverged, which allowed different candidates and geometric predicates to evaluate differently on boundary/endpoint/degenerate cases. Aligning them to use the identical grouped-range path (launching the same GPU pipeline kernel to locate candidates and predicate hits, and then collecting the corresponding pair IDs) guarantees mathematical consistency between counted and materialized intersections.

### Question 4: Are the synthetic witnesses sufficient to show the previously missing row categories: endpoint, endpoint tolerance, endpoint-on-segment, and near-collinear overlap?
**Answer:** Yes. The regression test suite in [goal4860_planar_map_lsi_row_materialization_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/goal4860_planar_map_lsi_row_materialization_test.py) includes test cases targeting:
- Minimal real witness (shared endpoints)
- Endpoint tolerance (very close endpoints within `1e-10 * scale`)
- Near-collinear shared endpoints
- Endpoint-on-segment interior intersections
- Near-collinear overlaps (requiring coordinate projection over collinear bounds)
These match the native coordinates-materialization routines (`try_endpoint`, clamping, and axis projection) implemented in the C++ workload file.

### Question 5: Does the County x Zipcode evidence prove `count == rows == expected == 961165` on the correct large input?
**Answer:** Yes. As documented in [goal4860_county_zipcode_lsi_row_gate_summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4860_county_zipcode_lsi_row_gate_summary.json), the planar-map LSI count and row count are both exactly `961165`, verifying that the correct large input dataset matches the expected outcome exactly, and the count and row quantities are equal.

### Question 6: Does the Australia representative evidence prove `count == rows == expected == 13622`?
**Answer:** Yes. The evidence file [goal4860_au_lsi_row_gate_summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4860_au_lsi_row_gate_summary.json) validates that `planar_map_lsi_count` and `planar_map_lsi_row_count` are both exactly `13622`, matching the expected value.

### Question 7: Are the claim boundaries correct: no Section 5.3/PIP claim, no Section 5.7 overlay claim, and no performance claim?
**Answer:** Yes. The evidence summaries explicitly set `"performance_claim"`, `"section53_pip_claim"`, and `"section57_overlay_claim"` to `false`. The result document explicitly clarifies that these domains remain un-authorized.

### Question 8: Are additional gates required before resuming Section 5.7 from repaired LSI rows?
**Answer:** No additional LSI row-level correctness gates are required. The Section 5.2 LSI row contract gate is satisfied. However, resuming Section 5.7 overlay construction is conditional upon resolving Section 5.3/PIP correctness and Section 5.7 topological builder correctness as separate, independent validation gates.

---

## 2. Technical Evaluation of the Repair

### Host-Device Contract Alignment
The repair aligns the host and device computations. Previously, candidate search, filtering, and refinement diverged. Now:
1. **Pass 1 (Count):** Launches `g_segment_pair_grouped_range_direct_intersection_exact_count.pipe->pipeline` on GPU to get the exact count.
2. **Pass 2 (Collect Pair IDs):** Launches the identical GPU pipeline with the computed count as capacity. If a hit is confirmed on the GPU under `rayjoin_lsi_intersection_device`, the matching `(left.id, right.id)` pair is packed into a 64-bit unsigned integer and saved to `params.pair_output`.
3. **Pass 3 (Refinement & Coordinate Materialization):** The host-side `finalize_segment_pair_intersection_rows` retrieves the downloaded pair IDs, runs the double-precision host-side predicate check `rayjoin_lsi_intersection_host`, and computes high-precision coordinate values using `planar_map_lsi_materialized_intersection_point`.

### Coordinate Materialization Robustness
`planar_map_lsi_materialized_intersection_point` solves floating-point degeneracies through:
- **Tolerant Endpoints:** If endpoints are within `1.0e-10 * scale`, it outputs the exact midpoint coordinate.
- **Collinear Overlap Projection:** When segments are collinear (`denom == 0`), it projects the overlapping sub-intervals along the axis of maximum length (`use_x = abs(rx) >= abs(ry)`) and returns the midpoint of the overlap.
- **Parametric Clamping:** Clamps param values `t` and `u` to `[0.0, 1.0]` under `1.0e-5` float tolerance.
This unified logic ensures that any intersection accepted by the GPU is assigned consistent double-precision coordinates on the host.

---

## 3. Non-Authorization Boundaries

This review does **NOT** authorize:
- **Section 5.3/PIP correctness** (Point-in-Polygon validation is out of scope and remains a future gate).
- **Section 5.7 overlay correctness** (Overlay composition correctness is out of scope and remains a future gate).
- **Section 5.7 performance or speedup claims** (Timings in the logs are accepted as execution proofs, but no relative speedup claims are approved).
- **Broad RayJoin paper reproduction** or general RTDL performance assertions.
