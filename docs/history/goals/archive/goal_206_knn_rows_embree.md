# Goal 206: KNN Rows Embree Closure

## Objective

Close the first accelerated backend for `knn_rows` by extending the Embree runtime while preserving the Goal 202 contract and Goal 205 CPU/oracle semantics.

## Scope

- Add Embree native/runtime support for `knn_rows`.
- Support both normal and raw Embree result modes.
- Prove parity against the Python truth path and CPU/oracle path on authored and fixture cases.
- Extend the baseline runner Embree backend coverage to `knn_rows`.

## Acceptance

- `rt.run_embree(knn_rows_reference, ...)` works end-to-end.
- Embree rows match Python truth-path semantics, including `neighbor_rank`.
- Raw mode exposes the expected row fields.
- Baseline runner Embree backend supports `knn_rows`.
