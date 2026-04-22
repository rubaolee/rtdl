# Goal757 Prepared OptiX Fixed-Radius Count Plan

## Purpose

Improve the NVIDIA OptiX path for fixed-radius apps by adding a prepared OptiX count-threshold handle for 2D fixed-radius queries.

This targets the public outlier-detection and DBSCAN app paths. Those apps already have a true OptiX traversal formulation through `fixed_radius_count_threshold_2d_optix`: search points become padded AABBs, query points shoot orthogonal rays, the custom intersection program performs exact radius checks, and the any-hit program counts accepted hits and terminates when a threshold is reached. The remaining performance problem is that the current OptiX API is one-shot and rebuilds/uploads the search scene every call.

## Scope

Add a prepared OptiX API for:

- building the search-point BVH once;
- reusing device search-point storage and OptiX acceleration structure across repeated query batches;
- returning compact count-threshold rows, not neighbor rows;
- preserving the existing one-shot API.

Target public apps:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_outlier_detection_app.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_dbscan_clustering_app.py`

Target runtime/native files:

- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_prelude.h`
- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_api.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_workloads.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/optix_runtime.py`

## Non-Scope

- Do not rewrite the CUDA KNN or fixed-radius neighbor-row path.
- Do not change default app behavior from full neighbor rows.
- Do not claim RTX RT-core speedup from GTX 1070 evidence.
- Do not implement full DBSCAN clustering on the backend; only the RT-heavy core-point/count-threshold step is in scope.
- Do not implement Hausdorff/ANN/Barnes-Hut in this goal.

## Proposed API

Python runtime:

```python
with rt.prepare_optix_fixed_radius_count_threshold_2d(search_points, max_radius=0.35) as prepared:
    count_rows = prepared.run(query_points, radius=0.35, threshold=3)
```

App-level prepared sessions:

```python
with outlier_app.prepare_session("optix", copies=20000) as session:
    payload = session.run(output_mode="density_summary")

with dbscan_app.prepare_session("optix", copies=20000) as session:
    payload = session.run(output_mode="core_flags")
```

## Expected Native Design

- Prepared handle owns:
  - OptiX context dependency;
  - device search point buffer;
  - search-point AABB buffer;
  - custom primitive GAS;
  - search count;
  - `max_radius`, because the custom-primitive AABBs must be wide enough for
    every run-time radius.
  - original point ids.
- Run call uploads only query points, rejects `radius > max_radius`, allocates
  output rows for query count, launches the existing `__raygen__frn_count_probe`
  pipeline against the prepared GAS, downloads compact count rows, and returns
  an `OptixRowView` or tuple rows.
- Destroy call releases the prepared handle and device memory.

## Tests

Add portable tests that:

- prove the Python prepared API exists and rejects closed handles;
- use mocks when native OptiX is unavailable locally;
- prove outlier and DBSCAN app prepared sessions match existing one-shot summary output;
- prove default full-output behavior remains unchanged.

Add Linux native tests that:

- rebuild OptiX;
- compare one-shot `fixed_radius_count_threshold_2d_optix` vs prepared handle output;
- run outlier and DBSCAN prepared sessions with OptiX.

## Performance Evidence

Run on Linux GTX 1070 for backend behavior evidence:

- one-shot OptiX count-threshold;
- prepared OptiX cold prepare;
- prepared OptiX warm repeated query median;
- app-level outlier density summary;
- app-level DBSCAN core flags.

Report the boundary explicitly: GTX 1070 validates OptiX backend behavior and scene-reuse performance only; it is not RTX RT-core speedup evidence.

## Acceptance Criteria

- Existing one-shot APIs and app CLIs remain compatible.
- Prepared API matches one-shot correctness for fixed-radius count-threshold rows.
- Outlier and DBSCAN prepared sessions match oracle-visible summaries.
- Linux native OptiX validation passes.
- Scaled Linux performance JSON/report shows whether prepared scene reuse reduces repeated query cost.
- 2+ AI consensus for plan and finish.
