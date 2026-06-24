# Goal2249: RayJoin PIP Prepared Closed-Shape Pod Evidence

Status: accepted pending external review.

## Purpose

Goal2248 added a prepared generic closed-shape membership primitive for OptiX:

```text
rtdl_optix_prepare_point_closed_shape_membership_2d
rtdl_optix_run_prepared_point_closed_shape_membership_2d
rtdl_optix_destroy_prepared_point_closed_shape_membership_2d
```

The design removes repeated closed-shape upload/GAS construction from the
same-query RayJoin PIP timing loop while keeping the native ABI app-agnostic:
the engine sees points, closed shapes, and membership rows; the Python RayJoin
harness maps those rows back to `point_id` / `polygon_id` app fields.

## Environment

- Pod SSH: `root@69.30.85.202 -p 22064`
- Pod checkout: `/root/rtdl_goal2198_launcher/rtdl`
- Commit: `9e8c60ef6ae6a1311940b76861fc9a665a52dcc5`
- GPU: NVIDIA RTX A5000, driver `570.211.01`
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
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_goal2198_launcher/rtdl/build/librtdl_optix.so \
  python3 -m unittest \
  tests.goal2248_prepared_closed_shape_membership_test \
  tests.goal2192_rayjoin_same_query_stream_adapter_test \
  tests.goal2241_rayjoin_same_query_pip_closed_shape_path_test \
  tests.goal2243_rayjoin_pip_closed_shape_path_2ai_consensus_test
Ran 16 tests: OK
```

## Timing Result

Command:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_goal2198_launcher/rtdl/build/librtdl_optix.so \
  python3 scripts/goal2192_rayjoin_same_query_stream_runner.py run-stream \
  --query-stream /root/goal2198_rayjoin_same_query_pod_r6/artifacts/rayjoin_pip_gen100000_stream.json \
  --output /root/goal2248_prepared_closed_shape_pod_clean/rtdl_pip_prepared_closed_shape_same_rayjoin_stream.json \
  --backends optix --reference-backend cpu --warmups 1 --repeats 9
```

Result artifact:
`docs/reports/goal2249_rayjoin_pip_prepared_closed_shape_same_query_pod_2026-05-17.json`

Summary:

```json
{
  "query_count": 100000,
  "row_count": 8686,
  "median_sec": 0.06389576941728592,
  "all_parity_vs_reference": true,
  "implementation_path": "prepared_closed_shape_membership_2d_optix",
  "input_preparation_path": "prepared_shape_scene_and_prepacked_points_once_per_run_stream"
}
```

Goal2245 measured the non-prepared but prepacked generic closed-shape path at
`0.08343074284493923` seconds median on the same query stream. Goal2249
therefore records a same-contract improvement to `0.766x` of that time, or
about 1.31x faster than Goal2245.

## Interpretation

The lesson is the same one RayJoin keeps teaching us: when geometry is stable
across a query stream, the generic RTDL primitive needs a prepared-scene contract,
not just a one-shot helper. This is still app-agnostic because the prepared
object owns only closed-shape acceleration state, not RayJoin logic.

This narrows a concrete performance gap in the RTDL v2.0 RayJoin learner test:
the optimized PIP path now avoids repeated Python packing and repeated native
closed-shape scene preparation inside the measured loop.

## Boundary

This report does not authorize:

- full RayJoin reproduction,
- a claim that RTDL beats RayJoin,
- paper-scale RayJoin speedup claims,
- v2.0 release readiness,
- or broad PIP acceleration claims beyond this exact 100,000-query same-query
  pod artifact.

The remaining RayJoin gap to the paper implementation is expected: RayJoin's
native benchmark reports pure GPU query execution, while this RTDL harness still
returns rows to Python and keeps the public language/runtime boundary visible.
