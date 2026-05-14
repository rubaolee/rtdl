# Goal2003 - CuPy RawKernel Exact Witness Filter

Status: pass-with-boundary

Date: 2026-05-14

## Scope

Goal2003 moves the segment/polygon hit-count exact-filter step from host Python
to the CuPy partner layer. The native OptiX engine remains app-agnostic: it
still emits only generic ray/primitive candidate witness pairs. The CuPy partner
adapter now applies an app-side RawKernel exact segment/triangle filter on the
GPU, then uses the existing generic `partner_group_count_unique_pairs_by_key`
reduction to produce per-segment hit-count columns.

The row adapter remains host-materialized because returning Python rows is a
host contract. This goal only upgrades the hit-count column path:

`rtdsl.segment_polygon_hitcount_optix_partner_device_count_columns(..., partner="cupy")`

## Contract

For CuPy, the hit-count path now records:

- `native_engine_row_contract: generic_ray_primitive_candidate_witness_pairs`
- `app_exact_filter: cupy_rawkernel_segment_triangle_filter_from_generic_witness_candidates`
- `app_exact_filter_device_materialization: true`
- `app_count_materialization: partner_gpu_unique_pair_counts_from_cupy_exact_filter`
- `app_count_host_materialization: false`
- `native_exact_row_semantics_authorized: false`
- `app_exact_row_semantics_authorized: true`
- `whole_app_true_zero_copy_authorized: true`
- `v2_0_release_authorized: false`

For Torch and fake test runtimes, the existing host exact filter remains in
place. That path still records `whole_app_true_zero_copy_authorized: false`.

## Pod Evidence

Pod:

- SSH: `root@69.30.85.251 -p 22085`
- GPU: `NVIDIA RTX A5000`
- Driver: `570.211.01`
- CUDA user space: `/usr/local/cuda-12.8`
- OptiX library: `/root/rtdl_goal2000/build/librtdl_optix.so`

Artifact:

`docs/reports/goal2003_pod_smoke/segment_polygon_cupy_rawkernel_hitcount_perf.json`

The artifact compares the v2.0 CuPy exact hit-count column path against the
v1.8 native OptiX row baseline using the same synthetic segment/polygon
contract. All output counts are exact:

- count 256: all hit counts equal `1`
- count 2048: all hit counts equal `1`
- count 8192: all hit counts equal `1`

Timing:

| count | v1.8 median (s) | v2.0 CuPy median (s) | ratio |
| ---: | ---: | ---: | ---: |
| 256 | `0.0015426017343997955` | `0.0034902114421129227` | `2.26254863084989x` |
| 2048 | `0.024160467088222504` | `0.0034985262900590897` | `0.14480375223227845x` |
| 8192 | `0.3330053258687258` | `0.004293236881494522` | `0.012892397051892683x` |

The count-256 row remains slower after warmup because the fixed partner/kernel
launch overhead is larger than the tiny warmed v1.8 native query. The larger
rows are positive evidence. First-call RawKernel compile latency is visible in
the count-256 row (`0.2112438939511776` seconds), so production comparisons
should use warmed timing rows or report compile latency separately.

## Boundary

Accepted:

- native OptiX remains generic and app-agnostic;
- CuPy hit-count exact filtering now stays on device;
- the hit-count column path can honestly mark whole-app true zero-copy for the
  exact-count output path;
- pod parity and timing evidence are available for counts 256, 2048, and 8192.

Still blocked:

- v2.0 release authorization;
- broad RT-core speedup wording;
- small-count speedup wording for this path;
- whole-app claims for Python row materialization paths;
- Torch parity for device-side exact filtering;
- final all-app v2.0 versus v1.8 performance matrix.

## Design Lesson

Goal2003 confirms the emerging v2.0 rule: RTDL native should produce generic
candidate tables, while partner adapters provide reusable GPU-side exact filters
and reductions. That is the general solution. We do not put app-specific
continuations into the engine; we give users a fast, composable partner layer
where app semantics can run without falling back to host Python.
