# Goal4605 / V3 M206 Binding And Device Interop Matrix

Status: `binding_device_interop_matrix_checked`

## Conclusion

Goal4605 consolidates the current V3 binding and device interop state. The source tree has executable C and Python ctypes examples, pkg-config and CMake staged handoffs, a host AABB2 C ABI query route, host-runtime metadata, and CUDA descriptor metadata including a `__cuda_array_interface__`-style Python bridge, DLPack-like metadata bridging, extracted archive Python ctypes smoke, and extracted archive C examples smoke. The device side is still deliberately fail-closed: no DLPack adapter, device-buffer query route, external CUDA stream ordering, generated binding, stable ABI, SDK, release, performance claim, or true-zero-copy claim is authorized by this matrix.

## Current Matrix

| Surface | Status |
| --- | --- |
| `c_source_tree_examples` | `validated_dynamic_and_direct_link` |
| `c_archive_examples` | `validated_direct_link_dlopen_host_runtime_cuda_metadata` |
| `pkg_config_stage` | `validated` |
| `cmake_prefix_find_package` | `validated_imported_target` |
| `cmake_archive_find_package` | `validated_extracted_archive_imported_target` |
| `python_ctypes_lifecycle_and_host_aabb2` | `validated_lifecycle_host_aabb2_cuda_metadata` |
| `python_ctypes_archive_examples` | `validated_lifecycle_host_aabb2_cuda_metadata_dlpack_like` |
| `host_aabb2_c_abi_query` | `validated_host_f32_to_host_u64_pairs` |
| `host_external_runtime_metadata` | `validated` |
| `cuda_buffer_descriptor_import_export` | `validated_metadata_only` |
| `cuda_array_interface_to_c_abi_descriptor` | `validated_metadata_only` |
| `cuda_descriptor_host_aabb2_query_route` | `rejected_invalid_argument` |
| `dlpack_like_to_c_abi_descriptor` | `validated_metadata_only` |
| `dlpack_like_descriptor_host_aabb2_query_route` | `rejected_invalid_argument` |
| `dlpack` | `design_contract_only` |
| `device_buffer_query_route` | `blocked` |
| `external_cuda_stream_ordering` | `blocked` |
| `generated_language_bindings` | `blocked` |
| `public_true_zero_copy_claim` | `blocked` |
| `stable_abi` | `blocked_until_1_0_gates` |
| `release` | `blocked` |

## Live Smokes

| Smoke | OK |
| --- | --- |
| `host_external_runtime` | `True` |
| `cuda_buffer_metadata` | `True` |
| `python_cuda_metadata_bridge` | `True` |

## Checks

| Check | Passed |
| --- | --- |
| `matrix_doc_exists` | `True` |
| `matrix_doc_lists_current_binding_surfaces` | `True` |
| `matrix_doc_blocks_device_claims` | `True` |
| `learn_readme_links_matrix` | `True` |
| `doctor_doc_mentions_binding_matrix` | `True` |
| `doctor_script_requires_binding_matrix` | `True` |
| `benchmark_index_links_goal4605` | `True` |
| `c_abi_draft_keeps_cuda_descriptor_metadata_only` | `True` |
| `zero_copy_doc_blocks_true_zero_copy` | `True` |
| `embedding_readme_blocks_device_execution` | `True` |
| `header_keeps_external_cuda_runtime_unsupported` | `True` |
| `python_cuda_example_rejects_host_query_route` | `True` |
| `all_source_reports_accept` | `True` |
| `host_runtime_metadata_validated` | `True` |
| `cuda_descriptor_validated_metadata_only` | `True` |
| `python_cuda_metadata_bridge_validated` | `True` |
| `python_dlpack_like_metadata_bridge_validated` | `True` |
| `archive_python_ctypes_examples_validated` | `True` |
| `archive_c_examples_validated` | `True` |
| `delivery_cmake_pkg_config_handoff_validated` | `True` |
| `device_and_stream_routes_blocked` | `True` |
| `generated_bindings_blocked` | `True` |
| `live_host_external_runtime_smoke_ok` | `True` |
| `live_cuda_buffer_metadata_smoke_ok` | `True` |
| `live_python_cuda_metadata_bridge_smoke_ok` | `True` |

## Boundary

- Current C/Python examples, staged pkg-config, and staged CMake handoffs are authorized as source-tree evidence.
- CUDA descriptor import/export and `__cuda_array_interface__` descriptor bridging are metadata-only.
- DLPack, device-buffer query routes, external CUDA stream ordering, generated bindings, stable ABI, packaged SDK, release, performance, and true-zero-copy wording remain blocked.
