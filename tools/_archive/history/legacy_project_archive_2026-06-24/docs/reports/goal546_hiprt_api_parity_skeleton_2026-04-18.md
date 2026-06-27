# Goal 546: HIPRT API Parity Skeleton

Date: 2026-04-18
Status: accepted with 2-AI consensus

## Purpose

Goal 546 adds the v0.9 HIPRT API parity skeleton.

The intent is not to pretend HIPRT already supports every peer workload. The
intent is to make `run_hiprt(...)` and `prepare_hiprt(...)` recognize the same
peer-backend predicate family and reject unimplemented workloads explicitly with
`NotImplementedError`, before backend loading and without CPU fallback.

This gives v0.9 a safe public/API foundation for implementing workload families
one by one.

## Files Changed

- `/Users/rl2025/rtdl_python_only/src/rtdsl/hiprt_runtime.py`
- `/Users/rl2025/rtdl_python_only/tests/goal543_hiprt_dispatch_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal546_hiprt_api_parity_skeleton_test.py`

## Implemented Behavior

`src/rtdsl/hiprt_runtime.py` now defines:

- `_HIPRT_PEER_PREDICATES`
- `_HIPRT_IMPLEMENTED_PREDICATES`
- `_HIPRT_GOAL_BY_PREDICATE`
- `_unsupported_hiprt_peer_workload(...)`

The recognized peer predicate set is:

- `segment_intersection`
- `point_in_polygon`
- `overlay_compose`
- `ray_triangle_hit_count`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `point_nearest_segment`
- `fixed_radius_neighbors`
- `bounded_knn_rows`
- `knn_rows`
- `bfs_discover`
- `triangle_match`
- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

Currently implemented remains:

- Ray3D/Triangle3D `ray_triangle_hit_count`

Everything else is rejected with a message that:

- names the predicate;
- states the implementation goal that owns it;
- states that no CPU fallback is used.

2D `ray_triangle_hit_count` is also rejected with `NotImplementedError` because
only Ray3D/Triangle3D is implemented today.

## Local Validation

Command:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest \
  tests.goal543_hiprt_dispatch_test \
  tests.goal544_hiprt_docs_examples_test \
  tests.goal546_hiprt_api_parity_skeleton_test
```

Result:

- `Ran 11 tests`
- `OK (skipped=2)`

## Linux Validation

Fresh sync target:

- `/tmp/rtdl_goal546_hiprt_api_skeleton`

Command:

```bash
cd /tmp/rtdl_goal546_hiprt_api_skeleton
HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
make build-hiprt HIPRT_PREFIX=$HIPRT_PREFIX
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
export LD_LIBRARY_PATH=$HIPRT_PREFIX/hiprt/linux64:${LD_LIBRARY_PATH:-}
PYTHONPATH=src:. python3 -m unittest \
  tests.goal540_hiprt_probe_test \
  tests.goal541_hiprt_ray_hitcount_test \
  tests.goal543_hiprt_dispatch_test \
  tests.goal544_hiprt_docs_examples_test \
  tests.goal546_hiprt_api_parity_skeleton_test
```

Result:

- `make build-hiprt` succeeded and produced `build/librtdl_hiprt.so`
- `Ran 16 tests`
- `OK`

The Linux run confirms the skeleton did not break the existing real HIPRT
probe, one-shot, prepared, dispatch, or example paths.

## Consensus

- Codex: ACCEPT
- Claude: ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal546_external_review_2026-04-18.md`

## Codex Review

Codex accepts Goal 546 because:

- it creates an honest API-parity skeleton instead of silent fallback;
- unimplemented peer workloads fail before backend loading;
- current Ray3D/Triangle3D HIPRT behavior remains working;
- local and Linux validation passed.
