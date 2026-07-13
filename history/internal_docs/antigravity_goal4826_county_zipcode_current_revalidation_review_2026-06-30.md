# Review Result: Goal4826 County x Zipcode Current-Line Revalidation Review

**Date:** 2026-06-30
**Reviewer:** Antigravity (AI Coding Assistant)

---

## Verdict Label

`approve_goal4826_correctly_blocks_county_zipcode_and_authorize_goal4827_mismatch_diagnosis`

---

## Review Question Answers

1. **Did Goal4826 correctly remain on the current v2.14-centered RTDL line, not V4 continuation?**
   Yes. The run utilized the current active core codebase tree (`/workspace/rtdl_goal4820_sos_fix`) on the POD rather than attempting a V4 continuation. This maintains focus on the active product/core line.

2. **Was it correct to reuse old Goal4806 data/artifact paths only as inputs or comparison targets, not as current product evidence?**
   Yes. The old Goal4806 paths and files (such as `author_overlay_debug.overlay.txt`) were only used as inputs or external comparison targets to compute differences, not as direct product evidence. All current product evidence is generated fresh from current-line runs.

3. **Does the midpoint finiteness probe justify the product-level finite-query repair?**
   Yes. The probe results in `goal4826_midpoint_finiteness_probe.json` indicate that LSI coordinates can materialize as nonfinite values (e.g., `nan`, `inf`, `-inf`), resulting in 69 nonfinite LSI rows, 26 map0 nonfinite midpoints, and 24 map1 nonfinite midpoints. Passing nonfinite coordinates to native point-location kernels caused a crash (`RuntimeError: RayJoin CDB point-location query points must be finite`), justifying the filtering repair.

4. **Is the finite-query repair properly bounded as a core/product invariant rather than a RayJoin-specific shortcut?**
   Yes. The repair is implemented at the core Python/numpy helper level (`_midpoint_points_from_lsi_rows_numpy` and `_midpoints_for_sorted_xsects`) to filter nonfinite points and keep midpoint owners properly synchronized, rather than implementing a RayJoin-specific bypass. It enforces the general product invariant that native kernels must not receive nonfinite query inputs.

5. **Do the local and POD tests sufficiently cover this finite-query repair?**
   Yes. Two unit/regression tests (`test_lsi_midpoint_projection_drops_nonfinite_points_with_telemetry` and `test_output_chain_midpoint_projection_drops_nonfinite_points_with_telemetry`) were introduced and successfully executed (30 tests OK) both locally and on the POD.

6. **Does the after-fix County x Zipcode run prove completion of the run but not byte-equality?**
   Yes. The run completed successfully without crashing, but failed byte-equality verification:
   - **SHA256**: `5a1808def771992e6532bbd1edd05a9625531b9e39a235578a11b5e29c395267` (Current RTDL output) vs `e8fed3e7e4691c028ee6c8e8a16a74eb06de5a0ffb20cc2b132ce8646b797b2a` (Author baseline)
   - **Bytes**: `2,388,737,142` vs `2,390,767,769`
   - **Chain Count**: `29,253,910` vs `29,254,027`
   - **Face Count**: `115,515` vs `115,490`

7. **Is the report correct to block performance claims and require mismatch diagnosis next?**
   Yes. Because correctness has not been verified (as demonstrated by the byte-equality failure and mismatching counts), performance claims are strictly blocked. Diagnosing the correctness mismatch is the correct next step.

8. **Should Goal4827 diagnose County x Zipcode before returning to Block x Water or broader Section 5.7 work?**
   Yes. The mismatch must be diagnosed and resolved on the simpler County x Zipcode case before returning to Block x Water or other broader Section 5.7 scaling.

---

## Strict Boundaries & Constraints

* **No V4 Continuation:** The work strictly avoided V4 continuation and remained on the current v2.14-centered RTDL line.
* **No Same-Source-As-Exact-Paper:** The input provenance is explicitly tracked as `same_source_regenerated_cdb`. These same-source regenerated CDBs are not treated as exact original paper inputs.
* **No Performance Claims Before Byte Equality:** Performance claims remain unauthorized. Byte-equality correctness is a strict prerequisite before any performance claims can be asserted.
