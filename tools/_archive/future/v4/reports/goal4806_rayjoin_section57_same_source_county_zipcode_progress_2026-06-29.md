# Goal4806 RayJoin Section 5.7 County x Zipcode Progress

Date: 2026-06-29

## Status

Goal4806 is still not complete as a full Section 5.7 polygon-overlay paper-reproduction claim.

The serious POD line is now past the earlier setup blockers: RayJoin author code builds, a same-source regenerated County x Zipcode CDB is available, RTDL OptiX runs on the same data, and V4+Numba now has a valid exact RayJoin LSI device-column route that Numba can consume. The remaining blocker has narrowed: V4+Numba has a correct post-traversal candidate-stage continuation, but it has not yet produced a full overlay output/topology digest that can be compared end-to-end against author code and the V2.14 exact-suite route.

## Evidence Location

Evidence directory:

`tools/_archive/future/v4/evidence/goal4806_rayjoin_section57_same_source_county_zipcode_2026-06-29/`

Included evidence:

- `section57_same_source_cdb_tree.json`
- `section57_same_source_county_zipcode_preflight.json`
- `section57_overlay_county_zipcode_author_rt_iter0.json`
- `section57_overlay_county_zipcode_rtdl_optix_retry_fixed.json`
- `section57_overlay_county_zipcode_rtdl_optix_after_midpoint_fix.json`
- `section57_overlay_county_zipcode_rtdl_optix_after_midpoint_fix.overlay_optix.digest.txt`
- `section57_v4_numba_candidate_measurements.json`
- `section57_v4_numba_candidate_measurements_exact_columns.json`
- `section57_v4_numba_candidate_measurements_exact_xy_columns_nohash.json`
- `section57_v4_numba_candidate_measurements_exact_xy_digest_after_native_fallback_nohash.json`
- `section57_overlay_county_zipcode_v4_numba.json`
- `section57_overlay_county_zipcode_v4_numba_digest_selector_nohash.json`
- `section57_overlay_county_zipcode_v4_numba.md`
- `section57_overlay_summary_refreshed.json`
- `section57_overlay_summary_refreshed.md`
- `section57_v4_numba_exact_grouped_count_probe.json`
- `rayjoin_goal4806_author_compat_combined.patch`
- `rayjoin_build_polyover_after_output_chain_patch.log`
- `rtdl_goal4806_build_optix.log`

## What Was Actually Run

Hardware:

- NVIDIA RTX 4000 Ada Generation
- Driver 550.127.05
- CUDA driver capability shown by `nvidia-smi`: 12.4

Author source:

- `https://github.com/pwrliang/RayJoin`
- Commit: `02bf6220d6d20b04af77ee20364eced75cc029c9`
- Built binaries:
  - `/workspace/RayJoin_fresh/release/bin/query_exec`
  - `/workspace/RayJoin_fresh/release/bin/polyover_exec`

Author compatibility patches were required on this POD:

- NVTX marker no-op patch for CUDA 12.8 header/API compatibility.
- `double2` hash/equality patch for `output_chain.h` with GCC 13/CUDA 12.8.

Input:

- Exact author preprocessed Dryad CDB share is currently unavailable: the public Dryad share redirects to a `404`.
- This run uses `same_source_regenerated_cdb`, built from the public ArcGIS County and Zipcode sources named by the RayJoin workflow.
- County CDB: 8,662,896 chains/segments; 17,325,792 points.
- Zipcode CDB: 23,931,046 chains/segments; 47,862,092 points.

This is serious large data, not toy data. It is not the exact preprocessed paper input.

## Result: Author vs RTDL OptiX On Same-Source CDB

Author RT run:

- File: `section57_overlay_county_zipcode_author_rt_iter0.json`
- `elapsed_sec`: `827.591928564012`
- Author timing notes:
  - `Read map 1`: `820748.0 ms`
  - `Computer output polygons`: `99.3578 ms`
  - `Intersection edges`: `17.4341 ms`

RTDL OptiX run:

