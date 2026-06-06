# Goal3561 Near-Parity Rows A5000 Probe

Date: 2026-06-06

## Purpose

Goal3560 Claude review suggested checking the cluster of small negative rows in Goal3558. Goal3561 runs targeted A5000 probes for the four near-parity rows that were below 1.0 in the full packet:

- Barnes-Hut node coverage
- LibRTS AABB index
- robot collision prepared device buffers
- spatial RayJoin prepared full route

## Results

Artifact directory:

`docs/reports/goal3561_near_parity_rows_probe_a5000/`

| Case | v2.3 sec | v2.8/v2.9 sec | Speedup |
| --- | ---: | ---: | ---: |
| `barnes_hut_optix_node_coverage` | 0.008181240 | 0.008198984 | 0.997836x |
| `librts_optix_aabb_index` | 0.000758030 | 0.000762927 | 0.993581x |
| `robot_collision_optix_prepared_device_buffers` | 0.001903920 | 0.001901677 | 1.001180x |
| `spatial_rayjoin_optix_prepared_full_route` | 0.000191347 | 0.000183260 | 1.044129x |

All four targeted rows met the 10-second observed target on both sides.

## Interpretation

This probe supports the Goal3559 conclusion: after RT-DBSCAN and RTNN cleanup, the remaining small negatives are mostly near-parity variance, not clear code-change mandates. LibRTS is still slightly below parity at `0.994x`, but that is too small to justify a source change without stronger repeated evidence.

## Boundaries

This is internal benchmark evidence only.

This goal does not authorize:

- release or tag action;
- public v2.9 speedup claims;
- broad RT-core speedup claims;
- whole-app acceleration claims;
- true zero-copy claims.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3561_near_parity_rows_probe_test tests.goal3559_raydb_sum_count_stability_probe_test
```

## Next Step

No immediate code change is justified from these four rows. Keep them on the watch list for a future repeated full-packet protocol.
