# Goal4570 / V3 M171 C ABI Ownership And Threading Contract

Status: `c_abi_ownership_threading_contract_checked`

## Conclusion

Goal4570 makes the V3 C ABI ownership and threading boundary explicit: imported buffers are caller-retained when `release` is NULL, release-callback-owned when `release` is provided, AABB2 index build copies primitive rows, result exports are borrowed until result destroy, and same-handle concurrency remains externally synchronized rather than a stable SDK promise.

## Checks

| Check | Passed |
| --- | --- |
| `contract_doc_exists` | `True` |
| `contract_defines_release_null_caller_retained` | `True` |
| `contract_defines_release_callback_transfer` | `True` |
| `contract_defines_index_copy_lifetime` | `True` |
| `contract_defines_result_view_lifetime` | `True` |
| `contract_defines_last_error_lifetime` | `True` |
| `contract_defines_threading_boundary` | `True` |
| `c_abi_doc_links_contract` | `True` |
| `c_abi_doc_updates_imported_buffer_wording` | `True` |
| `stability_policy_links_contract` | `True` |
| `example_readme_updates_imported_buffer_wording` | `True` |
| `learn_readme_links_contract` | `True` |
| `header_documents_release_switch` | `True` |
| `source_calls_release_on_buffer_destroy` | `True` |
| `source_copies_aabb2_into_index` | `True` |
| `c_compiler_available` | `True` |
| `cxx_compiler_available` | `True` |
| `shared_library_build_ok` | `True` |
| `c_client_compile_ok` | `True` |
| `c_client_run_ok` | `True` |
| `runtime_validated_all_cases` | `True` |

## Runtime Cases

| Case | Passed |
| --- | --- |
| `release_callback_called_once` | `True` |
| `index_survives_primitive_buffer_destroy` | `True` |
| `result_view_borrowed_until_destroy` | `True` |

## Boundary

- This documents and validates current source-tree ownership behavior.
- It does not create a stable thread-safety guarantee, packaged SDK, cross-version compatibility claim, device-buffer ownership route, external stream semantics, or performance wording.
