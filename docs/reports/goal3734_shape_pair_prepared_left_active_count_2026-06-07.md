# Goal3734 Shape-Pair Prepared-Left Active Count

Status: implemented locally; pod validation pending.

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
