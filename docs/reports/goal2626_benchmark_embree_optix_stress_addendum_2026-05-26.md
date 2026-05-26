# Goal2626 Embree vs OptiX Stress Addendum

This addendum records extra RTX A5000 pod tests run after the main Goal2626
baseline. It is internal engineering evidence for the next partner-runtime
version, not public speedup wording.

## Context

- Pod: `root@203.57.40.101 -p 10165`
- Working key on this Mac: `~/.ssh/id_ed25519_rtdl_codex`
- Main baseline commit already recorded: `11da92848a30be3a71d76ac58d8f53b1c8621ba7`
- Primary baseline report:
  `docs/reports/goal2626_benchmark_embree_optix_baseline_pod/summary.md`

## Additional Stress Evidence

| Stress test | Scale | Embree or CPU sec | OptiX sec | OptiX ratio | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| Hausdorff / X-HD threshold | large, 16384 copies | 0.399736 | 0.370397 | 1.08x | OptiX slightly faster |
| Barnes-Hut node coverage | large, 32768 bodies | 0.949983 | 1.76206 | 0.539x | Embree faster |
| Triangle counting summary | large, 20000 copies | 0.915364 | 1.56583 | 0.585x | Embree faster |
| Robot collision prepared query | 32768 poses, 512 obstacles, 2 links | 0.0568973 | 0.00643277 | 8.84x | OptiX faster in steady-state prepared-query timing |
| Contact AABB collect | grid 8192 | 0.837436 CPU discovery | 0.929862 OptiX discovery | 0.901x | CPU slightly faster at small scale |
| Contact AABB collect | grid 65536 | 36.4272 CPU discovery | 2.15704 OptiX discovery | 16.9x | OptiX faster after scale crossover |

## Interpretation

The extra tests sharpen the baseline instead of changing the main conclusion.
OptiX wins when the work is a large, reusable RT-shaped traversal or generic
AABB row-discovery path. Embree remains stronger for some compact or
process-wall-dominated app front doors where Python startup, app staging, or
non-RT postprocessing dominates.

The robot stress exposes an important measurement boundary: the app still runs
a CPU probe-reference oracle before backend timing. The reported `8.84x` ratio
is a steady-state prepared-query backend ratio, not end-to-end process wall
time. The per-run traversal medians are `0.0199478s` for Embree and
`0.000260056s` for OptiX, while prepared-query build phases are about
`2.37s` and `2.55s`. Future partner-runtime work should avoid repeatedly
charging Python oracle or preparation work when evaluating native RT kernels.

The contact-manifold stress gives the clearest new primitive-level signal:
`AABB_INDEX_QUERY_2D` plus `COLLECT_K_BOUNDED` is overhead-bound at 8192 rows,
but crosses over strongly by 65536 rows. This supports using the generic
bounded-row and broadphase primitives as optimization targets for the next
version instead of adding app-specific contact or collision logic.

## Copied Artifacts

- `docs/reports/goal2626_benchmark_embree_optix_stress_pod_large_no_robot/summary.md`
- `docs/reports/goal2626_benchmark_embree_optix_stress_pod_large_no_robot/summary.json`
- `docs/reports/goal2626_robot_collision_stress_pod_32768x512/summary.md`
- `docs/reports/goal2626_robot_collision_stress_pod_32768x512/compact_summary.json`
- `docs/reports/goal2626_contact_aabb_collect_stress_pod_8192/summary.md`
- `docs/reports/goal2626_contact_aabb_collect_stress_pod_8192/summary.json`
- `docs/reports/goal2626_contact_aabb_collect_stress_pod_65536/summary.md`
- `docs/reports/goal2626_contact_aabb_collect_stress_pod_65536/summary.json`

Large raw files generated on the pod were intentionally not copied into Git:
RTNN point CSVs, full robot flag dumps, and raw contact payloads. The compact
summaries are sufficient for internal baseline tracking.
