# Goal3548: v2.9 A5000 Same-Contract Repeat Evidence

Status: internal evidence, accept-with-boundary.

This goal reruns the v2.8/current versus v2.3 same-contract OptiX benchmark packet on an NVIDIA RTX A5000 after Goal3542 and Goal3547 added repeat/resident hooks to the five formerly partial rows. It is a v2.9 performance-lane measurement step, not a release authorization.

## Purpose

Goal3536 showed that the prior all-app table had five partial rows because the v2.3 side did not expose the same repeat hooks as current. Goal3547 added a v2.3 measurement overlay. Goal3548 uses that overlay on pod hardware and asks a narrower question:

Can every comparison row be measured with a long hot-query repeat protocol, and what does the same-contract v2.8/current versus v2.3 table look like once the measurement rows are no longer partial?

## Pod And Inputs

- Pod: `69.30.85.203:22057`
- GPU: `NVIDIA RTX A5000, driver 580.126.09, 24564 MiB`
- Current root on pod: `/root/rtdl_goal3548_current`
- v2.3 overlay root on pod: `/root/rtdl_goal3548_v23_overlay`
- v2.3 base commit: `2a28365d0246d51f3e3322b546f8a68c58632db4`
- v2.3 overlay patch: `docs/patches/goal3547_v23_measurement_overlay_repeat_hooks_2026-06-06.patch`
- Final full artifact: `docs/reports/goal3548_v2_9_repeat_hook_10s_rerun_a5000_compact_calibrated3/summary.json`
- RTNN supplement: `docs/reports/goal3548_v2_9_repeat_hook_10s_rerun_a5000_rtnn_supplement/summary.json`

## Measurement Harness Fix

The first calibrated run exposed a harness bug in `robot_collision`: the repeat loop stored full `flags` arrays and the whole `backend_result` object for every repeat. At 7,000+ repeats this drove the v2.3 subprocess to roughly 16 GB RSS and made the row untrustworthy as a steady-state measurement.

The v2.9 fix makes the robot repeat ledger scalar-only:

- keep `flagged_group_count`, `flags_signature`, `matches_probe_reference`, `prepared_run_index`, phase timings, and compact buffer metadata;
- drop per-repeat full `flags`;
- drop per-repeat full `backend_result`.

This is a measurement-memory fix. It does not change the RTDL native query, the OptiX prepared scene, or the primary timing calculation.

## Provenance Boundary

The final pod packet was generated after copying the compact robot ledger patch to the pod, before that patch had a new Git commit on the pod checkout. The artifact therefore reports the previous current commit in its row metadata. This report commits the exact compact-ledger source and the regenerated v2.3 overlay patch. Treat the packet as internal v2.9 evidence with this provenance boundary, not as a final release packet.

## Final Full Packet

The final full packet has `11` comparison rows and `target_met_by_plan_pair_count = 11`. It fixes the RayJoin repeat cap miss from the earlier calibrated pass by running with `--max-internal-repeat 100000`.

Summary:

- Median speedup: `1.000x`
- Geomean speedup: `1.001x`
- Minimum speedup: `0.955x` (`rt_dbscan`)
- Maximum speedup in full packet: `1.064x` (`rtnn`)

| App / row | v2.3 sec | v2.8/current sec | Speedup | v2.3 observed sec | v2.8 observed sec | Observed target |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `barnes_hut_optix_node_coverage` | 0.00808992 | 0.00829876 | 0.975x | 15.096 | 15.311 | pass/pass |
| `contact_manifold_optix_aabb_broadphase_collect_k` | 0.0275905 | 0.0276496 | 0.998x | 17.354 | 17.751 | pass/pass |
| `hausdorff_optix_threshold` | 0.0317885 | 0.0318784 | 0.997x | 15.195 | 14.441 | pass/pass |
| `librts_optix_aabb_index` | 0.000760280 | 0.000750563 | 1.013x | 15.039 | 15.017 | pass/pass |
| `raydb_optix_partner_resident_count` | 0.000591503 | 0.000590944 | 1.001x | 16.283 | 14.995 | pass/pass |
| `raydb_optix_partner_resident_sum` | 0.000789793 | 0.000789572 | 1.000x | 15.020 | 15.057 | pass/pass |
| `robot_collision_optix_prepared_device_buffers` | 0.00188892 | 0.00183312 | 1.030x | 14.531 | 14.176 | pass/pass |
| `rt_dbscan_optix_grouped_stream` | 1.36516 | 1.42976 | 0.955x | 15.111 | 15.996 | pass/pass |
| `rtnn_optix_prepared_3d_ranked_summary` | 0.00141039 | 0.00132497 | 1.064x | 6.395 | 14.390 | miss/pass |
| `spatial_rayjoin_optix_prepared_full_route` | 0.000179395 | 0.000178140 | 1.007x | 14.601 | 14.242 | pass/pass |
| `triangle_counting_optix_rt_graph_2a1_partner` | 0.000350908 | 0.000358337 | 0.979x | 14.927 | 15.265 | pass/pass |

The only observed-target miss in the full packet is RTNN v2.3. Its plan was target-compliant, but the measured primary time became much faster than the seed, so `4534` repeats produced only `6.395` measured seconds.

## RTNN Supplement

A narrow RTNN supplement reran both lanes at `12000` repeats on the same 65,536-point input file.

| Lane | Primary sec | Observed sec | Wall sec | OK |
| --- | ---: | ---: | ---: | --- |
| v2.3 | 0.00153181 | 18.382 | 25.839 | true |
| v2.8/current | 0.00140091 | 16.811 | 23.431 | true |

Supplemental RTNN speedup: `1.093x`.

This closes the RTNN observed-duration gap for internal evidence. The full-packet row remains preserved rather than edited, so downstream reviewers can see both the original calibrated packet and the targeted supplement.

## Interpretation

This is not the dramatic speedup table the user wants for v2.9. It is a clean measurement-foundation result:

- The five formerly partial rows now have repeat/resident coverage on both v2.3 and current.
- RayJoin is no longer partial and no longer a fake high-ratio artifact; same-contract count-route performance is near parity at `1.007x`.
- Robot-collision measurement no longer leaks memory under long repeat runs.
- RTNN has the clearest current win in this packet: `1.064x` in the full packet and `1.093x` in the target-compliant supplement.
- RT-DBSCAN remains a real weak row at `0.955x`; this should be a v2.9 optimization target.
- Hausdorff threshold, triangle counting, Barnes-Hut, and contact manifold are effectively parity rows under this particular hot-query protocol.

## Claim Boundary

All artifacts keep the release and public-claim flags false. This evidence does not authorize:

- v2.9 release;
- public speedup claims;
- whole-app speedup claims;
- broad RT-core speedup claims;
- true zero-copy claims;
- paper-reproduction claims.

## Next Engineering Targets

1. Make Goal3536 report observed target counts directly in the summary, not only target-plan counts.
2. Add a repeat planner margin for rows whose primary metric varies downward across calibration passes.
3. Optimize `rt_dbscan_optix_grouped_stream`, the weakest row in the final full packet.
4. Audit why `robot_collision` needs roughly 5 minutes of wall time to produce a 15-second hot-query metric; the hot-query number is valid, but the app wrapper overhead is too high.
5. Convert this packet into the v2.9 baseline table before starting new primitive work.

