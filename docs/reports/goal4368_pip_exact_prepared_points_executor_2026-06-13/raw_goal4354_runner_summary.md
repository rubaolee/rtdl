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
| `pip` | `grid` | 22.390400 | 2.956870 | n/a | 0 | n/a | n/a |
| `pip` | `lbvh` | 12.728400 | 5.464080 | n/a | 0 | n/a | pass |
| `pip` | `rt` | 0.830221 | 5.398990 | 0.605106 | 6 | n/a | pass |

## RTDL Same-Stream Results

| Workload | Backend | RT-core hw | Query count | Row count | Hot median ms | Hot total s | Repeats | Native phase ms | Route |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `pip` | `optix` | yes | 100000 | 8686 | 6.040250 | 0.047712 | 7 | 5.992433 | `prepared_exact_closed_shape_membership_prepared_points_scalar_count_executor` |
| `pip` | `embree` | no | 100000 | 8686 | 19.428359 | 0.144930 | 7 | 15.722725 | `prepared_embree_native_scalar_count` |

## Direct Comparison

| Workload | RTDL backend | RayJoin RT query ms | RTDL hot query ms | Speedup | Readout |
| --- | --- | ---: | ---: | ---: | --- |
| `pip` | `optix` | 0.830221 | 6.040250 | 0.137x | RayJoin RT faster on the same stream |
| `pip` | `embree` | 0.830221 | 19.428359 | 0.043x | RayJoin RT faster on the same stream |

## Correctness Checks

| Workload | RTDL counts | Cross-backend match | External check |
| --- | --- | --- | --- |
| `pip` | optix=8686, embree=8686 | True | RayJoin RT built-in check=True; RayJoin PIP log has no exported count |

## Interpretation Notes

- `lsi`: the RTDL route is the current exact prepared-left segment-pair scalar count front door.
- `pip`: the RTDL route is selected by `--pip-rtdl-count-mode`; `exact` preserves the original Goal4354 exact prepared closed-shape scalar count, while `exact_prepared_points` reuses prepared query-point columns but still performs host exact refinement.
- The faster relation-status executor is recorded only as a rejected diagnostic when it disagrees with exact PIP semantics.
- Differences versus RayJoin RT can come from specialization: RayJoin is a purpose-built C++/CUDA/OptiX program, while RTDL keeps a generic runtime contract and Python front-door orchestration outside the timed native call.
- The table separates hot query time from one-time pack/prepare work in the JSON artifact.
