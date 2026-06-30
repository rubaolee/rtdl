# Goal2066 v2 Pod Large-Scale Follow-Up

Date: 2026-05-15

Status: `accept-with-boundary`

## Purpose

Goal2066 uses the active NVIDIA L4 pod for a larger v2.0 evidence pass after Goal2064. The goal is not to authorize v2.0 release. The goal is to learn which rows become strong when scaled, which rows remain bounded by output shape, and which rows still need a better reusable partner primitive.

Pod context:

- Host: `66.92.198.234`
- SSH port: `11830`
- GPU: NVIDIA L4
- Driver: `570.195.03`
- CUDA: `/usr/local/cuda-12`
- OptiX SDK: `/root/vendor/optix-sdk`, tag `v8.0.0`
- Python environment: `/root/rtdl_goal2046_venv`
- OptiX library: `/root/rtdl_goal2048_9b95e5f2/build/librtdl_optix.so`

## Artifacts

- `docs/reports/goal2066_robot_collision_cupy_l4_32768x8192.json`
- `docs/reports/goal2066_robot_collision_cupy_l4_65536x8192.json`
- `docs/reports/goal2066_segment_polygon_hitcount_cupy_l4_131072_capacity67108864.json`
- `docs/reports/goal2066_fixed_radius_family_cupy_l4_16384.json`
- `docs/reports/goal2066_road_hazard_cupy_l4_12288_prepared_only.json`
- `docs/reports/goal2066_segment_polygon_anyhit_cupy_l4_4096_capacity16777216.json`
- `docs/reports/goal2066_polygon_rawkernel_cupy_optix_l4_2048.json`
- `docs/reports/goal2066_polygon_rawkernel_cupy_optix_l4_3072.json`
- `docs/reports/goal2066_polygon_rawkernel_cupy_optix_l4_4096_oom.log`

## Positive Scaling Rows

| Row | Scale | v1.8 reference median | v2 median | v2/v1.8 ratio | Meaning |
| --- | ---: | ---: | ---: | ---: | --- |
| robot_collision_screening | 32768 poses x 8192 obstacles | 0.003117s | 0.000510s | 0.164x | v2 turns the prior small-scale negative row into a speedup once pose flags amortize adapter cost |
| robot_collision_screening | 65536 poses x 8192 obstacles | 0.006289s | 0.000528s | 0.084x | larger scale improves the same prepared zero-copy path to about 11.9x faster |
| segment_polygon_hitcount | 131072 rows, capacity 67108864 | 0.452884s | 0.002772s | 0.006x | compact count columns are the strongest segment/polygon v2 shape |
| road_hazard_priority_flags | 12288 roads, 18432 hazards | 0.029205s | 0.002496s | 0.085x | prepared reusable witness outputs convert the earlier small negative into a large positive |

The common pattern is clear: v2.0 wins when the native engine emits generic compact signals and the partner owns the continuation columns. Prepared scene reuse and reusable output buffers matter as much as the RT query itself.

## Fixed-Radius Family at 16384 x 16384

Artifact: `docs/reports/goal2066_fixed_radius_family_cupy_l4_16384.json`

| App row | v2/v1.8 prepared ratio |
| --- | ---: |
| facility_knn_assignment threshold proxy | 0.008x |
| hausdorff_distance forward threshold proxy | 0.007x |
| hausdorff_distance reverse threshold proxy | 0.009x |
| ann_candidate_search threshold proxy | 0.007x |
| outlier_detection | 0.008x |
| dbscan_clustering core-count proxy | 0.008x |
| barnes_hut_force_app coverage proxy | 0.009x |

This strengthens the Goal2060 conclusion: the reusable fixed-radius count/threshold contract is performance-positive at larger L4 scale. It still does not prove richer app semantics such as exact KNN ranking, exact Hausdorff witness extraction, full DBSCAN cluster expansion, or Barnes-Hut force-vector accumulation.

## Remaining Negative or Mixed Rows

### Full Segment/Polygon Any-Hit Rows

Artifact: `docs/reports/goal2066_segment_polygon_anyhit_cupy_l4_4096_capacity16777216.json`

At `count=4096`, full witness-row materialization passes parity but is slower:

- v1.8 native OptiX row median: `0.105058s`
- v2 partner-column row median: `0.164098s`
- ratio: `1.562x`

This is not a correctness problem. It is an output-shape problem. Materializing full generic witness rows is a weaker v2 story than writing compact app-needed counts or flags into partner columns.

### Polygon RawKernel Control Apps

Artifacts:

- `docs/reports/goal2066_polygon_rawkernel_cupy_optix_l4_2048.json`
- `docs/reports/goal2066_polygon_rawkernel_cupy_optix_l4_3072.json`
- `docs/reports/goal2066_polygon_rawkernel_cupy_optix_l4_4096_oom.log`

| App | Scale | v2/v1.8 ratio | Result |
| --- | ---: | ---: | --- |
| polygon_pair_overlap_area_rows | 2048 | 1.261x | slower |
| polygon_set_jaccard | 2048 | 0.910x | slightly faster |
| polygon_pair_overlap_area_rows | 3072 | 1.301x | slower |
| polygon_set_jaccard | 3072 | 0.956x | near parity/slightly faster |
| polygon_pair_overlap_area_rows / polygon_set_jaccard | 4096 | n/a | OptiX candidate discovery hit CUDA out-of-memory before timing |

This is the sharpest remaining design lesson. The current control-app polygon continuation is useful as evidence that Python+CuPy RawKernel+RTDL can preserve semantics, but it is not yet a clean v2.0 performance primitive. The next reusable design should be a bounded or streaming candidate-summary contract that lets polygon overlap/Jaccard accumulate summaries without allocating or discovering an explosive candidate-pair surface.

## Design Conclusions

Solved by current v2.0 contracts:

- prepared generic native queries can hand device data to CuPy;
- compact count, flag, and threshold outputs can remain GPU-resident;
- large rows can outperform v1.8 prepared paths once dispatch and adapter cost are amortized;
- robot collision and road hazard are no longer merely zero-copy parity rows at larger scale.

Still not solved:

- full witness-row materialization is still slower than a specialized v1.8 native row;
- polygon-pair overlap needs a reusable bounded/streaming candidate-summary primitive;
- the fixed-radius family is excellent for threshold proxies, but richer exact continuations remain future work;
- the 4096 polygon control OOM is a real scaling blocker, not a timing anomaly.

## Release Boundary

Allowed:

- cite Goal2066 as large-scale NVIDIA L4 evidence that several v2 rows are now strongly positive;
- cite robot and road hazard as examples where larger scale flips the earlier small negative rows into speedups;
- cite compact partner-owned outputs as the key performance design principle.

Not allowed:

- claim all v2.0 apps are faster than v1.8;
- claim full witness-row materialization is solved;
- claim polygon overlap/Jaccard has a complete scalable v2 primitive;
- claim v2.0 release readiness without final release review and consensus.

Verdict: `accept-with-boundary`.
