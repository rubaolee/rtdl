# Goal4367 RayJoin Authors-Code Comparison Packet

Status: accepted internal comparison packet; not RayJoin paper reproduction and not broad public speedup wording.

## Direction Rule

For the direct comparison table, `RayJoin RT / RTDL` greater than 1 means the RTDL backend is faster than RayJoin RT for the same scalar-count contract. Values below 1 mean RayJoin RT is faster.

## Artifact Manifest

| Artifact | Role | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `rayjoin_lsi_gen100000_stream.json` | RayJoin-exported LSI query stream consumed by RTDL | 12629271 | `6bed3890d327cbd7f33c6fb3c14b306484aa9f1ccca001710ec164f4d03671bd` |
| `rayjoin_pip_gen100000_stream.json` | RayJoin-exported PIP query stream consumed by RTDL | 7059404 | `d5ba3289e346febf86492d2f5d7abdab1a14977a5b6518fc813fd665a90b63a0` |
| `rayjoin_lsi_grid.log` | RayJoin original LSI grid-mode timing log | 1190 | `ccebf3404481cb85e9aacf7db966b2501c8215acd25d8a51a627a4e5efab470b` |
| `rayjoin_lsi_lbvh.log` | RayJoin original LSI LBVH-mode timing log | 1190 | `9820ba846993571780398814349499d17005651b52a8662fcb8ce4e94f67426e` |
| `rayjoin_lsi_rt.log` | RayJoin original LSI RT-mode timing log | 2235 | `32a333baf2e19c7dd18d9f29a0af6b3f238df49ec480273f85a4e4cd70764889` |
| `rayjoin_pip_grid.log` | RayJoin original PIP grid-mode timing log | 675 | `f738fb717a05d0dca81440279d173deaa18929d22fe8c8e5c75111b8aabfb274` |
| `rayjoin_pip_lbvh.log` | RayJoin original PIP LBVH-mode timing log | 841 | `0f6fe2c1ff4249fd0835c68436cfadd90e940f874428f62a81ee409bfb430e60` |
| `rayjoin_pip_rt.log` | RayJoin original PIP RT-mode timing log | 1519 | `38a6ce23cbfd41bc5d0dcba781da2ca658d62f95c0262cb08c8a40e2a458af84` |
| `rtdl_lsi_same_rayjoin_stream.json` | RTDL LSI same-stream scalar-count result | 3051 | `0b46cf3145aee850c5ca89d609f0ffd32ec94193cc7c8bf57e73b7e6855009d6` |
| `rtdl_pip_same_rayjoin_stream.json` | RTDL PIP same-stream scalar-count result | 3123 | `e61dff24e56a62a9cb49e23e5d5c53213a0eeea0ec19914589f7488a73237ad7` |
| `summary.json` | Compact goal4358 summary retained outside the source tree artifact dir | 6951 | `9ed49df8d27ce759b8480c96df863fb683b612ec6c05dc9f764fd453133a8695` |
| `goal4354_lsi_pip100k_exact_prepared_points_rtx_a4000_summary_after_embree_lsi_no_bruteforce.json` | Full same-stream summary after Embree LSI no-bruteforce repair | 27926 | `f4bb3c96848c4d467362f688a3c12c8a7eb904fec5e972c52bddd5dd8007f584` |

## RayJoin Original Logs

| Workload | Mode | Query ms | Build/index ms | Adaptive grouping ms | OptiX launches | Correctness signal |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `lsi` | `grid` | 6.595 | 3.922 | n/a | 0 | intersections=8921 |
| `lsi` | `lbvh` | 2.021 | 5.052 | n/a | 0 | intersections=8921 |
| `lsi` | `rt` | 0.819 | 2.565 | 0.547 | 6 | intersections=8921 |
| `pip` | `grid` | 22.39 | 2.957 | n/a | 0 | n/a |
| `pip` | `lbvh` | 12.728 | 5.464 | n/a | 0 | built_in_check=True |
| `pip` | `rt` | 0.83 | 5.399 | 0.605 | 6 | built_in_check=True |

## RTDL Same-Stream Results

| Workload | Backend | Hot query ms | Count | Route | RT-core accelerated | Row stream materialized |
| --- | --- | ---: | ---: | --- | --- | --- |
| `lsi` | `optix` | 0.336 | 8921 | `prepared_left_exact_segment_pair_scalar_count` | `True` | `False` |
| `lsi` | `embree` | 14.539 | 8921 | `prepared_embree_native_scalar_count` | `False` | `False` |
| `pip` | `optix` | 12.034 | 8686 | `prepared_exact_closed_shape_membership_prepared_points_scalar_count` | `True` | `False` |
| `pip` | `embree` | 14.168 | 8686 | `prepared_embree_native_scalar_count` | `False` | `False` |

## Direct Comparison

| Workload | RTDL backend | RayJoin RT query ms | RTDL hot query ms | RayJoin RT / RTDL | Reciprocal when RayJoin is faster | Readout |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `lsi` | `optix` | 0.819 | 0.336 | 2.437x | n/a | RTDL backend faster than RayJoin RT for this scalar-count contract |
| `lsi` | `embree` | 0.819 | 14.539 | 0.056x | 17.76x | RayJoin RT faster than RTDL backend for this scalar-count contract |
| `pip` | `optix` | 0.83 | 12.034 | 0.069x | 14.49x | RayJoin RT faster than RTDL backend for this scalar-count contract |
| `pip` | `embree` | 0.83 | 14.168 | 0.059x | 17.07x | RayJoin RT faster than RTDL backend for this scalar-count contract |

## Interpretation

- LSI: Reasonable strong RTDL result: the RTDL OptiX route is an exact prepared-left segment-pair scalar count on the same stream, counts match RayJoin RT intersections, and no row stream is materialized in the measured RTDL path.
- PIP: Reasonable but not good enough for RTDL: RayJoin RT remains much faster on PIP because the current RTDL exact prepared-points path spends material time in exact membership refinement and generic orchestration. This is a v2.13 optimization debt, not a public RTDL win.

## Claim Boundary

This packet compares RayJoin authors-code logs with RTDL same-stream scalar-count results. It does not authorize full RayJoin paper reproduction, whole-application speedup wording, public RTDL-beats-RayJoin wording, or broad RT-core claims.

Validation status: `accept`.
