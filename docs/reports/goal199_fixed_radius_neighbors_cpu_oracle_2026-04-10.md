# Goal 199: Fixed-Radius Neighbors CPU/Oracle Closure

Date: 2026-04-10
Status: completed

## Result

`fixed_radius_neighbors` now has a fully working correctness-first RTDL path.

Users can now:

- author the workload in the public DSL
- lower it into an execution plan
- execute it through `run_cpu(...)`
- compare it against the Python truth path

This is the first complete RTDL runtime closure for the workload. Performance
and accelerated backend closure are still later goals.

## What changed

### Lowering support

Updated:

- [lowering.py](../../src/rtdsl/lowering.py)

The workload now lowers into a `native_loop` execution plan with explicit
`query_id`, `neighbor_id`, and `distance` emit fields.

### Native oracle runtime

Updated:

- [oracle_runtime.py](../../src/rtdsl/oracle_runtime.py)
- [rtdl_oracle_abi.h](../../src/native/oracle/rtdl_oracle_abi.h)
- [rtdl_oracle_api.cpp](../../src/native/oracle/rtdl_oracle_api.cpp)

Added native support for:

- query-point / search-point decoding
- inclusive radius filtering
- per-query distance ordering
- `neighbor_id` tie-break
- `k_max` truncation after ordering

### Oracle rebuild hardening

Updated:

- [oracle_runtime.py](../../src/rtdsl/oracle_runtime.py)

The native oracle library rebuild check now watches the modular oracle source
tree instead of only the top-level shim file. This avoids stale-library misses
after modular oracle edits.

### Tests

Added:

- [goal199_fixed_radius_neighbors_cpu_oracle_test.py](../../tests/goal199_fixed_radius_neighbors_cpu_oracle_test.py)

Updated:

- [goal40_native_oracle_test.py](../../tests/goal40_native_oracle_test.py)
- [test_core_quality.py](../../tests/test_core_quality.py)
- [llm_authoring_guide.md](../rtdl/llm_authoring_guide.md)
- [dsl_reference.md](../rtdl/dsl_reference.md)
- [fixed_radius_neighbors/README.md](../features/fixed_radius_neighbors/README.md)

## Verification

Ran:

- `PYTHONPATH=src:. python3 -m unittest tests.goal199_fixed_radius_neighbors_cpu_oracle_test tests.goal40_native_oracle_test tests.goal198_fixed_radius_neighbors_truth_path_test tests.test_core_quality`
  - `Ran 111 tests`
  - `OK`
- `python3 -m compileall src/rtdsl docs/rtdl examples/reference tests/goal199_fixed_radius_neighbors_cpu_oracle_test.py`
  - `OK`

## Acceptance summary

Goal 199 is complete:

- lowering support: yes
- native CPU/oracle support: yes
- authored-case parity: yes
- fixture-case parity: yes
- baseline-runner `cpu` support: yes
- Embree and beyond: intentionally no
