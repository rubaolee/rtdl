# Goal4603 / V3 M204 Embeddability Delivery Archive CMake Refresh

Status: `embeddability_delivery_archive_cmake_refreshed`

## Conclusion

Goal4603 refreshes the embeddability delivery ledger after the archive CMake smoke. The current V3 source-tree handoff now has validated pkg-config and CMake consumption from both prefix-stage and extracted archive layouts, plus thin Python `ctypes` examples and C/Python layout drift checks. This remains an experimental source-tree/prefix/archive handoff slice, not a stable ABI, packaged SDK, system install, DLPack/true-zero-copy path, external CUDA stream contract, OptiX/Embree C ABI query surface, generated binding, release, or performance claim.

## Status Matrix

| Surface | Status |
| --- | --- |
| `cuda_buffer_descriptor_import_export` | `validated_metadata_only` |
| `device_buffer_query_route` | `blocked` |
| `dlpack_zero_copy` | `blocked` |
| `external_cuda_stream_ordering` | `blocked` |
| `generated_language_bindings` | `blocked` |
| `host_aabb2_c_abi_query` | `validated_host_f32_to_host_u64_pairs` |
| `host_external_runtime_metadata` | `validated` |
| `packaged_sdk` | `blocked` |
| `prefix_cmake_find_package` | `validated_imported_target` |
| `prefix_layout_stage` | `validated` |
| `prefix_pkg_config` | `validated` |
| `python_ctypes_c_layout_audit` | `validated_sizeof_offsetof_matches` |
| `python_ctypes_prefix_examples` | `validated_lifecycle_host_aabb2_cuda_metadata` |
| `release` | `blocked` |
| `source_tree_stage_archive` | `validated_extract_compile_run` |
| `stable_abi` | `blocked_until_1_0_gates` |
| `system_install` | `blocked` |
| `archive_cmake_find_package` | `validated_extracted_archive_imported_target` |
| `source_tree_and_prefix_stage_handoff` | `validated_pkg_config_and_cmake` |

## Checks

| Check | Passed |
| --- | --- |
| `all_required_reports_accept` | `True` |
| `architecture_status_at_or_beyond_goal4602` | `True` |
| `architecture_names_archive_cmake_proof` | `True` |
| `architecture_keeps_cmake_as_stage_not_sdk` | `True` |
| `archive_cmake_smoke_ok` | `True` |
| `archive_cmake_authorizes_archive_stage_only` | `True` |
| `prefix_cmake_still_ok` | `True` |
| `layout_audit_still_ok` | `True` |
| `prior_delivery_status_keeps_device_query_blocked` | `True` |

## Boundary

- Authorized now: source-tree/prefix/archive handoff, staged CMake/pkg-config consumption, thin Python `ctypes` smoke, and layout-drift checking.
- Still blocked: stable ABI, packaged SDK, system install, package-manager artifact, DLPack/true-zero-copy wording, device-buffer query route, external CUDA stream, OptiX/Embree C ABI query execution, generated bindings, release, and performance claims.
