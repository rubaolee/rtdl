# Goal 198: Fixed-Radius Neighbors Truth Path

Date: 2026-04-10
Status: completed

## Result

`fixed_radius_neighbors` now has a real Python truth path.

Goal 198 adds:

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

- `fixed_radius_neighbors_cpu(query_points, search_points, *, radius, k_max)`

Semantics now proven in code:

- inclusive radius: `distance <= radius`
- per-query sort order:
  - ascending distance
  - then ascending `neighbor_id`
- truncation after ordering to `k_max`
- emitted row fields:
  - `query_id`
  - `neighbor_id`
  - `distance`

### Runtime truth path

Updated:

- [runtime.py](/Users/rl2025/rtdl_python_only/src/rtdsl/runtime.py)

`run_cpu_python_reference(...)` now dispatches the new predicate without
pretending that lowered or native runtime support exists.

### Baseline contracts and runner

Updated:

- [baseline_contracts.py](/Users/rl2025/rtdl_python_only/src/rtdsl/baseline_contracts.py)
- [baseline_runner.py](/Users/rl2025/rtdl_python_only/src/rtdsl/baseline_runner.py)

The baseline layer now:

- recognizes `fixed_radius_neighbors`
- exposes representative datasets
- supports `run_baseline_case(..., backend="cpu_python_reference")`

It does not yet advertise `cpu`, `embree`, `optix`, or `vulkan` closure for the
workload.

### Reference kernels and fixture builders

Added:

- [rtdl_fixed_radius_neighbors_reference.py](/Users/rl2025/rtdl_python_only/examples/reference/rtdl_fixed_radius_neighbors_reference.py)

Updated:

- [rtdl_release_reference.py](/Users/rl2025/rtdl_python_only/examples/reference/rtdl_release_reference.py)

New builders:

- authored case with deterministic tie-order and truncation behavior
- county-derived fixture case
- tiny public Natural Earth-style populated-places case

### Public fixture and loader

Added:

- [natural_earth_populated_places_sample.geojson](/Users/rl2025/rtdl_python_only/tests/fixtures/public/natural_earth_populated_places_sample.geojson)

Updated:

- [datasets.py](/Users/rl2025/rtdl_python_only/src/rtdsl/datasets.py)

New loader:

- `load_natural_earth_populated_places_geojson(...)`

This is a bounded local fixture, not a live network download path.

## Verification

Ran:

- `PYTHONPATH=src:. python3 -m unittest tests.goal198_fixed_radius_neighbors_truth_path_test tests.baseline_contracts_test`
  - `Ran 11 tests`
  - `OK`
- `python3 -m compileall src/rtdsl examples/reference tests/goal198_fixed_radius_neighbors_truth_path_test.py`
  - `OK`

## Acceptance summary

Goal 198 is complete:

- Python truth path: yes
- runtime reference dispatch: yes
- deterministic authored case: yes
- deterministic fixture case: yes
- tiny public fixture and loader: yes
- native/backend closure: intentionally no
