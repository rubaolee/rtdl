# Goal1201 OptiX Slower-App Investigation Intake

Date: 2026-05-01

Goal1201 intakes Goal1200 cloud artifacts only. It does not authorize public docs, release, or public RTX speedup claims.

## Summary

- status count: `31`
- failed count: `5`
- failed labels: `db_embree_100000, db_embree_300000, db_optix_100000, db_optix_300000, polygon_jaccard_optix_8192_chunk_64`
- archive sha256: `4e7409a0ad3015662026956696bca22ba832a5a3c7719e73e3c9a5a23e5d5079`
- public positive candidates from this batch: `none`

## Decisions

- `database_analytics`: `blocked_scale_ceiling_and_no_positive_speedup`
- `graph_analytics`: `rt_subpaths_completed_but_total_pack_prepare_dominated`
- `polygon_pair_overlap_area_rows`: `stable_rt_path_evidence_largest_scale_near_parity_no_public_positive_claim`
- `polygon_set_jaccard`: `blocked_existing_artifact_has_chunk64_failure_future_runs_must_use_public_safe_chunk_policy`
- `road_hazard_screening`: `positive_control_reproduced_but_public_floor_not_met_in_this_run`
- `hausdorff_distance`: `normalized_repair_evidence_collected_same_scale_still_missing`

## Database

| Copies | Embree status | OptiX status | Embree sec | OptiX sec | Ratio |
| ---: | --- | --- | ---: | ---: | ---: |
| `30000` | `ok` | `ok` | `0.092577` | `0.122074` | `0.758368` |
| `100000` | `failed` | `failed` | `n/a` | `n/a` | `n/a` |
| `300000` | `failed` | `failed` | `n/a` | `n/a` | `n/a` |

## Graph Visibility

| Copies | Embree sec | OptiX total sec | OptiX any-hit kernel sec | Total ratio | Kernel ratio | OptiX status |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `30000` | `0.78965` | `1.38627` | `0.000170158` | `0.569623` | `4640.68` | `pass` |
| `60000` | `1.58868` | `2.16487` | `0.000192118` | `0.733845` | `8269.31` | `pass` |
| `120000` | `3.18045` | `3.96891` | `0.000212318` | `0.80134` | `14979.6` | `pass` |

## Polygon Pair

| Copies | Embree sec | OptiX sec | Ratio | Parity |
| ---: | ---: | ---: | ---: | --- |
| `10000` | `1.09608` | `1.59694` | `0.686364` | `True` |
| `20000` | `2.22463` | `2.34855` | `0.947236` | `True` |
| `40000` | `4.59201` | `4.3847` | `1.04728` | `True` |

## Polygon Jaccard

| Chunk | Status | Exit | Chunk policy | Embree sec | OptiX sec | Ratio | Parity |
| ---: | --- | ---: | --- | ---: | ---: | ---: | --- |
| `1` | `ok` | `0` | `legacy_unclassified` | `0.729702` | `10.8828` | `0.0670509` | `True` |
| `8` | `ok` | `0` | `legacy_unclassified` | `0.729702` | `2.2758` | `0.320635` | `True` |
| `64` | `failed` | `1` | `legacy_unclassified` | `0.729702` | `1.45972` | `0.499891` | `False` |
| `512` | `ok` | `0` | `legacy_unclassified` | `0.729702` | `1.33637` | `0.546034` | `True` |

## Road Hazard Control

- Embree sec: `0.364707`
- OptiX sec: `0.0783454`
- Ratio Embree/OptiX: `4.65512`
- OptiX timing floor met: `False`
- Public positive ratio safe: `False`

## Hausdorff Normalized Repair

- Same-scale pair available: `False`
- Best Embree points/sec: `21963`
- Best OptiX points/sec: `1.69657e+08`
- Normalized OptiX/Embree throughput: `7724.68`

## Boundary

Goal1201 intakes Goal1200 cloud artifacts only. It does not authorize public docs, release, or public RTX speedup claims.

## Follow-Ups

- database_analytics needs chunked/streamed RT lowering before larger-scale DB claims
- polygon_set_jaccard needs chunk-stable OptiX correctness before promotion
- road_hazard_screening needs a larger floor-safe positive-control rerun
- hausdorff_distance needs same-scale or formally reviewed normalized evidence
- graph_analytics should keep kernel/pack/prepare/bookkeeping wording separated
- polygon_pair_overlap_area_rows needs additional tuning before public positive wording

## Conclusion

This pod run is useful engineering evidence, but it adds no new public positive RTX speedup candidate under the current timing-floor and same-scale rules. The next work is local code improvement plus one batched pod rerun after DB chunking, Jaccard stability, road-hazard scale, and Hausdorff comparison repairs are ready.

