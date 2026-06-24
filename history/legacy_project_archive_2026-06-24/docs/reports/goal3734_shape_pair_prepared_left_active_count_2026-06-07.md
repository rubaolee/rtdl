# Goal3734 Shape-Pair Prepared-Left Active Count

Status: implemented and validated on NVIDIA RTX A5000 pod.

## Purpose

Goal3733 moved the RayJoin safe mixed composite bottleneck from line-segment
intersection to the overlay active-count dependency row. The native phase timing
showed the current generic shape-pair device-continuation route already keeps
the relation flags and active-count reduction on the GPU, but each repeated
query still repacks and reuploads the left closed-shape payload.

This goal adds a generic prepared-left shape-pair relation active-count route.
The native engine still sees only shape-pair relation flags and active-count
reduction. RayJoin overlay interpretation remains in the Python benchmark app.

## Changes

| Area | Change |
| --- | --- |
| Native OptiX workload | Added `PreparedShapePairRelationLeftSet`, storing left polygon refs, vertices, bounds, and max-edge launch stride in CUDA-resident buffers. |
| Native C ABI | Added `rtdl_optix_prepare_shape_pair_relation_left_set`, `rtdl_optix_count_prepared_shape_pair_relation_active_device_prepared_left`, and `rtdl_optix_destroy_prepared_shape_pair_relation_left_set`. |
| Python runtime | Added `PreparedOptixShapePairRelationLeftSet`, `prepare_shape_pair_relation_left_set_optix(...)`, and `PreparedOptixShapePairRelation.count_active_device_continuation_prepared_left(...)`. |
| RayJoin app | The overlay active-count packed-left wrapper now prepares the generic left shape set once and the default device-continuation route calls the prepared-left active-count method. |
| Timing metadata | The shape-pair timing decoder now labels native mode `5` as `active_count_device_continuation_prepared_left`. |

## Expected Effect

This moves left preparation and left upload out of the hot repeated query path. On the
last A5000 probe, the old route reported about:

- left upload: `0.001875s`
- traversal: `0.000943s`
- active scan: `0.000457s`

The new route is expected to keep traversal and active scan similar while
driving hot-query `left_prepare` and `left_upload` to `0.0` in the last-phase
timing metadata. It is not expected to solve the remaining traversal or active
scan cost.

## Boundary

This does not authorize any public RayJoin, paper-reproduction, whole-app,
RT-core, true-zero-copy, release, or broad speedup claim. It is a generic
prepared-payload reuse route for a shape-pair active-count primitive.

## Pod Validation Plan

Run on the A5000 pod after rebuilding `librtdl_optix.so`:

```bash
export PYTHONPATH=src:.
export OPTIX_PREFIX=/root/vendor/optix-sdk
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
export RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so
make build-optix
python -m unittest tests.goal3734_shape_pair_prepared_left_active_count_test
python examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py \
  --workload overlay_seed \
  --execution-route prepared_optix_shape_pair_active_count \
  --dataset public_cdb_4096_chain \
  --result-mode count \
  --repeat 20 \
  --warmup 5
```

The validation should check:

- `row_count` stays stable.
- `native_phase_timings.mode` is `active_count_device_continuation_prepared_left`.
- `native_phase_timings.left_upload == 0.0`.
- `packed_left_reuse.native_prepared_left_set_enabled == true`.
- All claim-boundary flags remain false.

## Pod Validation Result

Artifacts:

- `docs/reports/goal3734_shape_pair_prepared_left_active_count_a5000_overlay_direct_summary.json`
- `docs/reports/goal3734_shape_pair_prepared_left_active_count_a5000_safe_mixed_summary.json`

Environment:

- GPU: NVIDIA RTX A5000
- Commit: `c8f3a67c7e770e1e9a7d684ce4521d6b37c9273b`
- `make build-optix` completed successfully with `OPTIX_PREFIX=/root/vendor/optix-sdk`.
- Focused pod tests passed:
  - `tests.goal3734_shape_pair_prepared_left_active_count_test`
  - `tests.goal3442_shape_pair_active_count_device_continuation_test`
  - `tests.goal3443_spatial_rayjoin_overlay_active_count_device_default_test`

Direct overlay active-count result over the materialized public-CDB 4096-chain
county/soil slice:

| Metric | Value |
| --- | ---: |
| Active relation count | `4,250` |
| Pair count | `15,006,618` |
| Hot median query | `0.0031651603s` |
| Native mode | `active_count_device_continuation_prepared_left` |
| Native left prepare | `0.0s` |
| Native left upload | `0.0s` |
| Native traversal | `0.000959525s` |
| Native active scan | `0.000460326s` |
| Prepared-left set build | `0.3430343568s` |

Safe mixed composite over the same 4096-chain slice:

| Workload | All-CuPy Baseline | Recommended Route | Speedup |
| --- | ---: | ---: | ---: |
| PIP | `0.000885301s` | `0.000885301s` | `1.000x` |
| LSI | `1.266489321s` | `0.000097052s` | `13049.632x` |
| Overlay active-count | `0.165980307s` | `0.003160997s` | `52.509x` |
| Composite sum | `1.433354628s` | `0.004143349s` | `345.941x` |

The overlay route improved from the Goal3733 measured `0.004832825s` class to
`0.003160997s` by removing repeated left-side upload from the hot query. The
remaining overlay cost is traversal plus active scan; this goal does not solve
those parts.

All claim-boundary flags in the direct and composite artifacts remain false.
These measurements are internal engineering evidence and do not authorize a
public RayJoin, paper-reproduction, release, broad RT-core, true-zero-copy, or
whole-app speedup claim.
