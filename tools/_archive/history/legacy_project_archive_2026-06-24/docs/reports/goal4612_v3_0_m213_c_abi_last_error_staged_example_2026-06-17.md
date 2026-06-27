# Goal4612 / V3 M213 C ABI Last-Error Staged Example

Status: `c_abi_last_error_staged_example_checked`

## Conclusion

Goal4612 promotes the C ABI status/last-error diagnostic pattern from an internal smoke into the user-facing embedding bundle. The new `c_api_last_error_client.c` example is staged, prefix-staged, archived, compiled through staged `pkg-config` flags, and run against the staged shared library. This authorizes the staged diagnostic example only; error text remains diagnostic and callers must branch on `rtdl_status`.

## Smoke

- OK: `True`
- Stage dir: `build/c_api_stage`
- Output: `case status_string_diagnostics_ok: ok
case null_context_last_error_ok: ok
case initial_last_error_empty: ok
case invalid_buffer_sets_last_error: ok
case successful_buffer_import_clears_last_error: ok
case unsupported_runtime_sets_last_error: ok
case successful_runtime_clears_last_error: ok
validated_last_error_diagnostics_cases=7`

## Checks

| Check | Passed |
| --- | --- |
| `example_source_exists_and_uses_diagnostic_api` | `True` |
| `makefile_stages_example_in_source_and_prefix_stages` | `True` |
| `staging_contract_lists_and_documents_example` | `True` |
| `embedding_readme_documents_example_command_and_boundary` | `True` |
| `staging_inventory_requires_example` | `True` |
| `archive_c_examples_smoke_requires_example` | `True` |
| `binding_matrix_names_staged_example` | `True` |
| `architecture_doc_current_to_goal4612` | `True` |
| `benchmark_index_links_goal4612` | `True` |
| `make_available` | `True` |
| `pkg_config_available` | `True` |
| `cc_available` | `True` |
| `stage_make_ok` | `True` |
| `pkg_config_cflags_ok` | `True` |
| `pkg_config_libs_ok` | `True` |
| `staged_example_compiles` | `True` |
| `staged_example_runs_expected_marker` | `True` |

## Boundary

- This validates the staged C status/last-error diagnostics example only.
- Error text remains diagnostic; callers branch on `rtdl_status`.
- No stable error-text, stable ABI, packaged SDK, system install, release, or performance claim is authorized.
