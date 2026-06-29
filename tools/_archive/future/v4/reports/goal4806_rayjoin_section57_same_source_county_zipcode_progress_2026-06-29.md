# Goal4806 RayJoin Section 5.7 County x Zipcode Progress

Date: 2026-06-29

## Status

Goal4806 is not complete yet.

The serious POD line is now past the earlier setup blockers: RayJoin author code builds, a same-source regenerated County x Zipcode CDB is available, RTDL OptiX runs on the same data, and V4+Numba has been tested far enough to expose the real remaining primitive/toolchain blockers.

## Evidence Location

Evidence directory:

`tools/_archive/future/v4/evidence/goal4806_rayjoin_section57_same_source_county_zipcode_2026-06-29/`

Included evidence:

- `section57_same_source_cdb_tree.json`
- `section57_same_source_county_zipcode_preflight.json`
- `section57_overlay_county_zipcode_author_rt_iter0.json`
- `section57_overlay_county_zipcode_rtdl_optix_retry_fixed.json`
- `section57_v4_numba_candidate_measurements.json`
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
- The drop counts are recorded in the result JSON:
  - `map0_nonfinite_midpoints_dropped`
  - `map1_nonfinite_midpoints_dropped`

Validation:

- Local focused tests passed: `28 tests OK`.
- POD focused gate passed: `6 tests OK`.
- Full POD RTDL OptiX retry then completed.

## Result: V4 + Numba

V4+Numba is not release-ready for RayJoin Section 5.7 polygon overlay yet.

### Candidate Pair-Column Probe

File: `section57_v4_numba_candidate_measurements.json`

Status: `no_rows_measured`

Blocker:

`cannot wrap an overflowed device pair-column stream; capacity=1152144 required_capacity=10142618; overflow_policy=fail_closed`

Interpretation:

The candidate stream is much larger than the exact count. Retrying with a bigger capacity would measure candidate rows, not exact Section 5.7 overlay rows. Treating candidate rows as exact would be wrong.

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

This stack successfully ran a minimal Numba CUDA kernel on the POD. V4+Numba tests on driver 550 should use this compatible stack or a newer driver that accepts PTX 8.7.

## Current Engineering Problems

1. Exact RayJoin paper preprocessed CDB inputs are not available from the public Dryad share.
2. Same-source regenerated CDB is serious and useful, but it is not the exact paper input.
3. RTDL OptiX compute runs and is much faster than the author run on this same-source input, but the author timing is dominated by CDB read time and RTDL used a packed cache path.
4. RTDL full-overlay output equality against author output has not yet been established for this same-source run.
5. V4+Numba lacks a valid exact segment-pair device-column primitive for Section 5.7 overlay rows.
6. Existing segment-pair count surfaces disagree across contracts on this same-source run:
   - RTDL overlay emitted rows: `965844`
   - scalar exact count probe: `1152144`
   - grouped-count device-column source rows: `382946`
7. Because of that contract mismatch, the automatic V4+Numba primitive selector must stay fail-closed for this workload.

## Non-Stupid Next Step

Do not publish a V4+Numba RayJoin Section 5.7 success claim from the current evidence.

The correct next engineering step is to implement or expose one exact segment-pair device-column primitive that uses the same RayJoin LSI predicate contract as the overlay route and returns the actual exact `(left_id, right_id, x, y)` row stream, or a fused exact overlay continuation that avoids materializing that row stream.

Only after that primitive exists should V4+Numba auto-selection be rerun for Section 5.7.

