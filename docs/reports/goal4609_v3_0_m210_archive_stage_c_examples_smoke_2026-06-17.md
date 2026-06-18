# Goal4609 / V3 M210 Archive-Stage C Examples Smoke

Status: `archive_stage_c_examples_smoke_checked`

## Conclusion

Goal4609 validates that the movable source-tree C ABI archive can compile and run the staged C examples after extraction. The pod smoke builds `package-c-api-stage`, unpacks `rtdl-c-api-stage-0.1.3.tar.gz`, compiles direct-link, `dlopen` host AABB2, host-runtime metadata, and CUDA descriptor metadata clients, then runs them against the extracted shared library. This authorizes extracted-archive C example smoke only; it is not a system install, package-manager artifact, packaged SDK, stable ABI, device-buffer query route, release, or performance claim.

## Smoke

- OK: `True`
- Archive: `build/rtdl-c-api-stage-0.1.3.tar.gz`
- Extract dir: `/tmp/rtdl_c_api_archive_c_examples_6ugkur2a/extracted/rtdl-c-api-stage-0.1.3`

| Example | Mode | OK | Stdout |
| --- | --- | --- | --- |
| `c_api_direct_link_client.c` | `pkg_config` | `True` | `direct_link_ok 0.1.3 ok` |
| `c_api_host_runtime_client.c` | `pkg_config` | `True` | `case host_external_runtime_metadata_ok: ok
case malformed_host_runtime_rejected: ok
case cuda_runtime_rejected: ok
validated_host_external_runtime_cases=3` |
| `c_api_cuda_buffer_metadata_client.c` | `pkg_config` | `True` | `case cuda_buffer_metadata_roundtrip_ok: ok
case cuda_query_route_rejected: ok
case cuda_buffer_release_callback_ok: ok
case invalid_cuda_buffer_metadata_rejected: ok
validated_cuda_buffer_metadata_cases=4` |
| `c_api_aabb2_overlap_client.c` | `dlopen` | `True` | `hit_count=1 first_pair=(0,0)` |

## Checks

| Check | Passed |
| --- | --- |
| `makefile_archive_carries_c_examples` | `True` |
| `staging_contract_documents_archive_c_examples` | `True` |
| `embedding_readme_documents_archive_c_examples` | `True` |
| `architecture_doc_current_to_goal4609` | `True` |
| `binding_matrix_names_archive_c_surface` | `True` |
| `benchmark_index_links_goal4609` | `True` |
| `prior_stage_archive_smoke_ok` | `True` |
| `prior_host_runtime_smoke_ok` | `True` |
| `prior_cuda_metadata_smoke_ok` | `True` |
| `prior_archive_cmake_smoke_ok` | `True` |
| `prior_archive_python_smoke_ok` | `True` |
| `make_package_stage_ok` | `True` |
| `archive_exists_and_nonempty` | `True` |
| `pkg_config_cflags_ok` | `True` |
| `pkg_config_libs_ok` | `True` |
| `all_archive_c_examples_compile_and_run` | `True` |
| `archive_direct_link_stdout_matches` | `True` |
| `archive_host_runtime_stdout_matches` | `True` |
| `archive_cuda_metadata_stdout_matches` | `True` |
| `archive_dlopen_aabb2_stdout_matches` | `True` |

## Boundary

- This validates extracted source-tree archive C examples only.
- It does not authorize a system install, package-manager artifact, packaged SDK, stable ABI, device-buffer query route, release, or performance claim.
