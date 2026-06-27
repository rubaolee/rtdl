# Goal 204: KNN Rows Truth Path

Date: 2026-04-10
Status: completed

## Result

`knn_rows` now has a real Python truth path.

Goal 204 adds:

- a pure-Python reference implementation
- `run_cpu_python_reference(...)` support
- deterministic authored and fixture cases
- a tiny public Natural Earth-style fixture and loader
- baseline-runner support for `cpu_python_reference`

Native CPU/oracle and Embree support are still intentionally deferred.

## What changed

### Reference execution

Added:

- [reference.py](/Users/rl2025/rtdl_python_only/src/rtdsl/reference.py)

New function:

- `knn_rows_cpu(query_points, search_points, *, k)`

Semantics now proven in code:

- per-query sort order:
  - ascending distance
  - then ascending `neighbor_id`
- 1-based `neighbor_rank`
- emit only the first `k` rows per query after ordering
- emitted row fields:
  - `query_id`
  - `neighbor_id`
  - `distance`
  - `neighbor_rank`

### Runtime truth path

Updated:

- [runtime.py](/Users/rl2025/rtdl_python_only/src/rtdsl/runtime.py)

`run_cpu_python_reference(...)` now dispatches the new predicate without
pretending that native runtime support exists.

### Baseline contracts and runner

Updated:

- [baseline_contracts.py](/Users/rl2025/rtdl_python_only/src/rtdsl/baseline_contracts.py)
- [baseline_runner.py](/Users/rl2025/rtdl_python_only/src/rtdsl/baseline_runner.py)

The baseline layer now:

- recognizes `knn_rows`
- exposes representative datasets
- supports `run_baseline_case(..., backend="cpu_python_reference")`

### Reference kernels and fixture builders

Added:

- [rtdl_knn_rows_reference.py](/Users/rl2025/rtdl_python_only/examples/reference/rtdl_knn_rows_reference.py)

New builders:

- authored case with deterministic ranking and tie order
- county-derived fixture case
- tiny public Natural Earth-style populated-places case

## Verification

Ran:

- `PYTHONPATH=src:. python3 -m unittest tests.goal204_knn_rows_truth_path_test tests.baseline_contracts_test`
- `python3 -m compileall src/rtdsl examples/reference tests/goal204_knn_rows_truth_path_test.py`

## Acceptance summary

Goal 204 is complete:

- Python truth path: yes
- runtime reference dispatch: yes
- deterministic authored case: yes
- deterministic fixture case: yes
- tiny public fixture and loader: yes
- native/backend closure: intentionally no
