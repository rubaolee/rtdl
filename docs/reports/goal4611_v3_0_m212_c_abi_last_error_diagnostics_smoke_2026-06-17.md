# Goal4611 / V3 M212 C ABI Last-Error Diagnostics Smoke

Status: `c_abi_last_error_diagnostics_checked`

## Conclusion

Goal4611 adds a C dynamic-load smoke for the C ABI diagnostic surface: status strings, null-context last-error behavior, selected failure messages, and clearing of last_error after successful context-mutating calls. This makes the embedding boundary easier to debug from Python/Rust/Julia-style bindings while keeping status codes as the only branching contract. It does not freeze exact error text, exhaustively validate every failure path, authorize concurrent last-error reads, or authorize release/performance wording.

## Runtime Cases

| Case | Validated |
| --- | --- |
| `status_strings_stable` | `True` |
| `null_context_last_error_stable` | `True` |
| `initial_last_error_empty` | `True` |
| `invalid_buffer_import_sets_message` | `True` |
| `successful_buffer_import_clears_error` | `True` |
| `cuda_runtime_sets_message` | `True` |
| `host_runtime_clears_error` | `True` |
| `index_abi_mismatch_sets_message` | `True` |
| `successful_index_build_clears_error` | `True` |
| `unsupported_query_sets_message` | `True` |
| `successful_query_clears_error` | `True` |

## Smoke

- OK: `True`
- C compiler: `/usr/bin/cc`
- C++ compiler: `/usr/bin/c++`
- Output marker: `case status_strings_stable: ok
case null_context_last_error_stable: ok
case initial_last_error_empty: ok
case invalid_buffer_import_sets_message: ok
case successful_buffer_import_clears_error: ok
case cuda_runtime_sets_message: ok
case host_runtime_clears_error: ok
case index_abi_mismatch_sets_message: ok
case successful_index_build_clears_error: ok
case unsupported_query_sets_message: ok
case successful_query_clears_error: ok
validated_last_error_lifecycle_cases=11`

## Support Matrix

| Surface | Status |
| --- | --- |
| `status_string_diagnostics` | `validated_source_tree_smoke` |
| `null_context_last_error` | `validated_source_tree_smoke` |
| `last_error_set_on_selected_failures` | `validated_source_tree_smoke` |
| `last_error_cleared_after_successful_context_mutations` | `validated_source_tree_smoke` |
| `last_error_text_as_machine_contract` | `blocked_use_status_codes` |

## Checks

| Check | Passed |
| --- | --- |
| `header_declares_status_string_and_last_error` | `True` |
| `source_has_status_string_and_null_context_diagnostic` | `True` |
| `source_clears_context_errors_after_successful_mutations` | `True` |
| `client_source_covers_all_lifecycle_markers` | `True` |
| `ownership_doc_defines_last_error_clear_rule` | `True` |
| `ownership_doc_keeps_error_text_non_machine_contract` | `True` |
| `architecture_doc_current_to_goal4611` | `True` |
| `binding_matrix_names_last_error_diagnostics` | `True` |
| `benchmark_index_links_goal4611` | `True` |
| `c_compiler_available` | `True` |
| `cxx_compiler_available` | `True` |
| `shared_library_build_ok` | `True` |
| `c_client_compile_ok` | `True` |
| `c_client_run_ok` | `True` |
| `runtime_validated_all_lifecycle_cases` | `True` |

## Boundary

- Status codes remain the machine-readable branching contract.
- Last-error text is diagnostic and may change while the ABI is still draft.
- This is not exhaustive failure-path coverage, thread-safe last-error authorization, release evidence, or performance evidence.
