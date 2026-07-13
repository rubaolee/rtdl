# Goal4949 RayJoin Hot-Path Remeasure

## Erratum

This report is superseded for the Numba-writer phase details by:

- `history/internal_docs/goal4949_erratum_clean_head_rerun_2026-07-04.md`

The original POD directory used for the first report was not a git checkout and
still contained stale experimental writer code from an earlier path-split line.
The high-level conclusion remains unchanged: the current Numba/app-layer helper
is not a RayJoin performance win. However, the detailed writer subphase evidence
must be read from the clean-HEAD rerun in the erratum, not from the stale remote
tree's path-split fields.

Date: 2026-07-04

Status: completed_measurement__layer2_current_helper_not_promoted

## Purpose

Goal4949 was created after Goal4947 and Goal4948 proved that the generic Layer 1/2 device-column row-buffer machinery can connect native RTDL output columns to Numba continuations. The specific question here was different and stricter:

> Does the current Layer 1/2 / Numba path move a real RayJoin Section 5.7 hot-path phase, rather than only proving a connector on demo operators?

This goal intentionally used the RayJoin public County x Soil sample, not a synthetic toy.

## Inputs And Environment

- Machine: POD `root@157.157.221.29:24344`
- Working directory: `/root/rtdl_goal4937`
- Dataset: RayJoin public County x Soil sample
- Data files:
  - `br_county_clean_25_odyssey_final.txt`
  - `br_soil_ascii_odyssey_final.txt`
  - `br_countyXbr_soil_answer.txt`
- App scripts:
  - `Paper-reproduction-apps/rayjoin-paper/section57_overlay.py`
  - `Paper-reproduction-apps/rayjoin-paper/section57_overlay_numba.py`

Artifact:

- `history/internal_docs/goal4949_rayjoin_hot_path_remeasure_artifact_2026-07-04.json`

## Runs

Two forms were run:

1. Full public-sample script: Section 5.2, 5.3, 5.7 baseline, and 5.7 Numba variant.
2. Hot rerun: Section 5.7 baseline and Section 5.7 Numba variant only, reusing the already warm packed cache.

Both 5.7 routes produced byte-identical output to the author answer:

- SHA256: `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`
- baseline byte-equal: true
- Numba variant byte-equal: true

Correctness is therefore not the issue in this measurement.

## Main Numbers

### First Full Run

| Route | Elapsed | Writer |
|---|---:|---:|
| baseline `section57_overlay.py` | 6.784s | 2.063s |
| `section57_overlay_numba.py` | 8.601s | 4.521s |

### Hot Rerun

| Route | Elapsed | Writer | Reprojection | Sort Total | Vertex PIP | LSI Rows |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 6.305s | 2.615s | 0.726s | 0.815s | 0.020s | 1.186s |
| Numba variant | 8.034s | 4.237s | 0.752s | 0.795s | 0.020s | 1.128s |

## Interpretation

The current Numba variant is not a RayJoin hot-path performance win. It preserves byte-equality, but it is slower than the baseline on this public sample.

The reason is clear from the phase table:

- It does not materially reduce the real current numeric hot phases:
  - reprojection remains about `0.73-0.75s`
  - sort remains about `0.80s`
  - vertex PIP is already tiny at about `0.02s`
- It makes the writer path worse:
  - baseline writer: `2.06-2.62s`
  - Numba variant writer: `4.24-4.52s`

The Numba writer variant's detailed hot writer phases show why:

- `path_split_materialize_map0_sec`: 1.356s
- `path_split_materialize_map1_sec`: 1.039s
- `path_split_format_map0_sec`: 0.751s
- `path_split_format_map1_sec`: 0.610s
- `bulk_writelines_sec`: 4.163s

This path is doing additional Python-side materialization / formatting / buffered output work. It is not the Layer 1/2 win we were looking for.

## Conclusion

Goal4949 answers the question negatively:

> The existing app-layer Numba overlay helper should not be promoted as a RayJoin Section 5.7 optimization path.

It is useful as correctness-preserving instrumentation and as evidence about the writer decomposition, but it is not a performance improvement.

The useful technical signal is this:

1. PIP traversal is not the RayJoin hot bottleneck in the prepared public sample.
2. The real remaining baseline costs are:
   - writer / output-chain generation: about `2.1-2.6s`
   - reprojection + sorting: about `1.5s`
   - LSI row production: about `1.1-1.2s`
   - point-location preparation: about `0.78s`
3. The next Layer 2 attempt must target `intersection_reprojection_sec` and `sort_map*_sec` directly with a generic numeric continuation. It must not use `uint32_equal_mask`, `segmented_count_i64`, or the current overlay writer wrapper as proof of RayJoin progress.
4. The larger prize remains Layer 3 writer / output assembly. However, the current "generic output assembly" implementation is not yet a win; it is slower and must not be promoted.

## Authorized Claim

Authorized:

- current RTDL baseline and Numba variant both preserve public-sample byte equality
- current Numba app-layer helper is not a performance win on the public County x Soil sample
- RayJoin prepared-hot PIP traversal is not the bottleneck on this sample
- next useful Layer 2 work must target reprojection/sort directly
- Layer 3 remains the larger target, but current writer assembly path is not acceptable as an optimization

Not authorized:

- no broad RayJoin speedup claim
- no whole-app RTDL speedup claim
- no claim that Layer 1/2 has moved the RayJoin hot path yet
- no claim that current Numba writer assembly should be kept as an optimized path
- no full eight-pair Section 5.7 claim

## Exit Label

`completed_measurement__current_layer2_helper_not_performance_win__next_target_reprojection_sort_or_layer3`