- File: `section57_overlay_county_zipcode_rtdl_optix_retry_fixed.json`
- `total_median_sec`: `100.59438601136208`
- `compute_without_load_pack_median_sec`: `99.19385035336018`
- `load_pack_median_sec`: `1.4005356580018997`
- `partner_cache.enabled`: `true`
- LSI emitted rows: `965844`
- midpoint PIP:
  - map0 midpoints: `123056`
  - map1 midpoints: `141486`
  - map0 non-finite midpoints dropped: `26`
  - map1 non-finite midpoints dropped: `24`

Same-source elapsed ratio:

- Author elapsed / RTDL total: about `8.227x`
- Author elapsed / RTDL compute-without-load-pack: about `8.343x`

Claim boundary:

This is a same-source engineering comparison, not an exact paper-input claim and not yet a full output-equality claim. The author run is dominated by CDB read time on this regenerated input, while RTDL used its packed cache path. The result is useful for engineering, but it must not be published as an unqualified RayJoin paper speedup.

## Fix Applied In RTDL

The RTDL overlay path initially failed on the same-source data because generated midpoint query points contained `NaN`/`Inf`.

Fix:

- `_midpoint_points_from_lsi_rows_numpy` now drops non-finite midpoint coordinates before point-location classification.
- `_midpoints_for_sorted_xsects` now applies the same non-finite midpoint filter during full output-chain assembly.
- The drop counts are recorded in the result JSON:
  - `map0_nonfinite_midpoints_dropped`
  - `map1_nonfinite_midpoints_dropped`

Validation:

- Local focused tests passed: `38 tests OK`.
- POD focused gate passed: `14 tests OK`.
- Full POD RTDL OptiX output-assembly retry then completed.

### RTDL Full Output Assembly Probe

After the output-chain midpoint fix, the RTDL OptiX route completed full overlay output assembly on the same-source County x Zipcode CDB.

File:

- `section57_overlay_county_zipcode_rtdl_optix_after_midpoint_fix.json`

Remote output artifact:

- `/workspace/rtdl_goal4806_fast_min/artifacts/section57_same_source_county_zipcode_output_digest/section57_overlay_county_zipcode_rtdl_optix_after_midpoint_fix.overlay_optix.txt`

Output digest:

- size: `2.3G`
- line count: `87667107`
- sha256: `0b19a536144b628ff59623146a271759f00df9a0a7bbd9ada5ed997318d54ae8`
- output chains: `29253799`
- face count: `119729`

Timing:

- total: `389.2522244974971 sec`
- load/pack: `54.44365684688091 sec`
- compute without load/pack: `334.80856765061617 sec`
- LSI native hot call: `11.482726581394672 sec`
- point-location prepare: `5.287372961640358 sec`
- LSI row materialization: `3.169036753475666 sec`
- LSI row sort: `2.4750871509313583 sec`
- output-chain assembly: `225.46251025795937 sec`
- output-chain write: `77.58183673769236 sec`

Interpretation:

This is a real full-output RTDL run on serious same-source data, not a toy run. It also shows that the full paper-reproduction output path is now dominated by Python-side output construction and file writing, not by RT-core traversal. That bottleneck must be treated as an engineering fact, not hidden under the faster no-output hot-path timings.

Author output-mode boundary:

- The author `polyover_exec -output` run on the same-source CDB failed after `20.602055735886097 sec` with `SIGABRT`.
- Therefore the current evidence does not establish output equality against author output on this regenerated input. It establishes that RTDL can produce a large full overlay output where the author output-mode executable aborts on this input.

## Result: V4 + Numba

V4+Numba is not release-ready for a full RayJoin Section 5.7 polygon-overlay paper-reproduction claim yet, but the previous device-column blocker has been removed.

### Candidate Pair-Column Probe

File: `section57_v4_numba_candidate_measurements.json`

Status: `no_rows_measured`

Blocker:

`cannot wrap an overflowed device pair-column stream; capacity=1152144 required_capacity=10142618; overflow_policy=fail_closed`

Interpretation:

The candidate stream is much larger than the exact count. Retrying with a bigger capacity would measure candidate rows, not exact Section 5.7 overlay rows. Treating candidate rows as exact would be wrong.

### Exact LSI Device-Column Primitive

