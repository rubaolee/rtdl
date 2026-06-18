# Goal4613 / V3 M214 Prefix-Stage C Examples Smoke

Status: `prefix_stage_c_examples_smoke_checked`

## Conclusion

Goal4613 validates that the DESTDIR/prefix-style C ABI stage can compile and run every staged C example. The pod smoke stages RTDL under a temporary `/opt/rtdl` prefix, compiles direct-link, `dlopen` host AABB2, host-runtime metadata, CUDA descriptor metadata, and status/last-error diagnostics clients, then runs them against the staged shared library. This authorizes prefix-stage C example smoke only; it is not a system install, package-manager artifact, packaged SDK, stable ABI, release, or performance claim.

## Smoke

- OK: `True`
- Prefix dir: `/tmp/rtdl_c_api_prefix_c_examples_ukeopjfs/opt/rtdl`

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
| `c_api_last_error_client.c` | `pkg_config` | `True` | `case status_string_diagnostics_ok: ok
case null_context_last_error_ok: ok
case initial_last_error_empty: ok
case invalid_buffer_sets_last_error: ok
case successful_buffer_import_clears_last_error: ok
case unsupported_runtime_sets_last_error: ok
case successful_runtime_clears_last_error: ok
validated_last_error_diagnostics_cases=7` |
| `c_api_aabb2_overlap_client.c` | `dlopen` | `True` | `hit_count=1 first_pair=(0,0)` |

## Checks

| Check | Passed |
| --- | --- |
| `makefile_prefix_stage_carries_all_c_examples` | `True` |
| `staging_contract_documents_prefix_c_examples` | `True` |
| `embedding_readme_documents_prefix_c_examples` | `True` |
| `architecture_doc_names_prefix_c_examples_smoke` | `True` |
| `binding_matrix_names_prefix_c_surface` | `True` |
| `benchmark_index_links_goal4613` | `True` |
| `make_prefix_stage_ok` | `True` |
| `pkg_config_available` | `True` |
| `cc_available` | `True` |
| `prefix_pkg_config_cflags_ok` | `True` |
| `prefix_pkg_config_libs_ok` | `True` |
| `all_prefix_c_examples_compile_and_run` | `True` |
| `prefix_direct_link_stdout_matches` | `True` |
| `prefix_host_runtime_stdout_matches` | `True` |
| `prefix_cuda_metadata_stdout_matches` | `True` |
| `prefix_last_error_stdout_matches` | `True` |
| `prefix_dlopen_aabb2_stdout_matches` | `True` |

## Boundary

- This validates prefix-stage C examples only.
- It does not authorize a system install, package-manager artifact, packaged SDK, stable ABI, release, or performance claim.
