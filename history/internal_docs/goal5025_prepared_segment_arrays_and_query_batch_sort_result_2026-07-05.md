# Goal5025 - Prepared Segment Arrays and Query-Batch Sort Probe

## Purpose

Continue the v2.14.3 query-many attack after Goal5024. Goal5024 removed the repeated right-vertex query-point preparation from `vertex_pip_map1_in_map0`. The next visible later-batch floor was:

- `intersection_reprojection_device_columnar_sec` around `0.16-0.17s` per batch.
- `sort_map1_device_columnar_sec` around `0.11-0.12s` per batch.

Goal5025 attacks those without changing RTDL core and without moving the regime.

## Boundary

- App route: `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`.
- No `src/rtdsl/**` or `src/native/**` changes.
- Regime: same-process prepared LSI base-session, distinct chain-contiguous full overlay batches.
- Not a cold CLI one-shot result.
- Not paper text output.
- Not author parity.
- Not a 10x claim.

## Implemented Change 1: Prepared Query-Batch Segment Arrays

Added:

```text
--prepared-query-batch-segment-arrays
```

With `--prepared-lsi-base-session --query-chain-batches N`, it:

- prepares the unchanged right-side segment arrays once;
- prepares each left-batch segment array once in the session;
- injects those device arrays into `numeric_xsect_columns_from_pair_device_columns_numba_device`.

This removes repeated host-to-device segment-array uploads from the per-batch reprojection phase.

## Implemented Change 2: Numba Warmup Signature Fix

The existing `_warm_numba()` did not warm the real carrier-builder signature because it passed `point_faces` and `midpoint_faces` as `int64`, while the real route passes `uint32`.

Fix:

```text
_warm_numba() now warms _build_projected_descriptor_side_numba with uint32 face arrays.
```

This removes a misleading first-batch carrier JIT cost from the measured query-batch body.

## Existing Probe Reused: Native Lexsort

The existing `--native-lexsort` opt-in was measured on the new query-batch route. It is still a generic sort probe, not a RayJoin core primitive.

## Validation

Local:

```text
py -3 -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
py -3 -m unittest tests.goal5021_prepared_lsi_base_session_test
Ran 8 tests - OK
```

POD: top4 County x Zipcode, six distinct chain-contiguous full overlay batches.

## Artifacts

- Baseline before Goal5024:
  - `history/internal_docs/rtdl_goal5024_query6_baseline_top4.json`
- Goal5024 right-vertex reuse:
  - `history/internal_docs/rtdl_goal5024_query6_prepared_right_points_top4.json`
- Goal5025 prepared segment arrays, first run:
  - `history/internal_docs/rtdl_goal5025_query6_prepared_right_points_and_segments_top4.json`
- Goal5025 prepared segment arrays, after Numba warm-signature fix:
  - `history/internal_docs/rtdl_goal5025_query6_prepared_right_points_segments_warmfix_top4.json`
- Goal5025 prepared segment arrays, rerun after Numba warm-signature fix/cache stabilization:
  - `history/internal_docs/rtdl_goal5025_query6_prepared_right_points_segments_bitonic_rerun_top4.json`
- Goal5025 prepared segment arrays plus native lexsort probe:
  - `history/internal_docs/rtdl_goal5025_query6_prepared_right_points_segments_native_lexsort_top4.json`

## Main Result

All rows below are six distinct full overlay query batches in the same prepared LSI base session.

| Route | Median Batch Body | Best Batch Body | Sum of 6 Batch Bodies | Later-Batch Sum | Query-Batch Extra Session Prep |
|---|---:|---:|---:|---:|---:|
| Baseline | 0.7576s | 0.7054s | 6.1415s | 3.7632s | 0 |
| + prepared right vertices | 0.4393s | 0.4323s | 4.1964s | 2.1896s | 1.0448s |
| + prepared segment arrays (bitonic rerun) | 0.2592s | 0.2308s | 3.1074s | 1.2647s | 1.2086s |
| + native lexsort probe | 0.2444s | 0.2150s | 3.0126s | 1.1875s | 1.2053s |

Net versus original 6-batch baseline, charging the added query-batch session prep:

```text
Original baseline body sum:      6.1415s
Native-lexsort route body sum:   3.0126s
Body saved:                      3.1289s
Added query-batch session prep:  1.2053s
Net saved after prep:            ~1.9236s
```

This is a real query-batch win, not same-query replay.

## Phase Movement

Reprojection:

```text
baseline per-batch reprojection: ~0.16-0.17s
prepared segment arrays:         ~0.0015-0.0034s
```

Prepared right vertices from Goal5024:

```text
baseline map1_in_map0 PIP: ~0.31-0.34s
prepared right vertices:   ~0.012-0.017s
```

Native lexsort probe:

```text
bitonic later sort_map1 median: ~0.1085s
native later sort_map1 median:  ~0.1006s
```

Native lexsort helps modestly. It is not the main win.

## Correctness Anchors

Descriptor pair counts remained stable across the six-batch comparisons:

```text
[6316, 2756, 4723, 3058, 2873, 2987]
```

LSI row-count sets remained consistent for the same six batches:

```text
[127926, 21424, 67840, 66414, 56228, 88490]
```

## Interpretation

What improved:

- Query-batch later-body median moved from `~0.758s` to `~0.244s`.
- Best later batch moved from `~0.705s` to `~0.215s`.
- The route now has the repeated right-vertex PIP preparation and repeated reprojection segment-array upload removed from the per-batch body.

What remains:

- First batch is still dominated by LSI workspace:
  - `lsi_bounded_exact_pair_id_device_columns_sec` around `1.6s`.
- Later batches are now dominated by:
  - `sort_map1_device_columnar_sec` around `0.10s`;
  - carrier construction around `0.06-0.07s`;
  - LSI around `0.04-0.05s`.

What this does not prove:

- No cold CLI one-shot speedup claim.
- No paper-text output speedup claim.
- No author parity.
- No 10x claim.
- No full device-resident pipeline claim.

## Exit Label

`completed_query_batch_segment_array_reuse_win__native_lexsort_modest_win`
