# Goal2233: Prepared Ray/Segment Group Count

Status: implemented and validated on the RTX pod; pending external review.

## Purpose

Goal2229 proved that `rtdl_optix_run_ray_segment_group_count_2d` is a correct,
app-agnostic primitive for grouped ray/segment intersection counts. A first
RayJoin-style probe then exposed the performance problem:

- dataset: RayJoin CDB boundary file with 15,700 groups and 341,048 segments
- query batch: 10,000 point-to-upward-ray probes
- optimized legacy RTDL PIP path: 0.036533 seconds median
- generic Goal2229 group-count path: 1.476056 seconds median
- ratio: 40.40x slower
- correctness: parity matched exactly, with 879 positive memberships
- intermediate output: 264,766 group-count rows

The primitive was right, but it rebuilt the same large segment scene for every
query batch and then emitted a much wider grouped row stream than the final PIP
answer needed.

Goal2233 fixes the reusable-scene part without changing the public app boundary:
the caller can prepare the segment set and its group-id mapping once, then run
many ray batches against the prepared OptiX scene.

## New ABI

The native OptiX backend now exposes:

- `rtdl_optix_prepare_ray_segment_group_count_2d`
- `rtdl_optix_run_prepared_ray_segment_group_count_2d`
- `rtdl_optix_destroy_prepared_ray_segment_group_count_2d`

The prepared object stores:

- the existing generic prepared segment-pair acceleration structure,
- the app-agnostic `segment_id -> group_id` mapping supplied by the caller.

Each `run` call converts finite `RtdlRay2D` records into probe segments, reuses
the prepared target segment scene, and finalizes count/parity rows keyed by
`(ray_id, group_id)`.

## Python Surface

`src/rtdsl/optix_runtime.py` now provides:

- `PreparedOptixRaySegmentGroupCount2D`
- `prepare_ray_segment_group_count_2d_optix(segments, segment_group_ids)`

The Python object is a context manager and releases the native prepared handle
through `rtdl_optix_destroy_prepared_ray_segment_group_count_2d`.

## Boundary

This goal does not authorize:

- a RayJoin speedup claim,
- a PIP speedup claim,
- a whole-app v2.0 speedup claim,
- a claim that grouped reductions are device-resident,
- a claim that the RayJoin reproduction project is finished.

It removes repeated scene-build overhead for static segment sets. It does not
solve the second major problem from the probe: the current implementation still
materializes grouped count rows and performs grouped aggregation on the host.
The next generic performance target remains a device-resident grouped reduction,
bounded accumulator, or streaming positive-output contract.

## App-Agnostic Check

The new API uses only generic RTDL terms:

- rays
- segments
- group ids
- counts
- parity
- prepared handle

It does not introduce RayJoin, PIP, polygon, map, county, spatial-join, or
dataset-specific vocabulary into the engine ABI.

## Validation Plan

Local:

```text
$env:PYTHONPATH='src;.'; py -3 -m py_compile src\rtdsl\optix_runtime.py
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal2229_ray_segment_group_count_primitive_test \
  tests.goal2231_ray_segment_group_count_2ai_consensus_test \
  tests.goal2233_prepared_ray_segment_group_count_test
```

Pod:

```text
git fetch origin main
git reset --hard origin/main
git apply /root/goal2233.patch
timeout 600 make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.8
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2229_ray_segment_group_count_primitive_test \
  tests.goal2231_ray_segment_group_count_2ai_consensus_test \
  tests.goal2233_prepared_ray_segment_group_count_test
```

Then run a small prepared functional probe and rerun the 10,000-query
RayJoin-style same-query probe with the prepared API. The expected first-order
improvement is removing repeated target-segment scene construction; if output
materialization remains dominant, the report must say so plainly.

## Validation Executed

Local Windows:

```text
$env:PYTHONPATH='src;.'; py -3 -m py_compile src\rtdsl\optix_runtime.py src\rtdsl\__init__.py
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal2229_ray_segment_group_count_primitive_test \
  tests.goal2231_ray_segment_group_count_2ai_consensus_test \
  tests.goal2233_prepared_ray_segment_group_count_test
Ran 11 tests: OK
```

RTX pod:

- SSH: `root@69.30.85.202 -p 22064`
- Pod checkout: `/root/rtdl_goal2198_launcher/rtdl`
- Base commit: `53ccecb9`
- OptiX SDK: `/root/vendor/optix-sdk`
- CUDA prefix: `/usr/local/cuda-12.8`

```text
git fetch origin main
git reset --hard origin/main
git apply /root/goal2233_mod.patch
timeout 600 make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.8
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2229_ray_segment_group_count_primitive_test \
  tests.goal2231_ray_segment_group_count_2ai_consensus_test \
  tests.goal2233_prepared_ray_segment_group_count_test
Ran 11 tests: OK
```

Functional prepared probe:

```json
[
  {"group_id": 7, "hit_count": 2, "parity": 0, "ray_id": 1},
  {"group_id": 8, "hit_count": 1, "parity": 1, "ray_id": 1}
]
```

The prepared result matched both the exact expected rows and the unprepared
Goal2229 function.

## RayJoin-Style Timing Probe

Command:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_goal2198_launcher/rtdl/build/librtdl_optix.so \
  N=10000 REPEATS=3 timeout 420 python3 /root/goal2233_prepared_rayjoin_probe.py
```

Observed payload:

```json
{
  "limit": 10000,
  "new_count_rows": 264766,
  "new_positive_rows": 879,
  "new_prepared_median_sec": 0.8209122363477945,
  "new_prepared_over_old_ratio": 20.642437294210346,
  "old_median_sec": 0.03976818360388279,
  "old_positive_rows": 879,
  "parity_match": true,
  "prepare_sec": 1.0061612650752068,
  "repeats": 3
}
```

Goal2233 reduced the generic path from the earlier unprepared 1.476056-second
median to 0.820912 seconds, about a 1.80x improvement. Correctness remained
exact against the optimized legacy RTDL PIP path.

The performance conclusion is still negative for RayJoin-style PIP: the generic
prepared path is 20.64x slower than the current optimized positive-output PIP
path on this 10,000-query probe. Scene reuse helps, but the remaining bottleneck
is the grouped-output contract. The primitive still materializes 264,766
`(ray_id, group_id, hit_count, parity)` rows to represent 879 positive
memberships.

## Next Engineering Target

The next generic primitive should not be another app-specific PIP path. It
should keep the app-agnostic engine boundary but change the output mechanics:

- device-resident grouped parity/count reduction,
- bounded or streaming positive-output rows,
- or a compact caller-selected predicate over grouped counts.

The old optimized path wins because it emits only positive rows after an
on-device candidate/predicate stage. Goal2233 proves that prepared scene reuse is
necessary but not sufficient.
