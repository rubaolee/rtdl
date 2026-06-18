# Goal4563 / V3 M164 C ABI AABB2 Negative Runtime

Status: `c_abi_aabb2_negative_runtime_checked`

## Conclusion

Goal4563 hardens the first V3 C ABI query proof with a real C client that validates fail-closed behavior for unsupported primitive/query kinds, bad dtype/device inputs, ABI mismatch, and a successful no-overlap result that returns an empty host U64 pair buffer. This remains a narrow host AABB2 proof, not backend or release evidence.

## Runtime Cases

| Case | Validated |
| --- | --- |
| `unsupported_primitive_rejected` | `True` |
| `bad_index_dtype_rejected` | `True` |
| `cuda_index_device_rejected` | `True` |
| `query_abi_mismatch_rejected` | `True` |
| `unsupported_query_kind_rejected` | `True` |
| `bad_query_dtype_rejected` | `True` |
| `no_overlap_returns_empty_u64_pairs` | `True` |

## Checks

| Check | Passed |
| --- | --- |
| `header_declares_aabb2_and_overlap` | `True` |
| `source_has_unsupported_status_paths` | `True` |
| `source_has_invalid_argument_paths` | `True` |
| `client_source_covers_all_negative_cases` | `True` |
| `client_source_validates_empty_result_shape` | `True` |
| `c_compiler_available` | `True` |
| `cxx_compiler_available` | `True` |
| `shared_library_build_ok` | `True` |
| `c_client_compile_ok` | `True` |
| `c_client_run_ok` | `True` |
| `runtime_validated_all_cases` | `True` |

## Boundary

- This validates only host F32 AABB2 C ABI negative/edge behavior.
- No OptiX, Embree, device-buffer query, broad semantics, frozen ABI, or release claim is authorized.
