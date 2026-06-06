# Goal3660 RayJoin PIP Batch Executor Throughput

Date: 2026-06-06

Status: internal v2.9 performance improvement; not release or public speedup
authorization.

## Purpose

Goal3658 made the one-shot PIP scalar-count route much better by tightening the
generic point/closed-shape device predicate and validating every sample against
the exact prepared count. That route became faster than the prior project-owned
CuPy dense baseline, but it still trailed RayJoin `query_exec` query timing.

Goal3660 tests a different contract that matters for batched application use:
repeated PIP count requests over the same prepared point/closed-shape inputs.
The existing generic reusable batch-count executor is wired into the Goal3244
same-slice runner so RTDL can measure batched repeated-request throughput
directly.

## What Changed

| Area | Change |
| --- | --- |
| Spatial RayJoin benchmark app | Added an opt-in batched repeated-request timing path for `device_filtered_prepared_points_validated` PIP counts. |
| Runner | Added `--rtdl-pip-batch-request-count` and `--rtdl-pip-batch-stream-count`. |
| Artifact contract | Records `pip_timing_contract = batched_repeated_request_throughput_not_one_shot_latency`, batch size, stream policy, batch-executor prepare time, per-request timing, and total timed batch duration. |

The implementation remains generic. The native runtime sees prepared
point-probe columns, a prepared closed-shape scene, a reusable generic count
executor, and a stream policy. RayJoin/CDB interpretation remains in the Python
benchmark layer.

## Clean A5000 Evidence

Artifact:

- `docs/reports/goal3660_rayjoin_pip_batch_executor_throughput_a5000/summary.json`

Pod:

- NVIDIA RTX A5000, driver `580.126.09`
- Clean checkout commit `def665eb`
- `source_dirty: []`
- OptiX backend rebuilt with `OPTIX_PREFIX=/root/vendor/optix-sdk`

Command shape:

```bash
python3 scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py \
  --workloads pip \
  --rayjoin-query-exec /root/RayJoin/release/bin/query_exec \
  --rayjoin-data-dir /root/rtdl_goal3595_clean/data/rayjoin_public_cdb \
  --rayjoin-pip-poly1 /root/rtdl_goal3595_clean/data/rayjoin_public_cdb/br_county_start256_count512.cdb \
  --rayjoin-pip-poly2 /root/rtdl_goal3595_clean/data/rayjoin_public_cdb/br_county_start256_count512.cdb \
  --rtdl-pip-dataset /root/rtdl_goal3595_clean/data/rayjoin_public_cdb/br_county_start256_count512.cdb \
  --rayjoin-warmup 100 \
  --rayjoin-repeat 30000 \
  --rayjoin-process-repeats 3 \
  --rtdl-repeat 3 \
  --rtdl-internal-warmup 100 \
  --rtdl-internal-query-repeat 30000 \
  --rtdl-pip-count-mode device_filtered_prepared_points_validated \
  --rtdl-pip-boundary-mode inclusive \
  --rtdl-pip-scalar-count-pipeline \
  --rtdl-pip-device-predicate-eps 1e-9 \
  --rtdl-pip-batch-request-count 100 \
  --rtdl-pip-batch-stream-count auto
```

## Results

| Route | Count | Median ms/request | Median total ms | Notes |
| --- | ---: | ---: | ---: | --- |
| RTDL batched prepared-point executor | 1417 | 0.034225 | 1027.254 | `30000` measured requests, `100` requests per batch, `auto` stream policy, exact validation passed. |
| RayJoin `query_exec` reported PIP query | n/a | 0.192133 | process wall median 6721.356 | Upstream binary does not expose positive-assignment count. |
| Goal3658 RTDL one-shot/sequential repeated route | 1417 | 0.283574 | 8536.058 | Same tuned predicate, no batch executor. |
| Goal3595 CuPy dense baseline | 1417 | 0.437917 | 87.362 over 200 repeats | Prior project-owned CUDA-core scalar-count baseline. |

Ratios:

- RTDL batch executor vs RayJoin reported query timing: `0.178x` RTDL/RayJoin
  per request.
- RTDL batch executor total vs RayJoin process wall total: about `0.153x`
  RTDL/RayJoin total.
- RTDL batch executor vs Goal3658 sequential RTDL route: about `0.121x`, or
  `8.28x` faster per request.
- RTDL batch executor vs Goal3595 CuPy dense baseline: about `0.078x`, or
  `12.79x` faster per request.

## Interpretation

This is the strongest current RTDL PIP throughput evidence, but it has a
narrow contract:

- It is batched repeated-request throughput over resident prepared inputs.
- It is not one-shot latency.
- It is not a drop-in replacement for every RayJoin `query_exec` timing.
- It does not prove full RayJoin paper reproduction.

The gain comes from using a reusable generic prepared point/closed-shape count
executor. Instead of paying a Python/native boundary, launch setup, and
synchronization cost for every request, the batch executor runs groups of
prepared requests with its owned stream pool and returns one count per request.
The hot path still avoids candidate-row materialization and host exact
refinement; every measured sample is validated against the exact prepared count.

## Current RayJoin Reading After Goal3660

| Contract | Best current RTDL route | Reading |
| --- | --- | --- |
| LSI visible segment-pair count | RTDL/OptiX prepared-left generic segment-pair route | Strong one-shot and long-run evidence versus RayJoin. |
| PIP positive assignment count, one-shot/sequential repeated | RTDL/OptiX tuned validated device count | Faster than prior project-owned CuPy dense baseline, still slower than RayJoin query timing. |
| PIP positive assignment count, batched repeated requests | RTDL/OptiX reusable prepared-point batch count executor | Strong throughput evidence: `0.034225ms/request`, but explicitly not one-shot latency. |
| Overlay active pair-dependency count | RTDL/OptiX prepared shape-pair active count | Strong contract evidence, still not full polygon overlay materialization. |

## Boundary

Goal3660 does not authorize:

- public v2.9 release wording;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app RayJoin speedup wording;
- RayJoin paper reproduction wording;
- RTDL-beats-RayJoin one-shot wording;
- true zero-copy wording;
- automatic partner/backend selection;
- app-specific native-engine logic.

## Validation

Local:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3244_rayjoin_same_slice_repeated_count_runner_test
py -3 -m py_compile scripts\goal3244_rayjoin_same_slice_repeated_count_runner.py examples\v2_0\research_benchmarks\spatial_rayjoin\rtdl_rayjoin_v2_spatial_join_app.py
```

Pod:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal3244_rayjoin_same_slice_repeated_count_runner_test
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk -j2
```