Implemented surface:

- Native C ABI: `rtdl_optix_prepared_segment_pair_exact_device_columns_prepared_left`
- Python wrapper: `PreparedOptixSegmentPairIntersection.exact_device_columns_prepared_left(...)`
- Predicate lock: the Section 5.7 probe runs inside `_rayjoin_lsi_predicate_env("optix")`, so it measures RayJoin LSI semantics rather than generic segment-pair intersection.
- Device-column payload: `left_id`, `right_id`, `intersection_point_x`, and `intersection_point_y`.
- Native finite-point fallback: degenerate/parallel denominator cases now emit a finite overlap representative instead of `NaN`/`Inf` in the x/y device columns.

POD validation:

- Local focused tests: `37 tests OK` after the x/y column extension.
- POD focused tests: `12 tests OK` after the x/y column extension.
- POD focused planner/probe tests: `12 tests OK` after the digest candidate and selector-scoreboard update.
- OptiX backend rebuilt successfully on the RTX 4000 Ada POD.

### V4+Numba Exact-Column Measurement

Files:

- `section57_v4_numba_candidate_measurements_exact_columns.json`
- `section57_v4_numba_candidate_measurements_exact_xy_columns_nohash.json`

Rows:

- `v4_numba_post_traversal_segmented_counts`
  - `correctness_status`: `stage_count_pass_full_overlay_hash_not_confirmed`
  - `candidate_row_count`: `965844`
  - `expected_lsi_count`: `965844`
  - `segmented_count_sum`: `965844`
  - `intersection_point_columns_present`: `true`
  - `host_materialization_in_hot_path`: `false`
  - `measured_total_sec`: `0.22065869718790054`
  - `candidate_column_traversal_sec`: `0.006589513`
  - `numba_elapsed_sec`: `0.2079133614897728`
  - `native_symbol`: `rtdl_optix_prepared_segment_pair_exact_device_columns_prepared_left`
- `v4_numba_post_traversal_mask_compact`
  - `correctness_status`: `stage_count_pass_full_overlay_hash_not_confirmed`
  - `compact_count`: `965844`
  - `intersection_point_columns_present`: `true`
  - `host_materialization_in_hot_path`: `true`
  - `measured_total_sec`: `0.12310758978128433`
  - rejected by the selector because the full overlay hash is not confirmed; it would also be unsafe as a hot-path route because it uses a host prefix sum.

Selector result:

- File: `section57_overlay_county_zipcode_v4_numba.json`
- selected plan: `null`
- selection policy: `fastest_valid`
- claim classification: `not_release_ready`
- rejection reasons: both measured rows are rejected as `correctness_not_pass` because the full overlay topology/geometry hash has not been produced yet.

### V4+Numba Exact LSI Stream Digest

File:

- `section57_v4_numba_candidate_measurements_exact_xy_digest_after_native_fallback_nohash.json`

Rows:

- `v4_numba_post_traversal_segmented_counts`
  - `candidate_row_count`: `965844`
  - `expected_lsi_count`: `965844`
  - `segmented_count_sum`: `965844`
  - `measured_total_sec`: `0.18558117002248764`
  - `candidate_column_traversal_sec`: `0.007678389`
  - `host_materialization_in_hot_path`: `false`
- `v4_numba_post_traversal_mask_compact`
  - `compact_count`: `965844`
  - `measured_total_sec`: `0.12148618698120117`
  - `host_materialization_in_hot_path`: `true`
- `v4_numba_post_traversal_lsi_stream_digest`
  - `row_count`: `965844`
  - `left_id_sum`: `3997578913974`
  - `right_id_sum`: `10977120967318`
  - `intersection_x_micro_sum`: `-89909278587144`
  - `intersection_y_micro_sum`: `36405147849366`
  - `nonfinite_intersection_points`: `0`
  - `measured_total_sec`: `0.16212832927703857`
  - `host_row_materialization_used`: `false`

Selector result:

