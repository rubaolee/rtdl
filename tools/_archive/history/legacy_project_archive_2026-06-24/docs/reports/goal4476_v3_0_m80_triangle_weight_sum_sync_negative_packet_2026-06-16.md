# Goal4476 V3.0 M80 Triangle Weight-Sum Sync Negative Packet

Goal4476 tests a narrow post-M79 optimization idea: replace per-segment
`_sum_uint64_like(ray_weights)` telemetry with the segment planner's known
logical two-hop row count. Two variants were measured:

- no-sync: remove the device reduction/sync entirely;
- explicit-sync: remove the device reduction but synchronize the CuPy default
  stream before native prepared-ray-batch handoff.

Both implementation commits were reverted. This is a negative-result packet,
not a promoted optimization.

## Result

| Dataset | M78 total | M80 no-sync total | M80 explicit-sync total | M78 query | M80 best query |
| --- | ---: | ---: | ---: | ---: | ---: |
| `com-lj` | 5.404s | 9.596s | 10.102s | 0.180s | 0.181s |
| `soc-LiveJournal1` | 11.669s | 13.761s | 14.241s | 0.264s | 0.263s |
| `com-orkut` | 35.379s | 37.007s | 38.235s | 1.732s | 1.729s |

The query medians are effectively unchanged, while total/backend timing does
not improve. `com-orkut` is close on backend timing, but still not a win; the
smaller rows are clearly worse.

## Interpretation

Do not promote this route. The old `_sum_uint64_like(ray_weights)` call was not
the main scalar-summary bottleneck. It also acted as a CUDA synchronization
point before native prepared-ray-batch handoff. Removing it shifts or exposes
pending CUDA work rather than reducing the true route cost.

The current best internal Triangle Counting route remains Goal4474/Goal4475
M78: `numba_direct` plus prepared ray batch.

## Next Target

Stop treating scalar weight-sum telemetry/copy-back as the main debt. The next
serious optimization target should be partner materialization, segment-ray
construction, or prepared-ray-batch build, and only if the change preserves the
generic RTDL primitive contract.

## Evidence

- `docs/reports/goal4476_v3_0_m80_triangle_weight_sum_sync_negative_packet_2026-06-16.json`
- `docs/reports/goal4476_v3_0_m80_triangle_no_weight_sum_sync_com_lj_w1r3_2026-06-16.json`
- `docs/reports/goal4476_v3_0_m80_triangle_no_weight_sum_sync_com_lj_w1r3_rerun_2026-06-16.json`
- `docs/reports/goal4476_v3_0_m80_triangle_no_weight_sum_sync_soc_livejournal1_w1r3_2026-06-16.json`
- `docs/reports/goal4476_v3_0_m80_triangle_no_weight_sum_sync_soc_livejournal1_w1r3_rerun_2026-06-16.json`
- `docs/reports/goal4476_v3_0_m80_triangle_no_weight_sum_sync_com_orkut_w1r3_2026-06-16.json`
- `docs/reports/goal4476_v3_0_m80_triangle_no_weight_sum_sync_com_orkut_w1r3_rerun_2026-06-16.json`
- `docs/reports/goal4476_v3_0_m80_triangle_no_weight_sum_reduction_sync_com_lj_w1r3_2026-06-16.json`
- `docs/reports/goal4476_v3_0_m80_triangle_no_weight_sum_reduction_sync_soc_livejournal1_w1r3_2026-06-16.json`
- `docs/reports/goal4476_v3_0_m80_triangle_no_weight_sum_reduction_sync_com_orkut_w1r3_2026-06-16.json`
