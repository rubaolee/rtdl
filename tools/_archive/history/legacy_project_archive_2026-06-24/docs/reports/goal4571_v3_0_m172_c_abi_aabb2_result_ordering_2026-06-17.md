# Goal4571 / V3 M172 C ABI AABB2 Result Ordering

Status: `c_abi_aabb2_result_ordering_checked`

## Conclusion

Goal4571 documents and validates deterministic result ordering for the current host F32 AABB2 C ABI route: rows are emitted by ascending query_id, then ascending primitive_id. This is a narrow host-route contract, not a general OptiX, Embree, device-buffer, or performance claim.

## Checks

| Check | Passed |
| --- | --- |
| `c_abi_doc_defines_result_ordering` | `True` |
| `example_readme_repeats_result_ordering` | `True` |
| `source_loop_order_matches_contract` | `True` |
| `client_source_checks_multi_hit_order` | `True` |
| `evidence_index_links_goal4571` | `True` |
| `c_compiler_available` | `True` |
| `cxx_compiler_available` | `True` |
| `shared_library_build_ok` | `True` |
| `c_client_compile_ok` | `True` |
| `c_client_run_ok` | `True` |
| `runtime_validated_all_cases` | `True` |

## Runtime Cases

| Case | Passed |
| --- | --- |
| `multi_hit_rows_query_then_primitive_order` | `True` |
| `result_shape_stride_and_byte_count_match_pairs` | `True` |

## Boundary

- This validates only the current host F32 AABB2 overlap route.
- No general query ordering, OptiX ordering, Embree ordering, device-buffer route, or performance wording is authorized.
