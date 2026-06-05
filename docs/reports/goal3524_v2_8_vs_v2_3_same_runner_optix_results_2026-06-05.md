# Goal3524: v2.8 vs v2.3 Same-Runner OptiX Results

Date: 2026-06-05

Status: internal A5000 evidence collected; not a release packet and not public
speedup wording.

## Purpose

Goal3523 defined the protocol for comparing v2.8 against v2.3 without mixing
different app contracts. Goal3524 executes the first strict slice of that
protocol: the same `scripts/goal2626_benchmark_embree_optix_baseline.py`
OptiX-only runner was built and run in both a v2.3-era evidence checkout and
the current v2.8 checkout on the same RTX A5000 pod.

This answers a narrow question: can the shared Goal2626 OptiX runner compare
the accepted v2.3 evidence baseline against current v2.8 on identical hardware?
Yes. It does not answer every promoted-v2.8 question, because some v2.8 apps now
have evolved contracts that are intentionally different from the older Goal2626
rows.

## Source Of Truth

Tracked compact artifact:

- `docs/reports/goal3524_pod_artifacts/goal3524_compact_results.json`

Pod and build facts:

- GPU: NVIDIA RTX A5000, driver `580.126.09`, 24564 MiB
- CUDA: `/usr/local/cuda-12`, `nvcc` CUDA 12.8
- OptiX SDK: `/root/vendor/optix-sdk`
- Remote work root: `/root/rtdl_goal3524`
- SSH endpoint: `root@69.30.85.203 -p 22057`
- SSH key actually used by Codex: repo-local `id_ed25519_rtdl_codex`
- v2.3 evidence checkout: `2a28365d0246d51f3e3322b546f8a68c58632db4`
- v2.8 checkout: `d266b0370bcbcd4cbc24006ce9de2dfe783c1d2e`

Boundary note: this uses the accepted v2.3-era evidence commit, not the literal
`v2.3` tag, because the literal tag does not contain the Goal2626 all-benchmark
runner. This is the same distinction recorded in Goal3523.

Remote raw artifacts:

- `/root/rtdl_goal3524/artifacts/v23_evidence_standard_optix/summary.json`
- `/root/rtdl_goal3524/artifacts/v28_current_standard_optix/summary.json`
- `/root/rtdl_goal3524/artifacts/v23_evidence_standard_optix_weak_rerun/summary.json`
- `/root/rtdl_goal3524/artifacts/v28_current_standard_optix_weak_rerun/summary.json`

The tracked local artifact is compacted to avoid committing multi-megabyte raw
summaries.

## Standard Same-Runner OptiX Table

All 11 shared OptiX cases completed with status `ok` in both checkouts.

| App | Case | v2.3 evidence sec | v2.8 sec | v2.8 speedup vs v2.3 |
| --- | --- | ---: | ---: | ---: |
| `barnes_hut` | `barnes_hut_optix_node_coverage` | 0.011919661 | 0.029753055 | 0.401x |
| `contact_manifold` | `contact_manifold_optix_aabb_broadphase_collect_k` | 0.027746658 | 0.028518789 | 0.973x |
| `hausdorff_xhd` | `hausdorff_optix_threshold` | 0.042307159 | 0.035178864 | 1.203x |
| `librts_spatial_index` | `librts_optix_aabb_index` | 0.459445468 | 0.458496532 | 1.002x |
| `raydb_style` | `raydb_optix_partner_resident_count` | 0.000646546 | 0.000654835 | 0.987x |
| `raydb_style` | `raydb_optix_partner_resident_sum` | 0.005897518 | 0.000818909 | 7.202x |
| `robot_collision` | `robot_collision_optix_prepared_device_buffers` | 0.001886345 | 0.001905329 | 0.990x |
| `rt_dbscan` | `rt_dbscan_optix_grouped_stream` | 1.520225293 | 1.368746759 | 1.111x |
| `rtnn` | `rtnn_optix_prepared_3d_ranked_summary` | 0.001708961 | 0.001645898 | 1.038x |
| `spatial_rayjoin` | `spatial_rayjoin_optix_prepared_full_route` | 0.000529252 | 0.000482951 | 1.096x |
| `triangle_counting` | `triangle_counting_optix_rt_graph_2a1_partner` | 0.000433386 | 0.000437028 | 0.992x |

