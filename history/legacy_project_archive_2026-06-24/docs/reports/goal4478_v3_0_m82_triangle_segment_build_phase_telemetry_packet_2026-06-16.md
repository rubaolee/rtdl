# Goal4478 / V3.0 M82: Triangle Segment-Ray Build Phase Telemetry

## Verdict

M82 is instrumentation, not a speedup claim. It adds opt-in `--segment-ray-build-telemetry sync_subphases` for the current Triangle Counting route so we can stop treating `segment_ray_build_median_ms` as a black box.

The result is decisive: the next optimization target is `cupy_unique_counts`, not prepared ray batches, not scalar weight telemetry, and not RT traversal.

## Route Profiled

Current M78 best route:

- `unique_weighted`
- `numba_direct`
- `prepared_segment_replay`
- full 3-D ray columns
- `sync_subphases` telemetry enabled

The sync telemetry is profiling-only; it adds CUDA stream synchronization between subphases and is not promoted performance timing.

## Phase Matrix

| Dataset | Count | Segment build | Top phase | Top phase share | Numba key fill | Ray projection | Unique decode |
|---|---:|---:|---:|---:|---:|---:|---:|
| com-lj | 177,820,130 | 1.670s | `cupy_unique_counts` 0.694s | 41.6% | 0.391s | 0.182s | 0.126s |
| soc-LiveJournal1 | 285,730,264 | 2.215s | `cupy_unique_counts` 1.035s | 46.8% | 0.478s | 0.259s | 0.179s |
| com-orkut | 627,584,181 | 11.838s | `cupy_unique_counts` 6.306s | 53.3% | 2.185s | 1.640s | 1.136s |

## Full Phase Order

| Dataset | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| com-lj | `cupy_unique_counts` 694ms | `numba_key_fill` 391ms | `numba_kernel_lookup` 231ms | `ray_column_projection_full` 182ms |
| soc-LiveJournal1 | `cupy_unique_counts` 1035ms | `numba_key_fill` 478ms | `ray_column_projection_full` 259ms | `numba_kernel_lookup` 190ms |
| com-orkut | `cupy_unique_counts` 6306ms | `numba_key_fill` 2185ms | `ray_column_projection_full` 1640ms | `unique_decode_weights` 1136ms |

Small phases are not the next target: filtering, edge slicing, offset allocation, and duplicate ray-count sum are each tiny compared with unique/count.

## Interpretation

The scaling story is clean. `cupy_unique_counts` grows from 41.6% to 53.3% of segment-ray construction as the dataset grows. This is the phase that turns duplicate two-hop keys into unique weighted rays. It is currently a general-purpose CuPy unique/count over a huge key stream.

M83 should attack that exact boundary:

- avoid feeding so many duplicate keys into `cp.unique(return_counts)`;
- replace generic `cp.unique` with a route better matched to sorted/grouped graph structure;
- or change segmentation/partner lowering so unique/count is local, fused, or avoided before ray-column projection.

Do not spend the next optimization cycle on ray-batch ABI, scalar weight-sum telemetry, counts/filter, or RT traversal.

## Artifacts

- `goal4478_v3_0_m82_triangle_segment_build_telemetry_com_lj_w1r1_2026-06-16.json`
- `goal4478_v3_0_m82_triangle_segment_build_telemetry_soc_livejournal1_w1r1_2026-06-16.json`
- `goal4478_v3_0_m82_triangle_segment_build_telemetry_com_orkut_w1r1_2026-06-16.json`
- `goal4478_v3_0_m82_triangle_segment_build_phase_telemetry_packet_2026-06-16.json`