- File: `section57_overlay_county_zipcode_v4_numba_digest_selector_nohash.json`
- selected plan: `null`
- classification: `blocked_missing_author_baseline`
- scoreboard status:
  - `v4_numba_post_traversal_mask_compact`: `measured_rejected`, `correctness_not_pass`
  - `v4_numba_post_traversal_segmented_counts`: `measured_rejected`, `correctness_not_pass`
  - `v4_numba_post_traversal_lsi_stream_digest`: `measured_rejected`, `correctness_not_pass`

Interpretation:

This removes the previous V4+Numba x/y-stream blocker: Numba now consumes the exact RTDL LSI device stream, including finite intersection x/y columns, and produces a stable stream digest without materializing the full row stream on the host. It still does not complete Section 5.7 polygon overlay because the digest is for the exact LSI stream, not for the final overlay topology/geometry output. The selector correctly records the measured rows while refusing to select them for release.

Interpretation:

This is real V4+Numba progress: RTDL now emits the same exact RayJoin LSI row count as the full RTDL OptiX route (`965844`) into device-resident columns, including finite intersection x/y columns, and Numba consumes that stream without hot-path row materialization on the segmented-count and digest routes. It is not yet a full app-level speedup claim because the end-to-end overlay output/topology digest has not been produced. The selector correctly remains fail-closed.

### Exact Grouped-Count Probe

File: `section57_v4_numba_exact_grouped_count_probe.json`

Result:

- `correctness_status`: `fail`
- scalar exact count route: `1152144`
- device grouped-count `source_row_count`: `382946`
- Numba sum over device count column: `382946`
- OptiX grouped-count wall time: `0.06614872813224792 sec`
- Numba sum time: `0.26569657772779465 sec`

Interpretation:

The existing grouped-count device-column primitive is device-resident and Numba can consume the CUDA count column, but it is not semantically aligned with the Section 5.7 exact overlay LSI contract. It cannot be used as a valid Section 5.7 result.

### Numba Toolchain Note

Default POD venv:

- Python 3.12
- Numba 0.65.1
- llvmlite 0.47.0

This stack failed even for a minimal CUDA kernel:

`Unsupported .version 8.7; current version is '8.4'`

Compatible test stack:

- Python 3.11
- Numba 0.60.0
- CUDA 12.4 NVVM from `nvidia-cuda-nvcc-cu12==12.4.131`

This stack successfully ran a minimal Numba CUDA kernel on the POD when the CUDA 12.4 NVVM/PTX environment is supplied before Python starts. V4+Numba tests on driver 550 should use this compatible stack or a newer driver that accepts PTX 8.7.

## Current Engineering Problems

1. Exact RayJoin paper preprocessed CDB inputs are not available from the public Dryad share.
2. Same-source regenerated CDB is serious and useful, but it is not the exact paper input.
3. RTDL OptiX compute runs and is much faster than the author run on this same-source input, but the author timing is dominated by CDB read time and RTDL used a packed cache path.
4. RTDL now produces a full overlay output on this same-source run, but output equality against author output has not been established because the author `polyover_exec -output` path aborts on the same regenerated input.
5. V4+Numba now has a valid exact RayJoin LSI device-column primitive with ids and finite intersection x/y plus a Numba stream digest, but it has not yet produced a full overlay output/topology digest for end-to-end author/V2.14 comparison.
6. Older segment-pair count surfaces still disagree across contracts on this same-source run:
   - RTDL overlay emitted rows: `965844`
   - scalar exact count probe: `1152144`
   - grouped-count device-column source rows: `382946`
7. The automatic V4+Numba primitive selector records the measured rows as `measured_rejected` and remains fail-closed because they are stage-count/digest correct but do not yet carry a full overlay topology/geometry hash.

## Non-Stupid Next Step

Do not publish a V4+Numba full RayJoin Section 5.7 success claim from the current evidence.

The correct next engineering step is to consume the exact `(left_id, right_id, x, y)` device stream in an end-to-end overlay correctness artifact. There are two honest options:

1. let Numba compute the topology/geometry digest or output assembly from the device stream, or
2. implement a fused exact overlay continuation that avoids materializing that row stream but still emits a digest/output comparable with author code and the V2.14 exact-suite route.

Only after that end-to-end artifact exists should Goal4806 be considered complete.
