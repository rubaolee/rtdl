# Goal3567 Composite v2.9 Packet After RayDB Sum Fast Path

schema: `rtdl.goal3567.v2_9_composite_packet_after_raydb_sum_fastpath.v1`

| Metric | Value |
| --- | ---: |
| row count | 11 |
| reused Goal3558 rows | 9 |
| Goal3565 replacement rows | 2 |
| geomean speedup | 1.069163x |
| median speedup | 1.009085x |
| min speedup | 0.987619x |
| max speedup | 1.585627x |

| Case | v2.3 sec | v2.9 sec | v2.9 speedup | Evidence source |
| --- | ---: | ---: | ---: | --- |
| `robot_collision_optix_prepared_device_buffers` | 0.001890558 | 0.001914259 | 0.987619x | goal3558_full_10s_packet_unchanged_row |
| `spatial_rayjoin_optix_prepared_full_route` | 0.000179248 | 0.000181246 | 0.988978x | goal3558_full_10s_packet_unchanged_row |
| `librts_optix_aabb_index` | 0.000752487 | 0.000758727 | 0.991776x | goal3558_full_10s_packet_unchanged_row |
| `barnes_hut_optix_node_coverage` | 0.008123981 | 0.008174485 | 0.993822x | goal3558_full_10s_packet_unchanged_row |
| `rt_dbscan_optix_grouped_stream` | 0.012592142 | 0.012627419 | 0.997206x | goal3558_full_10s_packet_unchanged_row |
| `raydb_optix_partner_resident_count` | 0.000588950 | 0.000583647 | 1.009085x | goal3565_targeted_raydb_fastpath_a5000 |
| `hausdorff_optix_threshold` | 0.031770580 | 0.031161210 | 1.019555x | goal3558_full_10s_packet_unchanged_row |
| `triangle_counting_optix_rt_graph_2a1_partner` | 0.000362574 | 0.000352157 | 1.029580x | goal3558_full_10s_packet_unchanged_row |
| `rtnn_optix_prepared_3d_ranked_summary` | 0.001532887 | 0.001444450 | 1.061225x | goal3558_full_10s_packet_unchanged_row |
| `contact_manifold_optix_aabb_broadphase_collect_k` | 0.028139902 | 0.023074425 | 1.219528x | goal3558_full_10s_packet_unchanged_row |
| `raydb_optix_partner_resident_sum` | 0.000751490 | 0.000473938 | 1.585627x | goal3565_targeted_raydb_fastpath_a5000 |
