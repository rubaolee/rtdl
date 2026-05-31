# Goal2808 v2.5 Current-Head Canonical Harness Rerun

Date: 2026-05-31

Verdict: accept-with-boundary.

Goal2808 reran the seven current v2.5 canonical app harnesses on the RTX A5000 pod from a clean `origin/main` checkout and recorded the JSON artifacts under `docs/reports/goal2808_current_head_canonical_harness_pod/`.

This is internal readiness evidence only. It does not authorize a release, public speedup wording, paper reproduction wording, broad RT-core speedup wording, whole-app speedup wording, or true-zero-copy wording.

## Run Environment

| Field | Value |
| --- | --- |
| Source commit | `eba4de3cd0fc513e01410b4dd2bece7f55c1ac57` |
| Source dirty state | `[]` in all seven JSON artifacts |
| GPU | `NVIDIA RTX A5000, 570.211.01` |
| Pod repo | `/root/rtdl_goal2785_work` |
| OptiX library | `/root/rtdl_goal2785_work/build/librtdl_optix.so` |
| Python path | `PYTHONPATH=src:.` |
| Partner packages observed | NumPy 2.1.2, CuPy 14.1.0, Torch 2.8.0+cu128, Triton 3.4.0 |

## Harness Results

| Harness | App | Status | Key Result |
| --- | --- | --- | --- |
| Goal2797 | triangle counting | pass | 6 OptiX rows passed across 16, 1024, and 5000 disjoint triangles; both `rt_graph_2a1_generic_rt` and `rt_graph_1a2_generic_rt` match oracle counts. |
| Goal2798 | LibRTS spatial index | pass | Prepared AABB query medians: point contains 0.838 ms, range contains 0.859 ms, range intersects 1.530 ms. |
| Goal2799 | Spatial RayJoin | pass | Prepared OptiX count/parity route passed PIP, LSI, and overlay-seed workloads; prepared query medians were 0.132 ms, 0.139 ms, and 0.008 ms. |
| Goal2800 | RTNN | pass | Exact fixed-radius ranked-summary contract matched CuPy grid for uniform, clustered, and shell distributions; CuPy grid remained faster at 0.107x, 0.387x, and 0.183x of RTDL elapsed time. |
| Goal2801 | Hausdorff/X-HD | pass | Exact RTDL/OptiX path matched the CuPy grouped-grid exact baseline with zero distance error, but RTDL elapsed was 151.635x the CuPy grid elapsed on this 4096x4096 scenario. |
| Goal2802 | RT-DBSCAN | pass | Grouped stream continuation avoided neighbor-row/full-adjacency materialization and was 3.936x to 4.887x faster than prepared CuPy grid tail at 32k, 65k, and 131k points. |
| Goal2803 | Barnes-Hut | pass | OptiX membership wrapper was 8.881x to 160.970x faster than Embree membership wrapper; end-to-end OptiX total reached 5.025x vs Embree on the 8192-body case. |

## Schema Hardening

The first pass surfaced a provenance gap: Goal2797, Goal2798, and Goal2799 artifacts did not record `source_commit`, `source_dirty`, or `gpu`, while Goal2800-Goal2803 already did. Goal2808 fixed those three harness scripts and reran all seven artifacts from the pushed clean commit. The final artifact set is therefore provenance-complete.

## Claim Boundary

Every artifact keeps its public claim flags false. In particular:

- No public speedup claim is authorized.
- No whole-app speedup claim is authorized.
- No paper reproduction claim is authorized.
- No broad RT-core speedup claim is authorized.
- No true-zero-copy claim is authorized.
- No native engine customization is used as an app feature.

## Development Signal

Strong areas:

- RT-DBSCAN now has the clearest v2.5 continuation win: grouped stream continuation gives multi-x tail speedup over prepared CuPy grid while avoiding huge neighbor streams.
- Barnes-Hut confirms the value of RT membership probes and frontier lowering on larger cases; OptiX membership wrapper acceleration is substantial and the total path improves at scale.
- Spatial RayJoin and LibRTS pass as bounded prepared-count/parity harnesses with clean provenance.

Weak or still-open areas:

- Hausdorff remains correct and RT-core-backed, but the current exact RTDL adaptive nearest-witness path is much slower than the optimized CuPy grouped-grid exact baseline for the tested synthetic case.
- RTNN remains correct against the exact CuPy grid contract, but the same-contract CuPy grid is still faster on the current synthetic distributions.
- Triangle counting passes but still carries promoted phase timing from the inherited v2.4 contract inside row payloads; this is bounded by the harness-level claim flags and should be kept out of public wording.

## Files

- `scripts/goal2797_triangle_counting_v25_canonical_harness.py`
- `scripts/goal2798_librts_v25_warm_median_harness.py`
- `scripts/goal2799_spatial_rayjoin_v25_prepared_count_harness.py`
- `docs/reports/goal2808_current_head_canonical_harness_pod/goal2797_triangle_counting.json`
- `docs/reports/goal2808_current_head_canonical_harness_pod/goal2798_librts.json`
- `docs/reports/goal2808_current_head_canonical_harness_pod/goal2799_spatial_rayjoin.json`
- `docs/reports/goal2808_current_head_canonical_harness_pod/goal2800_rtnn.json`
- `docs/reports/goal2808_current_head_canonical_harness_pod/goal2801_hausdorff_xhd.json`
- `docs/reports/goal2808_current_head_canonical_harness_pod/goal2802_rt_dbscan.json`
- `docs/reports/goal2808_current_head_canonical_harness_pod/goal2803_barnes_hut.json`
- `tests/goal2808_v2_5_current_head_canonical_harness_rerun_test.py`

## Validation

Local focused validation after the provenance patch:

```text
py -3 -m py_compile scripts/goal2797_triangle_counting_v25_canonical_harness.py scripts/goal2798_librts_v25_warm_median_harness.py scripts/goal2799_spatial_rayjoin_v25_prepared_count_harness.py
py -3 -m unittest tests.goal2797_triangle_counting_v25_canonical_harness_test tests.goal2798_librts_v25_warm_median_harness_test tests.goal2799_spatial_rayjoin_v25_prepared_count_harness_test
Ran 13 tests in 0.221s
OK
```

Pod validation:

```text
Clean checkout at eba4de3cd0fc513e01410b4dd2bece7f55c1ac57.
Goal2797: pass
Goal2798: pass
Goal2799: pass
Goal2800: pass
Goal2801: pass
Goal2802: pass
Goal2803: pass
```
