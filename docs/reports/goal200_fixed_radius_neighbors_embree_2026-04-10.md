# Goal 200: Fixed-Radius Neighbors Embree Closure

Date: 2026-04-10
Status: completed

## Result

`fixed_radius_neighbors` now runs through a true Embree backend path.

This is the first accelerated backend closure for the workload after the
contract, DSL, Python truth path, and native CPU/oracle closure.

Users can now:

- author the workload in the public DSL
- run it through `rt.run_embree(...)`
- compare Embree rows against both:
  - the Python truth path
  - the native CPU/oracle path

## What changed

### Native Embree ABI and runtime

Updated:

- [rtdl_embree_prelude.h](/Users/rl2025/rtdl_python_only/src/native/embree/rtdl_embree_prelude.h)
- [rtdl_embree_scene.cpp](/Users/rl2025/rtdl_python_only/src/native/embree/rtdl_embree_scene.cpp)
- [rtdl_embree_api.cpp](/Users/rl2025/rtdl_python_only/src/native/embree/rtdl_embree_api.cpp)
- [embree_runtime.py](/Users/rl2025/rtdl_python_only/src/rtdsl/embree_runtime.py)

Added native support for:

- build-side point geometry in Embree user geometry
- point-query collection with exact distance filtering
- deterministic row ordering
- `neighbor_id` tie-breaks
- per-query `k_max` truncation
- Embree raw-row exposure for:
  - `query_id`
  - `neighbor_id`
  - `distance`

### Embree rebuild hardening

Updated:

- [embree_runtime.py](/Users/rl2025/rtdl_python_only/src/rtdsl/embree_runtime.py)

The shared-library rebuild check now watches the modular Embree source tree,
not only the top-level `rtdl_embree.cpp` shim. This avoids stale-library misses
after edits under `src/native/embree/`.

### Correctness repair during Goal 200

The first Embree implementation over-emitted duplicate neighbors because the
point-query callback could revisit the same build primitive.

That was fixed during the goal by adding per-query deduplication in the native
query state before row materialization.

### Tests

Added:

- [goal200_fixed_radius_neighbors_embree_test.py](/Users/rl2025/rtdl_python_only/tests/goal200_fixed_radius_neighbors_embree_test.py)

The new test slice covers:

- authored-case Embree parity vs Python truth path
- fixture-case Embree parity vs Python truth path
- out-of-order `query_id` grouping
- raw-mode field exposure
- baseline-runner `embree` support

## Verification

Ran:

- `PYTHONPATH=src:. python3 -m unittest tests.goal200_fixed_radius_neighbors_embree_test tests.goal199_fixed_radius_neighbors_cpu_oracle_test tests.goal198_fixed_radius_neighbors_truth_path_test`
  - `Ran 18 tests`
  - `OK`
- `PYTHONPATH=src:. python3 -m unittest tests.goal40_native_oracle_test tests.cpu_embree_parity_test`
  - `Ran 4 tests`
  - `OK`

## Acceptance summary

Goal 200 is complete:

- Embree support: yes
- authored-case parity: yes
- fixture-case parity: yes
- out-of-order `query_id` grouping: yes
- raw-mode exposure: yes
- rebuild hardening for modular Embree edits: yes

Still intentionally not claimed in this goal:

- external performance win
- OptiX / Vulkan support
- `knn_rows`
