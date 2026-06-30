# Goal4354 RayJoin Original vs RTDL+Partner Same-Stream Comparison

Status: measured from RayJoin-exported query streams. Speedup column is `RayJoin RT Query ms / RTDL hot query ms`; values above 1 mean RTDL is faster.

## Scope

- RayJoin side: original `query_exec` logs for `grid`, `lbvh`, and `rt` modes.
- RTDL side: current prepared scalar-count hot paths, consuming the same exported queries.
- Contract: scalar count only; RTDL measured paths do not materialize match rows.
- Boundary: this is not a full RayJoin paper reproduction claim.

## Hardware Classification

| Field | Value |
| --- | --- |
| GPU | `NVIDIA RTX A4000, 580.126.20` |
| GPU compute capability query | `NVIDIA RTX A4000, 580.126.20, 8.6` |
| NVIDIA RT-core hardware for this run | yes |
| Detection | GPU name contains RTX |

## RayJoin Original Logs

| Workload | Mode | Query ms | Build index ms | Adaptive grouping ms | OptiX launches | Intersections | Built-in check |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `lsi` | `grid` | 6.594990 | 3.922220 | n/a | 0 | 8921 | n/a |
| `lsi` | `lbvh` | 2.020840 | 5.052090 | n/a | 0 | 8921 | n/a |
| `lsi` | `rt` | 0.818825 | 2.564910 | 0.547171 | 6 | 8921 | n/a |
| `pip` | `grid` | 22.390400 | 2.956870 | n/a | 0 | n/a | n/a |
| `pip` | `lbvh` | 12.728400 | 5.464080 | n/a | 0 | n/a | pass |
| `pip` | `rt` | 0.830221 | 5.398990 | 0.605106 | 6 | n/a | pass |

## RTDL Same-Stream Results

| Workload | Backend | RT-core hw | Query count | Row count | Hot median ms | Hot total s | Repeats | Native phase ms | Route |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `lsi` | `optix` | yes | 100000 | 8921 | 0.335959 | 0.001607 | 5 | n/a | `prepared_left_exact_segment_pair_scalar_count` |
| `lsi` | `embree` | no | 100000 | 8921 | 14.538773 | 0.072705 | 5 | 10.648286 | `prepared_embree_native_scalar_count` |
| `pip` | `optix` | yes | 100000 | 8686 | 12.033907 | 0.056421 | 5 | 6.806260 | `prepared_exact_closed_shape_membership_prepared_points_scalar_count` |
| `pip` | `embree` | no | 100000 | 8686 | 14.167797 | 0.122312 | 5 | 11.039620 | `prepared_embree_native_scalar_count` |

## Direct Comparison

| Workload | RTDL backend | RayJoin RT query ms | RTDL hot query ms | Speedup | Readout |
| --- | --- | ---: | ---: | ---: | --- |
| `lsi` | `optix` | 0.818825 | 0.335959 | 2.437x | RTDL faster on the same stream |
| `lsi` | `embree` | 0.818825 | 14.538773 | 0.056x | RayJoin RT faster on the same stream |
| `pip` | `optix` | 0.830221 | 12.033907 | 0.069x | RayJoin RT faster on the same stream |
| `pip` | `embree` | 0.830221 | 14.167797 | 0.059x | RayJoin RT faster on the same stream |

## Correctness Checks

| Workload | RTDL counts | Cross-backend match | External check |
| --- | --- | --- | --- |
| `lsi` | optix=8921, embree=8921 | True | RayJoin RT intersections=8921; match=True |
| `pip` | optix=8686, embree=8686 | True | RayJoin RT built-in check=True; RayJoin PIP log has no exported count |

## Interpretation Notes

- `lsi`: the RTDL route is the current exact prepared-left segment-pair scalar count front door.
- `pip`: the RTDL route is selected by `--pip-rtdl-count-mode`; `exact` preserves the original Goal4354 exact prepared closed-shape scalar count, while `exact_prepared_points` reuses prepared query-point columns but still performs host exact refinement.
- The faster relation-status executor is recorded only as a rejected diagnostic when it disagrees with exact PIP semantics.
- Differences versus RayJoin RT can come from specialization: RayJoin is a purpose-built C++/CUDA/OptiX program, while RTDL keeps a generic runtime contract and Python front-door orchestration outside the timed native call.
- The table separates hot query time from one-time pack/prepare work in the JSON artifact.
