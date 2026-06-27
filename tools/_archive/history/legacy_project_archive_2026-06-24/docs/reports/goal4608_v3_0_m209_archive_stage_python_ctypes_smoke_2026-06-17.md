# Goal4608 / V3 M209 Archive-Stage Python Ctypes Smoke

Status: `archive_stage_python_ctypes_smoke_checked`

## Conclusion

Goal4608 validates that the movable source-tree C ABI archive can run the staged Python `ctypes` examples after extraction. The pod smoke builds `package-c-api-stage`, unpacks `rtdl-c-api-stage-0.1.3.tar.gz`, and runs lifecycle, host AABB2, CUDA metadata, and DLPack-like metadata examples against the extracted shared library. This authorizes extracted-archive Python `ctypes` smoke only; it is not a generated Python package, wheel, system install, package-manager artifact, packaged SDK, stable ABI, device-buffer query route, release, or performance claim.

## Smoke

- OK: `True`
- Archive: `build/rtdl-c-api-stage-0.1.3.tar.gz`
- Extract dir: `/tmp/rtdl_c_api_archive_python_n7b_zxc6/extracted/rtdl-c-api-stage-0.1.3`

| Script | OK | Stdout |
| --- | --- | --- |
| `python_ctypes_client.py` | `True` | `python_ctypes_ok 0.1.3 ok` |
| `python_ctypes_aabb2_query_client.py` | `True` | `python_ctypes_hit_count=1 first_pair=(0,0)` |
| `python_ctypes_cuda_buffer_metadata_client.py` | `True` | `python_ctypes_cuda_metadata_shape=(3,4) query_route_rejected=invalid argument` |
| `python_ctypes_dlpack_like_metadata_client.py` | `True` | `python_ctypes_dlpack_like_metadata_shape=(2,3) query_route_rejected=invalid argument` |

## Checks

| Check | Passed |
| --- | --- |
| `makefile_archive_carries_python_ctypes_examples` | `True` |
| `staging_contract_documents_archive_python_examples` | `True` |
| `embedding_readme_documents_archive_python_examples` | `True` |
| `architecture_doc_names_archive_python_smoke` | `True` |
| `binding_matrix_names_archive_python_surface` | `True` |
| `benchmark_index_links_goal4608` | `True` |
| `prior_stage_archive_smoke_ok` | `True` |
| `prior_archive_cmake_smoke_ok` | `True` |
| `prior_prefix_python_smoke_ok` | `True` |
| `prior_dlpack_like_bridge_smoke_ok` | `True` |
| `make_package_stage_ok` | `True` |
| `archive_exists_and_nonempty` | `True` |
| `all_archive_python_examples_run` | `True` |
| `archive_python_lifecycle_stdout_matches` | `True` |
| `archive_python_aabb2_stdout_matches` | `True` |
| `archive_python_cuda_metadata_stdout_matches` | `True` |
| `archive_python_dlpack_like_metadata_stdout_matches` | `True` |

## Boundary

- This validates extracted source-tree archive Python `ctypes` examples only.
- It does not authorize a generated Python package, wheel, system install, package-manager artifact, packaged SDK, stable ABI, device-buffer query route, release, or performance claim.
