# Goal4604 / V3 M205 Toolchain Support Matrix

Status: `toolchain_support_matrix_checked`

## Conclusion

Goal4604 adds a V3 toolchain support matrix and, when run on the pod, records the live Python/C compiler/make/CMake/pkg-config/NVIDIA/CuPy/Numba/native-library observations needed to interpret current V3 embeddability evidence. This is pod-specific source-tree evidence, not a stable platform support promise, packaged SDK, system install, stable ABI, performance claim, or release authorization.

## Live Probe

- Python: `3.12.3`
- NVIDIA: `550.127.08, NVIDIA RTX 4000 Ada Generation`
- CuPy: `14.1.1`; runtime `12090`
- Numba: `0.60.0`
- NVCC in PATH: `False`

## Native Artifacts

| Artifact | Present |
| --- | --- |
| `rtdl_optix` | `True` |
| `rtdl_embree` | `True` |
| `rtdl_c_api` | `True` |
| `c_api_stage_archive` | `True` |

## Checks

| Check | Passed |
| --- | --- |
| `toolchain_doc_exists_and_sets_boundary` | `True` |
| `learn_readme_links_toolchain_matrix` | `True` |
| `doctor_requires_toolchain_doc` | `True` |
| `doctor_doc_names_toolchain_support` | `True` |
| `v3_current_report_is_present_and_matrix_sized` | `True` |
| `embeddability_delivery_goal4603_accepts` | `True` |
| `python_probe_available` | `True` |
| `cc_available` | `True` |
| `make_available` | `True` |
| `cmake_available` | `True` |
| `pkg_config_available` | `True` |
| `nvidia_smi_available` | `True` |
| `numpy_importable` | `True` |
| `cupy_importable` | `True` |
| `numba_importable` | `True` |
| `cupy_cuda_runtime_observed` | `True` |
| `optix_library_present` | `True` |
| `embree_library_present` | `True` |
| `c_api_library_present` | `True` |
| `c_api_stage_archive_present` | `True` |

## Boundary

- This is a pod-specific source-tree support observation.
- It does not authorize stable platform support, packaged SDK, system install, stable ABI, public performance claims, or release wording.
