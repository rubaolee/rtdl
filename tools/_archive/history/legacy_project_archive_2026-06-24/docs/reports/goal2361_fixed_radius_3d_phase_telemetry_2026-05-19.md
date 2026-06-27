# Goal2361 - Fixed-Radius 3D Phase Telemetry

Date: 2026-05-19

Status: implemented and pod-tested; optimization decision evidence collected.

## Purpose

Goal2357/Goal2359 improved the RTDL OptiX 3D bounded-neighbor path with a generic uniform-cell compact row stream. It now beats the old RTDL all-pairs CUDA path on the tested warm/raw rows, but still trails RTNN at the larger 262k row.

Goal2361 adds phase telemetry so the next v2.2 optimization is driven by evidence instead of guesswork. This is not RTNN-specific: it instruments the generic `fixed_radius_neighbors_3d` OptiX primitive.

## Implementation

The OptiX backend now records the most recent 3D fixed-radius neighbor execution in these phases:

| Field | Meaning |
| --- | --- |
| `mode` | `all_pairs_cuda`, `uniform_cell_compact`, `simple_rt_traversal`, or `none` |
| `prepare` | host-side point packing, grid/cell preparation, and RT BVH build where applicable |
| `upload` | device upload for query/search/grid data |
| `candidate_count_pass` | first pass for per-query capped counts |
| `count_download_and_prefix` | count copyback plus host prefix offsets |
| `row_offset_upload` | compact-row offset upload |
| `candidate_write_pass` | compact candidate row write pass, or RT traversal time for the diagnostic RT mode |
| `row_download` | compact row copyback |
| `exact_refine` | host exact-distance filtering and output normalization |
| `raw_candidate_count` | compact candidate rows before exact host refinement |
| `emitted_count` | final rows returned to Python |

The C ABI is:

```text
rtdl_optix_fixed_radius_neighbors_3d_get_last_phase_timings
```

The Python helper is:

```python
rt.get_last_fixed_radius_neighbors_3d_phase_timings()
```

The RTNN comparison harness now writes `phase_timings` into RTDL JSON artifacts from `run-rtdl-current-3d-neighbors-smoke`.

## Pod Evidence

| Item | Value |
| --- | --- |
| SSH endpoint | `ssh root@69.30.85.236 -p 22170 -i id_ed25519_rtdl_codex` |
| GPU | NVIDIA RTX A5000 |
| CUDA | 12.8.93 |
| OptiX SDK | `/root/vendor/optix-sdk-9.0` |
| Build | `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk-9.0 CUDA_PREFIX=/usr/local/cuda` passed |
| Unit smoke | `tests.goal311_v0_5_optix_3d_nn_test` + `tests.goal2357_v2_2_rtnn_uniform_cell_neighbor_step_test`: 7/7 pass |

Artifacts:

```text
docs/reports/goal2361_rtdl_3d_neighbor_phase/
```

Same-protocol warm/raw rows with telemetry:

| Input | Wall sec | Row count | Native phase sum | Key native phase signal |
| --- | ---: | ---: | ---: | --- |
| 65,536 points, radius 0.02, K=50 | 0.775476 | 206,168 | 0.011538 | exact refine 0.005389s; row download 0.001384s; prepare 0.003649s |
| 262,144 points, radius 0.02, K=50 | 3.329380 | 2,510,258 | 0.112743 | exact refine 0.080799s; row download 0.010866s; prepare 0.016254s |

The telemetry is intentionally narrow, but the signal is strong: the measured native count/write phases are not the main 262k wall-time cost. The next v2.2 improvement should focus on reusable prepared inputs and lower-overhead row continuation / normalization, because Python-side loading, packing, row view setup, and host exact-normalization dominate the end-to-end harness wall time.

## Claim Boundary

This goal authorizes a narrow diagnostic claim: RTDL can now explain where time goes inside the current generic 3D bounded-neighbor primitive. It is not a release claim.

This goal does not authorize:

- RTNN parity;
- a broad RT-core speedup claim;
- a claim that the default path is RT-core accelerated;
- a v2.2 release claim.

## Next Step

Use pod telemetry to decide the next concrete primitive change. The expected next generic primitive remains:

```text
prepared_bounded_neighbor_search_3d
```

The telemetry says the first prepared-handle work should prioritize reusable host/device grid preparation and lower-overhead row continuation / normalization before deeper RT-core experiments. That remains v2.x runtime work, not v3.0 user-defined shader injection.
