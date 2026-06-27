# Goal 315 Report: Vulkan 3D Nearest-Neighbor Closure

Date:
- `2026-04-12`

Goal:
- close Vulkan support for the `v0.5` 3D point nearest-neighbor line

Scope:
- native Vulkan ABI
- Python Vulkan runtime
- focused 3D point parity tests
- Linux probe validation only

Implemented files:
- `src/native/vulkan/rtdl_vulkan_prelude.h`
- `src/native/vulkan/rtdl_vulkan_api.cpp`
- `src/native/vulkan/rtdl_vulkan_core.cpp`
- `src/rtdsl/vulkan_runtime.py`
- `tests/goal261_v0_5_native_3d_point_contract_test.py`
- `tests/goal315_v0_5_vulkan_3d_nn_test.py`

What changed:
- added `RtdlPoint3D` to the Vulkan public ABI
- added Vulkan 3D C exports for:
  - `rtdl_vulkan_run_fixed_radius_neighbors_3d(...)`
  - `rtdl_vulkan_run_knn_rows_3d(...)`
- added native 3D Vulkan compute kernels for:
  - fixed-radius neighbors
  - KNN rows
- updated the Python Vulkan runtime to:
  - accept `Points3D`
  - dispatch to optional 3D Vulkan exports when present
  - support `bounded_knn_rows` honestly through fixed-radius rows plus
    Python-side ranking
- replaced the old Vulkan 3D rejection contract with real 3D packing support

Important honesty boundary:
- this goal closes Vulkan 3D point NN capability only
- it does not claim large-scale Vulkan performance closure by itself
- it does not claim Windows or macOS Vulkan validation
- it does not change the existing platform priority:
  - Linux is the real Vulkan validation host

Linux validation host:
- `lestat-lx1`
- isolated probe tree:
  - `/home/lestat/work/rtdl_v05_vulkan_probe`

Linux validation evidence:
- Vulkan library built successfully:
  - `make build-vulkan`
- runtime version check succeeded:
  - `rt.vulkan_version() == (0, 1, 0)`
- focused 3D Vulkan tests passed:
  - `PYTHONPATH=src:. python3 -m unittest tests.goal315_v0_5_vulkan_3d_nn_test`
  - `Ran 4 tests`
  - `OK`
- legacy and new Vulkan tests passed together:
  - `PYTHONPATH=src:. python3 -m unittest tests.goal218_fixed_radius_neighbors_vulkan_test tests.goal219_knn_rows_vulkan_test tests.goal315_v0_5_vulkan_3d_nn_test`
  - `Ran 18 tests`
  - `OK`

Local non-Vulkan validation on macOS:
- `python3 -m unittest tests.goal261_v0_5_native_3d_point_contract_test`
  - `Ran 5 tests`
  - `OK`
- `python3 -m unittest tests.claude_v0_5_full_review_test`
  - `Ran 112 tests`
  - `OK`

Result:
- Vulkan now supports the 3D point nearest-neighbor workload trio on Linux:
  - `fixed_radius_neighbors`
  - `bounded_knn_rows`
  - `knn_rows`
- the Vulkan runtime no longer needs to reject 3D point nearest-neighbor
  payloads in prepared execution
- focused row parity to the Python truth path is proven on the Linux Vulkan host

Conclusion:
- Goal 315 is technically closed pending saved review
