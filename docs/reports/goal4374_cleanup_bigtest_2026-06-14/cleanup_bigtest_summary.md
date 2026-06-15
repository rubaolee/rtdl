# Goal4374 Cleanup Big Test Summary

Date: 2026-06-14

## Cleanup Completed

- Public Python API now exposes app-agnostic directed-segment point-location names for OptiX and Embree.
- Native OptiX and Embree ABI now export `directed_segment_point_location` symbols.
- Legacy `rayjoin_cdb_point_location` symbols remain as compatibility fallbacks.
- Python ctypes registration for the new and legacy symbols was deduplicated into shared registration loops.
- Standalone RayJoin LSI in `scripts/rayjoin_paper_reproduction_suite.py` now uses the same RayJoin LSI row route as overlay, then reports row count. This fixed the earlier standalone LSI count mismatch and removed the old slow Embree scalar count path.
- The RTDL RayJoin runner now enables a packed-array partner cache by default. The tested cache path was `/workspace/rayjoin_same_source_data/results/partner_cache_20260614`, with a 1.7 GB cache footprint for the two County x Zipcode CDB files.
- Overlay no-output mode now uses count-only directed-segment point-location for vertex and midpoint PIP, avoiding multi-million-row PIP materialization when no output chains are requested.
- Overlay midpoint generation for no-output mode now uses NumPy projection from structured LSI rows instead of Python `RayjoinOverlayIntersection` objects and Python sorting.
- OptiX overlay LSI pair dump now uses binary `uint64` pair output instead of TSV text dump plus `np.loadtxt`.
- Overlay benchmarking now records point-location prepare/build-index time separately, and the runner supports native warmup/repeat median output for overlay.
- RayJoin Embree LSI now defaults its internal AABB scenes to Embree low-build quality, while preserving explicit user `RTDL_EMBREE_AABB_SCENE_BUILD_QUALITY` overrides. This is scoped to the RayJoin LSI overlay path.

## Dataset

Dataset root: `/workspace/rayjoin_same_source_data/cdb_partial_topology`

| File | Bytes | Chains | Segments | Points | Nonzero Faces |
|---|---:|---:|---:|---:|---:|
| `dtl_cnty_Point.cdb` | 904,529,353 | 8,662,896 | 8,662,896 | 17,325,792 | 3,144 |
| `USAZIPCodeArea_Point.cdb` | 185,388,484 | 9,503 | 5,279,181 | 5,288,684 | 4,500 |

Availability: 3 / 24 exact-suite cases ready on this staged dataset: LSI, PIP, and Overlay for County x Zipcode.

## Big Test Matrix

| Program | Backend | Run Size | Count / Key Output | Stable | Hot Median Sec | Native Median Sec |
|---|---|---:|---:|---|---:|---:|
| LSI | RTDL OptiX | warmup 1, repeat 3 | 181,629 intersections | true | 2.520978 | 0.002023 |
| LSI | RTDL Embree | warmup 1, repeat 3 | 181,629 intersections | true | 5.892485 | n/a |
| PIP | RTDL Embree | warmup 5, repeat 60 | 3,823,783 positive faces | true | 0.303879 | 0.303813 |
| PIP | RTDL OptiX host-points | warmup 5, repeat 60 | 3,823,783 positive faces | true | 0.277429 | 0.118839 |
| PIP | RTDL OptiX device-resident count | warmup 5, repeat 60 | 3,823,783 positive faces | true | 0.118584 | 0.118549 |
| PIP | RTDL OptiX device-resident segment ids | warmup 5, repeat 60 | 5,288,684 point ids written | true | 0.118565 | 0.118543 |
| Overlay | RTDL OptiX | warmup 0, repeat 1 | 181,629 LSI intersections | n/a | 59.169130 total | n/a |
| Overlay | RTDL Embree | warmup 0, repeat 1 | 181,629 LSI intersections | n/a | 65.648922 total | n/a |
| Overlay P0 Final | RTDL OptiX | warmup 1, repeat 3 | 181,629 LSI intersections | true | 5.804978 total median | n/a |
| Overlay P0 Final | RTDL Embree | warmup 1, repeat 3 | 181,629 LSI intersections | true | 9.900761 total median | n/a |

## Partner Cache Overlay Rerun

The original overlay totals included repeated CDB text parsing and pack construction. With the packed-array partner cache warmed, the same overlay run changed as follows:

| Backend | Original Total Sec | Original Load/Pack Sec | Warm-Cache Total Sec | Warm-Cache Load/Pack Sec | Warm-Cache Compute Without Load/Pack Sec |
|---|---:|---:|---:|---:|---:|
| RTDL OptiX | 59.169130 | 47.806122 | 15.975173 | 0.420241 | 15.554932 |
| RTDL Embree | 65.648922 | 47.531593 | 18.225433 | 0.044618 | 18.180815 |

This removes the avoidable repeated Python CDB parse/pack cost from the steady-state comparison. It does not make RTDL faster than the RayJoin author implementation; it makes the remaining gap honest.

## Overlay P0 Final

