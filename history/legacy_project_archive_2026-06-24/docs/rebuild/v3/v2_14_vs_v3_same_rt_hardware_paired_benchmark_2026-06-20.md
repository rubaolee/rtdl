# V2.14 vs Current V3 Same RT Hardware Paired Benchmark

Status: serious paired evidence, 2026-06-20.

This report answers the narrow question:

```text
On the same RTX pod, with the same benchmark runners and same workloads where
both versions can run, is current V3 faster than V2.14?
```

Short answer:

```text
V3 is clearly stronger on runability and benchmark-route health.
V3 is not proven broadly faster than V2.14 on same-metric raw timing.
Same-row performance is mostly parity with row-specific wins and a few losses.
```

## Artifact

Remote:

```text
/root/rtdl_v3_rebuild_20260620/artifacts/v2_14_vs_v3_same_rt_hardware_paired_20260620_140120
```

Local:

```text
docs/rebuild/v3/evidence/v2_14_vs_v3_same_rt_hardware_paired_20260620_140120
```

Summary files:

```text
paired_v2_v3_summary.json
paired_v2_v3_summary.md
main.log
status.tsv
```

Second-machine report-gate confirmation:

```text
docs/rebuild/v3/evidence/v3_paired_report_lx1_confirmation_20260620
```

That confirmation passes the V3 rebuild test matrix, release wording gate, and
source-tree doctor on `lx1`. It does not rerun the performance suite.

Hardware:

```text
NVIDIA RTX 4000 Ada Generation, driver 550.127.05, 20475 MiB
```

Baseline:

```text
V2.14 tag: v2.14
V2.14 commit: 8384a38376567fe518d89721453eb4433de08312
Current V3 tree: /root/rtdl_v3_rebuild_20260620/current
```

## Suite Results

| Suite | V2.14 result | Current V3 result | Meaning |
| --- | ---: | ---: | --- |
| `goal2626_standard` | 20 ok / 2 failed | 22 ok / 0 failed | V3 repairs standard benchmark route failures. |
| `goal2636_standard` | 26 ok / 2 failed | 28 ok / 0 failed | V3 repairs strengthened benchmark route failures. |
| `goal3828_full` | 9 pass / 1 failed | 10 pass / 0 failed | V3 passes the full scale-profile gate where V2.14 does not. |

V2.14 failed rows:

| Suite | Row | Failure |
| --- | --- | --- |
| `goal2626_standard` | `spatial_rayjoin_optix_prepared_full_route` | OptiX invalid value in prepared count route. |
| `goal2626_standard` | `triangle_counting_optix_rt_graph_2a1_partner` | CUDA/PTX toolchain launch failure. |
| `goal2636_standard` | `triangle_counting_optix_rt_graph_2a1_cliques_5000` | CUDA/PTX toolchain launch failure. |
| `goal2636_standard` | `triangle_counting_optix_rt_graph_2a1_cliques_20000` | CUDA/PTX toolchain launch failure. |
| `goal3828_full` | `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | V2.14 tree cannot resolve the public-CDB data directory. |

Current V3 failed rows:

```text
none in these three suites
```

## Same-Metric Timing

Only rows where both V2.14 and current V3 produced numeric
`primary_metric_sec` are included in the timing comparison.

```text
Compared rows: 46
V3 faster by >5%: 10
Within +/-5%: 32
V3 slower by >5%: 4
Geomean V3 speedup vs V2.14: 1.012x
```

That is essentially parity, not a major speedup.

App-level geomean:

| App | V3 speedup vs V2.14 |
| --- | ---: |
| `barnes_hut` | 0.917x |
| `contact_manifold` | 0.996x |
| `hausdorff_xhd` | 1.062x |
| `librts_spatial_index` | 1.163x |
| `raydb_style` | 1.017x |
| `robot_collision` | 1.016x |
| `rt_dbscan` | 0.992x |
| `rtnn` | 1.019x |
| `spatial_rayjoin` | 1.000x |
| `triangle_counting` | 0.984x |

## Strongest Same-Row V3 Wins

| Suite | App | Case | Backend | V3 speedup vs V2.14 |
| --- | --- | --- | --- | ---: |
| `goal2636_standard` | `spatial_rayjoin` | `rayjoin_optix_promoted_overlay_seed_tiled_x512` | OptiX | 1.305x |
| `goal2636_standard` | `hausdorff_xhd` | `hausdorff_optix_threshold_copies_16384` | OptiX | 1.209x |
| `goal2626_standard` | `librts_spatial_index` | `librts_embree_aabb_index` | Embree | 1.206x |
| `goal2636_standard` | `hausdorff_xhd` | `hausdorff_embree_threshold_copies_16384` | Embree | 1.205x |
| `goal2636_standard` | `rtnn` | `rtnn_embree_clustered_65536_ranked_summary` | Embree | 1.195x |
| `goal2626_standard` | `raydb_style` | `raydb_optix_partner_resident_sum` | OptiX | 1.155x |

## Strongest Same-Row V3 Losses

| Suite | App | Case | Backend | V3 speedup vs V2.14 |
| --- | --- | --- | --- | ---: |
| `goal2636_standard` | `barnes_hut` | `barnes_hut_optix_node_coverage_bodies_32768` | OptiX | 0.639x |
| `goal2626_standard` | `spatial_rayjoin` | `spatial_rayjoin_embree_generic` | Embree | 0.855x |
| `goal2636_standard` | `spatial_rayjoin` | `rayjoin_embree_lsi_tiled_x512` | Embree | 0.917x |
| `goal2636_standard` | `spatial_rayjoin` | `rayjoin_embree_pip_tiled_x512` | Embree | 0.942x |

These rows need performance tuning or explanation before any performance-first
V3 release wording.

## Verdict

What this evidence supports:

```text
Current V3 is stronger than V2.14 as a usable benchmark-app platform because it
passes route and scale-profile rows that V2.14 fails.
```

What this evidence does not support:

```text
Current V3 broadly outperforms V2.14 in same-row raw timing.
```

The honest V3 performance claim is therefore:

```text
V3 repairs important V2.14 runability failures and preserves mostly parity
same-row performance, with row-specific speedups and a few regressions that
still require tuning or public explanation.
```

## Release Boundary

```text
release_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

Do not publish a broad V3-over-V2 speedup claim from this artifact.

## Goal-Level Decision Audit

Decision: use this artifact as the current V2.14-vs-V3 paired evidence source.

1. Did I make a foolish decision?

   The corrected decision is not foolish. It replaces vague performance wording
   with a same-hardware paired run.

2. What action would make it foolish?

   Treating the 1.012x geomean as a major speedup, or hiding the four same-row
   V3 losses.

3. Was there another path?

   Yes. I could have reused older partial artifacts or only compared V3 OptiX
   against V3 Embree. Those paths do not answer the user's V2-vs-V3 question.

4. Can I now try a different path that truly solves the problem?

   Yes. The next performance path is targeted tuning for the losing rows,
   especially Barnes-Hut OptiX 32768 and Spatial RayJoin Embree rows, followed
   by another same-hardware paired rerun.
