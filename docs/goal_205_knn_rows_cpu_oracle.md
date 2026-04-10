# Goal 205: KNN Rows CPU/Oracle Closure

## Objective

Close the first correctness-complete native execution path for `knn_rows` by extending the RTDL CPU/oracle runtime, preserving the frozen Goal 202 contract and matching the Goal 204 Python truth path exactly.

## Scope

- Add native oracle ABI support for `knn_rows`.
- Add Python ctypes/runtime glue for `knn_rows`.
- Ensure `rt.run_cpu(...)` executes `knn_rows` through the native oracle path.
- Prove parity against the Python truth path on authored and fixture cases.
- Extend the baseline runner CPU backend coverage to `knn_rows`.

## Non-Goals

- Embree/GPU support.
- Performance claims.
- External baseline expansion beyond the already-closed `fixed_radius_neighbors` line.

## Acceptance

- `rt.run_cpu(knn_rows_reference, ...)` works end-to-end through the native oracle path.
- Native oracle rows match the Python truth path for authored and fixture cases.
- Ordering and `neighbor_rank` semantics match the frozen Goal 202 contract.
- Baseline runner CPU backend supports `knn_rows`.
- Bounded tests pass and the result is reviewed under the current Codex + Gemini bar.
