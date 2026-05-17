# Goal2235: Prepared Ray/Segment Odd-Parity Output

Status: implemented and validated on the RTX pod; pending external review.

## Purpose

Goal2233 showed that prepared scene reuse is necessary but not sufficient for
RayJoin-style point-location performance. On the 10,000-query pod probe, the
prepared generic path was correct but still returned 264,766 grouped count rows
to express only 879 odd-parity positive memberships.

Goal2235 adds a compact output mode to the same prepared generic primitive:

`rtdl_optix_run_prepared_ray_segment_group_odd_parity_2d`

It reuses the prepared ray/segment group-count scene, computes the same grouped
counts, and returns only rows whose final grouped parity is odd.

## Design

The engine input remains app-agnostic:

- finite 2-D rays,
- finite 2-D segments,
- caller-owned `uint32` segment group ids,
- a prepared native handle.

The output row type remains `RtdlRaySegmentGroupCountRow`, but even-parity
groups are filtered before allocating and copying the result rows.

This is the smallest safe next step after Goal2233:

- it does not rename the engine around RayJoin or PIP,
- it does not add closed-shape semantics to the native ABI,
- it does not change the exact count/parity calculation,
- it lets RayJoin-style callers request the compact positive-membership stream
  they actually need.

## Boundary

This goal does not authorize:

- a v2.0 release claim,
- a whole-app speedup claim,
- a broad RayJoin speedup claim,
- a claim that grouped reductions are fully device-resident,
- a claim that this is a complete RayJoin reproduction.

It is not a RayJoin reproduction claim. It is a generic compact-output mode for
odd parity over grouped counts. The current implementation still uses the segment-pair
intersection pipeline and host grouping; the improvement target is reduced row
materialization and Python conversion pressure.

## Validation Plan

Local:

```text
$env:PYTHONPATH='src;.'; py -3 -m py_compile src\rtdsl\optix_runtime.py
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal2233_prepared_ray_segment_group_count_test \
  tests.goal2235_prepared_ray_segment_odd_parity_test
```

Pod:

```text
timeout 600 make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.8
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2233_prepared_ray_segment_group_count_test \
  tests.goal2235_prepared_ray_segment_odd_parity_test
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_goal2198_launcher/rtdl/build/librtdl_optix.so \
  python3 /root/goal2235_odd_parity_functional_probe.py
```

Then rerun the 10,000-query RayJoin-style probe using
`PreparedOptixRaySegmentGroupCount2D.run_odd_parity`. The expected correctness
target is exact equality with the legacy optimized positive PIP row set. The
expected performance target is lower Python/result-conversion overhead, but the
report must remain honest if segment-pair traversal or host grouping dominates.

## Validation Executed

Local Windows:

```text
$env:PYTHONPATH='src;.'; py -3 -m py_compile src\rtdsl\optix_runtime.py src\rtdsl\__init__.py
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal2233_prepared_ray_segment_group_count_test \
  tests.goal2235_prepared_ray_segment_odd_parity_test
Ran 8 tests: OK
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
git apply /root/goal2235_mod.patch
timeout 600 make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.8
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2229_ray_segment_group_count_primitive_test \
  tests.goal2231_ray_segment_group_count_2ai_consensus_test \
  tests.goal2233_prepared_ray_segment_group_count_test \
  tests.goal2235_prepared_ray_segment_odd_parity_test
Ran 15 tests: OK
```

Functional compact probe:

```json
[
  {"group_id": 8, "hit_count": 1, "parity": 1, "ray_id": 1}
]
```

The compact odd-parity result matched the filtered full-count result exactly.

## RayJoin-Style Timing Probe

Command:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_goal2198_launcher/rtdl/build/librtdl_optix.so \
  N=10000 REPEATS=3 timeout 420 python3 /root/goal2235_odd_parity_rayjoin_probe.py
```

Observed payload:

```json
{
  "count_median_sec": 0.7242644298821688,
  "limit": 10000,
  "odd_median_sec": 0.28234790451824665,
  "odd_over_count_ratio": 0.38984091012750977,
  "odd_over_old_ratio": 8.962546176503611,
  "odd_rows": 879,
  "old_median_sec": 0.031503090634942055,
  "old_positive_rows": 879,
  "parity_match": true,
  "prepare_sec": 0.8857800606638193,
  "repeats": 3
}
```

Goal2235 improves the prepared generic path by cutting the timed run from
0.724264 seconds to 0.282348 seconds on this probe, a 2.56x improvement over
full grouped-count output. The compact path emits exactly 879 rows, matching the
legacy optimized positive PIP row set.

The performance conclusion is still bounded. The compact generic path remains
8.96x slower than the old optimized positive-output PIP path on this probe. The
remaining gap is the traversal/refinement shape: the generic ray/segment path
computes boundary crossings, while the old optimized path uses a closed-shape
candidate/predicate path and emits only positives.

## Next Engineering Target

For RayJoin-style point-location performance, RTDL needs a generic closed-shape
membership or caller-supplied predicate primitive, not another app-named PIP
export. The primitive should remain app-agnostic, but it must avoid reducing
point location through all boundary segment crossings when the app only needs
positive membership rows.
