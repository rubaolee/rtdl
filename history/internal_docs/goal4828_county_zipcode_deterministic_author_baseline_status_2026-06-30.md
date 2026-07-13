# Goal4828 Status: County x Zipcode Deterministic Author Baseline and RTDL Comparator Correction

Date: 2026-06-30

## Scope

Dataset under test:

- `same_source_regenerated_cdb`, not exact paper-preprocessed Section 5.7 input.
- Map 0: `/workspace/rayjoin_section57_same_source_cdb/point_cdb/dtl_cnty/dtl_cnty_Point.cdb`
- Map 1: `/workspace/rayjoin_section57_same_source_cdb/point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb`

This goal is correctness-only. Performance remains blocked until byte-level correctness is established against a deterministic reference.

## What Was Done

1. Built a deterministic author baseline from the author code plus the author-reply `t_reported` perturbation.

   The patched author binary produced:

   - Output: `/workspace/rtdl_goal4820_sos_fix/artifacts/goal4828_county_zipcode_author_deterministic/author_deterministic_county_zipcode_overlay.txt`
   - Bytes: `2390767769`
   - SHA256: `e8fed3e7e4691c028ee6c8e8a16a74eb06de5a0ffb20cc2b132ce8646b797b2a`
   - Wall time: `169.338126s`

   This replaces the old Goal4806 author output as the comparison target for this same-source dataset. The old output remains a debug clue only.

2. Compared a partial RTDL full-output run against the deterministic author baseline.

   A direct RTDL output attempt wrote a partial file:

   - Output: `/workspace/rtdl_goal4820_sos_fix/artifacts/goal4828_county_zipcode_rtdl_current_vs_author_deterministic/rtdl_current_county_zipcode_overlay.txt`
   - Partial bytes: `872415232`

   Prefix comparison found a mismatch immediately:

   - First differing byte: offset `440` / byte `441`, line `25`
   - Author line: `9 2 8 9 1 2`
   - RTDL line: `9 2 8 9 5 6`

   Geometry and point ids matched at the first diff; only face ids differed. This isolated the failure to point-location / midpoint-face / face-id creation semantics rather than LSI geometry.

3. Re-read the author determinism summary and author source diff.

   Important correction: the author-reply patch adds `t_reported` perturbation, but does not change the author source's existing equal-`xsect_y` in-primitive slope comparator. I had over-corrected RTDL by changing both layers at once.

   Correct interpretation now used:

   - Keep the author-source internal comparator behavior for equal-`best_y` candidates inside the same primitive/range.
   - Add the author-reply `t_reported` perturbation for cross-primitive OptiX pruning determinism.

4. Corrected RTDL OptiX directed-segment point-location comparator.

   Files changed:

   - `src/native/optix/rtdl_optix_core.cpp`
   - `tests/goal4373_rayjoin_cdb_point_location_route_test.py`

   Effective internal comparator now matches the author source's actual behavior:

   - `query_map_id == 0`: smaller slope wins inside the same primitive/range.
   - `query_map_id != 0`: larger slope wins inside the same primitive/range.

   The `t_reported` perturbation remains:

   - `query_map_id == 0`: `tie_breaker = normalized_slope`
   - `query_map_id != 0`: `tie_breaker = 1.0 - normalized_slope`

   This preserves the author-reply cross-primitive pruning fix without silently rewriting the author source's internal comparator.

5. Rebuilt and tested on the POD.

   POD build and tests:

   - `make build-optix OPTIX_PREFIX=/tmp/optix-sdk-probe CUDA_PREFIX=/usr/local/cuda-12.8 OPTIX_CUDA_ARCH=sm_89`
   - `RTDL_OPTIX_LIB=/workspace/rtdl_goal4820_sos_fix/build/librtdl_optix.so PYTHONPATH=src python3 -m unittest tests.goal4374_rayjoin_exact_paper_suite_test tests.goal4373_rayjoin_cdb_point_location_route_test`
   - Result: `Ran 32 tests ... OK`

6. Re-ran the official public County x Soil sample after the comparator correction.

   Result:

   - Byte-equal: `true`
   - Bytes: `16631243`
   - SHA256: `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`

   This proves the correction did not regress the official public validation sample.

7. Ran County x Zipcode no-output RTDL core-stage summary after comparator correction.

   Artifact:

   - `/workspace/rtdl_goal4820_sos_fix/artifacts/goal4828_county_zipcode_no_output_after_comparator_restore/summary.json`

   Key values:

   - Outer wall: `187.766137s`
   - LSI intersections: `965844`
   - Map 0 input: `8662896` chains, `17325792` points
   - Map 1 input: `23931046` chains, `47862092` points
   - Midpoint counts after finite filtering: map0 `123056`, map1 `141486`
   - Nonfinite midpoints dropped: map0 `26`, map1 `24`

   This is not a byte-equality proof, but it confirms the core no-output route runs and LSI count matches the author log line for this same-source run.

## Problems Found

1. The previous RTDL comparator change was overbroad.

   I incorrectly treated the author-reply `t_reported` tie-break direction as also authorizing a change to the author source's in-primitive equal-height comparator. The source diff does not support that. This was corrected.

2. Full RTDL output assembly is too heavy for the current harness.

   The RTDL full-output path spends a long time in Python-side output-chain assembly before writing. One direct session wrote only a partial `872415232` byte file before the execution harness stopped. A background attempt also failed to complete cleanly.

   This is a product/harness blocker for full byte comparison on this large same-source dataset. It is not a performance result.

3. POD quota was temporarily hit.

   A failed remote edit while quota was exhausted truncated the remote `src/native/optix/rtdl_optix_core.cpp`. I removed obsolete/partial large outputs and restored the full file from the local workspace, then rebuilt and passed tests. The local workspace file was not truncated.

## Current Status

Current verified facts:

- Deterministic author baseline exists for County x Zipcode same-source.
- RTDL public County x Soil remains byte-equal after the comparator correction.
- RTDL no-output County x Zipcode core route runs and reports the expected LSI count.
- Full byte-equality for County x Zipcode after the corrected comparator is not yet proven.

Current blocker:

- Need a reliable way to compare RTDL output against the deterministic author baseline after the corrected comparator without relying on the current full Python list-assembly plus 2.4GB file write path.

## Next Work

Recommended next goal:

1. Build a bounded current-code prefix/hash comparison that does not require completing the whole 2.4GB output file.
2. It must use the corrected comparator build.
3. It should compare at least the first N chains and, if possible, an incremental output hash/chunk stream against the deterministic author baseline.
4. If the prefix now matches, continue toward a streaming full-output hash strategy.
5. If the prefix still mismatches, diagnose the first mismatch as a correctness gap.

Forbidden next steps:

- Do not run performance.
- Do not compare against the old nondeterministic Goal4806 author output as truth.
- Do not claim full Section 5.7 correctness.
- Do not add RayJoin-only hidden kernels.
