# Goal 218 Report

## Scope

Implement Vulkan support for `fixed_radius_neighbors`.

## Main Changes

- added `RtdlFixedRadiusNeighborRow` to the Vulkan C ABI
- added `rtdl_vulkan_run_fixed_radius_neighbors(...)`
- added a Vulkan compute shader for `fixed_radius_neighbors`
- added host-side Vulkan compute launch and row extraction
- added Python runtime dispatch and ctypes registration
- added dedicated tests in
  `/Users/rl2025/rtdl_python_only/tests/goal218_fixed_radius_neighbors_vulkan_test.py`

## Validation

Local macOS slice:

- `PYTHONPATH=src:. python3 -m unittest tests.goal218_fixed_radius_neighbors_vulkan_test tests.rtdsl_vulkan_test`
- result:
  - `Ran 13 tests`
  - `OK (skipped=12)`

Linux host `lestat@192.168.1.20`:

- `cd /home/lestat/work/rtdl_python_only && make build-vulkan`
- `cd /home/lestat/work/rtdl_python_only && PYTHONPATH=src:. python3 -m unittest discover -s tests -p "goal218_fixed_radius_neighbors_vulkan_test.py" -v`
- result:
  - `Ran 8 tests`
  - `OK`

Regression confirmation:

- `rtdsl_vulkan_test.py`
  - `Ran 19 tests`
  - `OK`

## Boundary

- This goal closes Vulkan runnability and correctness for
  `fixed_radius_neighbors`.
- It does not make Vulkan `fixed_radius_neighbors` performance-optimized.
