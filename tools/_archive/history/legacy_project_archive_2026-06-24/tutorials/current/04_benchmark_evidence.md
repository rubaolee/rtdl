# Benchmark Evidence

Status: V3 rebuild tutorial.

The repaired current-side pod evidence is:

| Suite | Result |
| --- | ---: |
| `goal2626_standard_all_rows` | 22 ok / 0 failed |
| `goal2636_standard_all_rows` | 28 ok / 0 failed |
| `goal3828_full_clean` | 10 pass / 0 fail |
| GPU Python environment gate | pass |

Local artifact roots:

```text
docs/rebuild/v3/evidence/v3_current_goal2626_clean_env_20260620_055523
docs/rebuild/v3/evidence/v3_current_goal2636_full_clean_20260620_060726
docs/rebuild/v3/evidence/v3_current_goal3828_full_clean_20260620_060412
docs/rebuild/v3/evidence/v3_gpu_python_env_gate_20260620_061058
```

Representative OptiX-over-Embree rows from the repaired artifacts:

| App row | Current-side signal |
| --- | ---: |
| `rt_dbscan` same-contract compact threshold | internal only: 1.150x / 1.079x / 1.071x at serious scales |
| `spatial_rayjoin` overlay strengthened row | 5419.291x |
| `raydb_style` grouped count | 277.838x |
| `triangle_counting` 20k cliques strengthened row | 114.229x |
| `robot_collision` prepared collision flags | 5.099x |
| `librts_spatial_index` calibrated generic AABB row | 814.339x |
| `librts_spatial_index` small standard row | 0.065x |

The RTDBSCAN row is intentionally not a public speedup claim: the old huge
all-app ratio was superseded by a same-contract rerun and stays internal. The
small LibRTS row is also intentionally included. Good docs must show both where
RTDL should choose another route and where a larger same-contract AABB workload
becomes a useful OptiX candidate.

Read next:

- [GPU Partner Gate](05_gpu_partner_gate.md)
