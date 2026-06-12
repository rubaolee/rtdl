# Goal4354 RayJoin Original vs RTDL+Partner Same-Stream Comparison

Status: measured on the pod from RayJoin-exported query streams. Speedup column is `RayJoin RT Query ms / RTDL hot query ms`; values above 1 mean RTDL is faster.

## Scope

- RayJoin side: original `query_exec` logs for `grid`, `lbvh`, and `rt` modes.
- RTDL side: current prepared scalar-count hot paths, consuming the same exported queries.
- Contract: scalar count only; RTDL measured paths do not materialize match rows.
- Boundary: this is not a full RayJoin paper reproduction claim.
- Release hygiene: the large exported query-stream JSON files and raw run logs
  are intentionally omitted from the source tree; this compact summary is the
  retained evidence artifact.

## RayJoin Original Logs

| Workload | Mode | Query ms | Build index ms | Adaptive grouping ms | OptiX launches | Intersections | Built-in check |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `lsi` | `grid` | 4.974680 | 3.715990 | n/a | 0 | 8921 | n/a |
| `lsi` | `lbvh` | 1.546700 | 4.909990 | n/a | 0 | 8921 | n/a |
| `lsi` | `rt` | 1.012010 | 0.756025 | 0.604153 | 4 | 8921 | n/a |
| `pip` | `grid` | 15.885000 | 3.178830 | n/a | 0 | n/a | n/a |
| `pip` | `lbvh` | 8.205650 | 7.719990 | n/a | 0 | n/a | pass |
| `pip` | `rt` | 0.613610 | 1.024010 | 0.609875 | 4 | n/a | pass |

## RTDL Same-Stream Results

| Workload | Backend | Query count | Row count | Hot median ms | Hot total s | Repeats | Native traversal ms | Route |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `lsi` | `optix` | 100000 | 8921 | 0.237690 | 0.000746 | 3 | n/a | `prepared_left_exact_segment_pair_scalar_count` |
| `lsi` | `embree` | 100000 | 8921 | 183730.426896 | 183.730427 | 1 | 183525.940321 | `prepared_embree_native_scalar_count` |
| `pip` | `optix` | 100000 | 8686 | 7.081935 | 0.024170 | 3 | n/a | `prepared_exact_closed_shape_membership_scalar_count` |
| `pip` | `embree` | 100000 | 8686 | 71.735307 | 0.071735 | 1 | 45.135902 | `prepared_embree_native_scalar_count` |

## Direct Comparison

| Workload | RTDL backend | RayJoin RT query ms | RTDL hot query ms | Speedup | Readout |
| --- | --- | ---: | ---: | ---: | --- |
| `lsi` | `optix` | 1.012010 | 0.237690 | 4.258x | RTDL faster on the same stream |
| `lsi` | `embree` | 1.012010 | 183730.426896 | 0.000x | RayJoin RT faster on the same stream |
| `pip` | `optix` | 0.613610 | 7.081935 | 0.087x | RayJoin RT faster on the same stream |
| `pip` | `embree` | 0.613610 | 71.735307 | 0.009x | RayJoin RT faster on the same stream |

## Correctness Checks

| Workload | RTDL counts | Cross-backend match | External check |
| --- | --- | --- | --- |
| `lsi` | optix=8921, embree=8921 | True | RayJoin RT intersections=8921; match=True |
| `pip` | optix=8686, embree=8686 | True | RayJoin RT built-in check=True; RayJoin PIP log has no exported count |

## Interpretation Notes

- `lsi`: the RTDL route is the current exact prepared-left segment-pair scalar count front door.
- `pip`: the RTDL route is the exact prepared closed-shape scalar count. The faster relation-status executor is recorded only as a rejected diagnostic when it disagrees with exact semantics.
- Differences versus RayJoin RT can come from specialization: RayJoin is a purpose-built C++/CUDA/OptiX program, while RTDL keeps a generic runtime contract and Python front-door orchestration outside the timed native call.
- The table separates hot query time from one-time pack/prepare work in the JSON artifact.