Summary:

- rows: 11
- v2.8 wins: 6
- v2.8 losses: 5
- median speedup: 1.002x
- geometric mean speedup: 1.138x
- best row: `raydb_optix_partner_resident_sum`, 7.202x
- worst row: `barnes_hut_optix_node_coverage`, 0.401x

## Weak-Row Rerun

The weak or near-flat rows were rerun as a targeted check.

| App | Case | v2.3 evidence sec | v2.8 sec | v2.8 speedup vs v2.3 |
| --- | --- | ---: | ---: | ---: |
| `barnes_hut` | `barnes_hut_optix_node_coverage` | 0.012506337 | 0.024860590 | 0.503x |
| `contact_manifold` | `contact_manifold_optix_aabb_broadphase_collect_k` | 0.028573418 | 0.027752892 | 1.030x |
| `raydb_style` | `raydb_optix_partner_resident_count` | 0.000639002 | 0.000641004 | 0.997x |
| `robot_collision` | `robot_collision_optix_prepared_device_buffers` | 0.001882866 | 0.001942751 | 0.969x |
| `triangle_counting` | `triangle_counting_optix_rt_graph_2a1_partner` | 0.000442130 | 0.000431465 | 1.025x |

Interpretation:

- Barnes-Hut node coverage is the real regression. It is slower in both runs,
  at 0.401x in the standard run and 0.503x in the rerun.
- Robot collision is slightly slower in both runs.
- RayDB count is essentially flat and slightly slower.
- Contact manifold and triangle counting look like parity/noise around 1.0x;
  they flip direction between the standard run and weak rerun.

## Engineering Reading

This result is useful but not flattering enough to hide behind a headline:
v2.8 is not uniformly faster than the v2.3 evidence baseline under the shared
Goal2626 OptiX runner.

The good news is that the same-runner comparison is complete, reproducible, and
overall positive by geometric mean. The strong RayDB sum win shows that some
primitive-first grouped-reduction work is paying off even under the old runner.
Hausdorff, RayJoin, DBSCAN, RTNN, and LibRTS also move in the right direction or
stay close to parity.

The caution is that Barnes-Hut node coverage regressed significantly, and this
must remain visible in any v2.8 planning or release discussion. The likely next
engineering target is a Barnes-Hut-specific investigation under the same
contract: confirm whether the slowdown comes from codegen, launch structure,
prepared-handle setup, threshold parameters, or extra generic bookkeeping added
after v2.3.

## What This Does Not Claim

Goal3524 does not authorize:

- public v2.8 release wording;
- public speedup wording;
- whole-app speedup wording;
- broad RT-core speedup wording;
- package-install or PyPI wording;
- true zero-copy wording;
- paper reproduction claims;
- hidden partner selection;
- app-specific native-engine behavior.

The compact artifact encodes the same claim boundary with all authorization
flags set to false.

## Next Steps

1. Investigate the Barnes-Hut node-coverage regression first.
2. Decide whether the final v2.8 comparison should remain a same-runner table
   or add a second promoted-v2.8-contract table for evolved paths.
3. Seek external review of this Goal3524 packet before using it in any release
   narrative.

## Validation

Local validation:

```text
PYTHONPATH=src;. py -3 -m unittest tests.goal3524_v2_8_vs_v2_3_same_runner_optix_results_test
```

## Verdict

`accept-with-boundary`

The A5000 pod is usable and the same-runner OptiX comparison is complete. The
result is internal evidence, not final release authorization. It establishes
one strong improvement, several small wins, several parity rows, and one clear
regression that should be investigated before v2.8 positioning is finalized.