After the P0 overlay fixes, the steady-state overlay path is no longer dominated by Python CDB parse/pack or PIP row materialization. The final measured packet is `p0_final_overlay_county_zipcode_all_w1r3_default_low_20260614.json`, produced by the script's native `warmup=1, repeat=3` overlay repeat support. For Embree, the default-low packet uses the new RayJoin LSI internal AABB low-build-quality default; no app-side user code or C++/CUDA is required.

| Backend | Total Median Sec | Load/Pack Median Sec | Compute Without Load/Pack Sec | LSI Hot Median Sec | Point-Location Prepare Wall Sec | PIP Hot Sum Median Sec | Midpoint Projection Sec |
|---|---:|---:|---:|---:|---:|---:|---:|
| RTDL OptiX | 5.804978 | 0.050966 | 5.754012 | 2.438230 | 1.325645 | 1.420532 | 0.099911 |
| RTDL Embree | 9.900761 | 0.040058 | 9.860703 | 4.977931 | 3.310194 | 1.147167 | 0.066300 |

Optimization progression from the warm-cache baseline:

| Backend | Warm-Cache Baseline Total Sec | P0 Final Total Median Sec | Improvement |
|---|---:|---:|---:|
| RTDL OptiX | 15.975173 | 5.804978 | 2.75x |
| RTDL Embree | 18.225433 | 9.900761 | 1.84x |

Both OptiX and Embree are now in the 1-10 second human-visible range for this overlay case. Embree's remaining cost is still primarily LSI scene/index work and point-location prepare/build-index time, not avoidable Python row output.

Overlay extra checks:

| Backend | Map0 Vertex Positive Faces | Map1 Vertex Positive Faces | Map0 Midpoint Positive Faces | Map1 Midpoint Positive Faces |
|---|---:|---:|---:|---:|
| RTDL OptiX | 7,034,556 | 3,823,783 | 27,465 | 14,355 |
| RTDL Embree | 7,037,306 | 3,823,783 | 27,594 | 14,579 |

## Result Files

- `cleanup_bigtest_availability_topology_20260614.json`
- `cleanup_bigtest_scan_county_zipcode_20260614.json`
- `cleanup_bigtest_lsi_county_zipcode_all_fixedroute_w1r3_20260614.json`
- `cleanup_bigtest_pip_county_zipcode_all_w5r60_20260614.json`
- `cleanup_bigtest_overlay_county_zipcode_all_w0r1_20260614.json`
- `partner_cache_fill_pip_optix_w0r1_20260614.json`
- `partner_cache_overlay_county_zipcode_all_warm_w0r1_20260614.json`
- `p0_binary_lsi_numpy_overlay_county_zipcode_all_warm_w0r1_20260614.json`
- `p0_backend_aware_prepare_overlay_county_zipcode_all_warm_w0r1_20260614.json`
- `p0_final_overlay_county_zipcode_all_w1r3_native_repeat_20260614.json`
- `p0_embree_aabb_quality_low_overlay_county_zipcode_w1r3_20260614.json`
- `p0_final_overlay_county_zipcode_all_w1r3_default_low_20260614.json`
- `author_vs_rtdl_partner_cache_summary_20260614.json`
- `author_vs_rtdl_partner_cache_summary_20260614.md`
- `author_vs_rtdl_p0_final_summary_20260614.json`
- `author_vs_rtdl_p0_final_summary_20260614.md`
- `author_vs_rtdl_p0_final_default_low_summary_20260614.json`
- `author_vs_rtdl_p0_final_default_low_summary_20260614.md`

## Interpretation

The cleanup is not cosmetic only. The big test found that standalone LSI and overlay LSI were not using the same route. After fixing standalone LSI to use the overlay RayJoin LSI row path, OptiX and Embree both report 181,629 intersections and the Embree LSI run drops from the previous 436.9 s scalar route to 5.89 s median on the repeated fixed-route run.

PIP remains count-consistent across Embree, OptiX host-points, and OptiX device-resident paths. The fastest PIP route is the device-resident OptiX path at 0.1186 s median for 5.29M query points.

The partner-cache rerun confirmed the correct RTDL principle: avoidable ingestion and packing overhead should be removed before making performance claims. The P0 final run then removed the largest remaining no-output materialization debts. RTDL OptiX overlay is now 5.80 s median on the staged County x Zipcode overlay case, faster than the author RT overlay process wall time measured earlier at 7.15 s. RTDL Embree overlay is now 9.90 s median, putting the CPU path into the requested 1-10 second range. This is not a claim that generic RTDL beats hand-written RayJoin in every timing view; it is a claim that this app-level no-output overlay path is now competitive after removing avoidable RTDL overhead.

The Embree result is also much improved, from 18.23 s warm-cache baseline to 9.90 s final median. Its remaining gap is explainable: Embree LSI spends about 4.98 s hot time while its measured `rtcCollide` traversal is about 0.82 s, meaning scene/index construction and row production dominate; point-location prepare contributes another 3.31 s wall time even after parallel preparation. That is the next native CPU optimization debt, not an unexplained RTDL/Python overhead.
