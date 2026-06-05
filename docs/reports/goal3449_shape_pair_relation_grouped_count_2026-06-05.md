# Goal3449 - Shape-Pair Relation Grouped Count Continuation

## Status

Implemented and pod-validated.

Goal3449 consumes the Goal3447 resident shape-pair relation columns with an already-existing generic device-column grouped-count reducer. This turns the RayJoin overlay path from:

1. generic shape-pair relation flags
2. compact active relation columns

into:

3. compact grouped counts by relation id, still on CUDA

The first app-facing route groups active relation rows by `left_id`, which is the useful RayJoin overlay-seed summary direction, but the runtime method supports both `left` and `right` id axes. The native engine remains app-agnostic: no RayJoin/CDB/overlay-specific native ABI was added.

Because the generic grouped-count reducer uses direct-address id keys, the app wrapper records `id_capacity = max(left_id) + 1` when packing the left shapes. It deliberately does not assume `group_capacity == left_shape_count`, because public CDB ids can be sparse.

## What Changed

Python runtime:

- `OptixShapePairRelationDeviceColumnOutput.grouped_count_by_id_compact_device_columns(...)`
- `grouped_count_by_left_id_compact_device_columns(...)`
- `grouped_count_by_right_id_compact_device_columns(...)`

Benchmark app:

- `PreparedRayJoinOptixShapePairActiveCount.run_packed_left_active_relation_grouped_count_by_left(...)`

Probe:

- `scripts/goal3449_shape_pair_relation_grouped_count_probe.py`

## Claim Boundary

This goal does not authorize:

- v2.8 release
- public speedup wording
- RT-core speedup wording
- true-zero-copy wording
- RayJoin paper reproduction claims
- RTDL-beats-RayJoin claims
- full overlay relation-row, area, or witness completion claims

The intended claim is narrow: generic resident relation columns can feed a generic grouped-count continuation without returning to host materialized relation-row tables.

## Validation

Local validation:

- `py -3 -m py_compile src\rtdsl\optix_runtime.py examples\v2_0\research_benchmarks\spatial_rayjoin\rtdl_rayjoin_v2_spatial_join_app.py scripts\goal3449_shape_pair_relation_grouped_count_probe.py tests\goal3449_shape_pair_relation_grouped_count_test.py`
- `py -3 -m unittest tests.goal3449_shape_pair_relation_grouped_count_test`

Pod validation:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
python scripts/goal3449_shape_pair_relation_grouped_count_probe.py \
  --iterations 4 \
  --output docs/reports/goal3449_shape_pair_relation_grouped_count_pod_2026-06-05.json
```

Pod artifact:

- `docs/reports/goal3449_shape_pair_relation_grouped_count_pod_2026-06-05.json`
- `docs/reports/goal3449_shape_pair_relation_grouped_count_pod_2026-06-05.stdout`

Hardware/result summary:

- Commit: `f52dad39`
- GPU: NVIDIA RTX A5000, driver `580.126.09`
- Dataset: `br_county.cdb` joined against `br_county_start256_count1024.cdb`
- Left/right shapes: `15700 / 949`
- Left id capacity: `16483`
- Active relation count: `4543`
- Compact grouped left-id rows: `1261`
- Counts matched for all four iterations:
  - host active count: `[4543, 4543, 4543, 4543]`
  - grouped count sum: `[4543, 4543, 4543, 4543]`
- Median host active-count time: `0.14792247023433447s`
- Median relation-column plus grouped-count time: `0.004763435106724501s`
- Median grouped-count reduction-only time: `0.00022551091387867928s`
- Median speedup versus host active-count route: `31.698682479082052x`
- First iteration was a warmup outlier (`0.664122230373323s` total), so this report treats the median and per-iteration output as internal engineering evidence rather than public speedup wording.
- Grouped-count output stayed device-resident, relation-column native phase mode was `active_relation_device_columns`, and all claim-boundary flags remained false.

## Remaining Work

Goal3449 still does not produce full overlay relation rows or exact overlay area. The next useful step is a bounded witness/area continuation over active relation columns, or a generic row-stream continuation that can keep richer relation outputs resident.
