# Goal2245: RayJoin PIP Closed-Shape Prepack Pod Evidence

Status: accepted with boundary.

## Purpose

Goal2241 routed RayJoin same-query PIP/OptiX through the generic
`closed_shape_membership_2d_optix` primitive. The first pod timing exposed a
harness mistake: repeated Python packing of 100,000 points and the closed-shape
set dominated timing. Goal2243 fixed the runner to prepack PIP points and
shapes once per `run-stream` invocation. Goal2245 records the clean pushed-commit
pod timing for that corrected path.

## Environment

- Pod SSH: `root@69.30.85.202 -p 22064`
- Pod checkout: `/root/rtdl_goal2198_launcher/rtdl`
- Commit: `f0e2583019c62326a28ce59cbedc3d59ea2dbdcb`
- OptiX SDK: `/root/vendor/optix-sdk`
- CUDA prefix: `/usr/local/cuda-12.8`
- Query stream:
  `/root/goal2198_rayjoin_same_query_pod_r6/artifacts/rayjoin_pip_gen100000_stream.json`

## Validation

The pod was reset to `origin/main`, rebuilt, and tested:

```text
git fetch origin main
git reset --hard origin/main
timeout 600 make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.8
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2192_rayjoin_same_query_stream_adapter_test \
  tests.goal2241_rayjoin_same_query_pip_closed_shape_path_test \
  tests.goal2243_rayjoin_pip_closed_shape_path_2ai_consensus_test
Ran 13 tests: OK
```

## Timing Result

Command:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_goal2198_launcher/rtdl/build/librtdl_optix.so \
  python3 scripts/goal2192_rayjoin_same_query_stream_runner.py run-stream \
  --query-stream /root/goal2198_rayjoin_same_query_pod_r6/artifacts/rayjoin_pip_gen100000_stream.json \
  --output /root/goal2244_rayjoin_pip_closed_shape_prepack_pod/rtdl_pip_closed_shape_prepack_same_rayjoin_stream.json \
  --backends optix --reference-backend cpu --warmups 1 --repeats 9
```

Result artifact:
`docs/reports/goal2245_rayjoin_pip_closed_shape_prepack_same_query_pod_2026-05-17.json`

Summary:

```json
{
  "query_count": 100000,
  "row_count": 8686,
  "median_sec": 0.08343074284493923,
  "all_parity_vs_reference": true,
  "implementation_path": "closed_shape_membership_2d_optix",
  "input_preparation_path": "prepacked_points_and_shapes_once_per_run_stream"
}
```

## Interpretation

This closes the immediate design problem found after Goal2241. With repeated
Python packing removed from the measured loop, the generic closed-shape
membership path returns to the same fast class as the prior optimized PIP path
while keeping the public primitive vocabulary app-agnostic.

The result is strong evidence for the design direction:

- native engine: closed-shape membership,
- Python app harness: map `shape_id`/`membership` into RayJoin
  `polygon_id`/`contains`,
- performance harness: prepack stable inputs once, then time primitive calls.

## Boundary

This report does not authorize:

- full RayJoin reproduction,
- a claim that RTDL beats RayJoin,
- paper-scale speedup claims,
- v2.0 release readiness,
- or broad PIP acceleration claims beyond this same-query 100,000-query pod
  evidence.
