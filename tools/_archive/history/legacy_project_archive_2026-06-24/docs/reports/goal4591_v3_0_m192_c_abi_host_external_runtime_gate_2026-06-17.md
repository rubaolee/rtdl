# Goal4591 / V3 M192 C ABI Host External Runtime Gate

Status: `c_abi_host_external_runtime_checked`

## Conclusion

Goal4591 turns `rtdl_context_set_external_runtime` from an all-unsupported placeholder into a narrow, validated host-runtime metadata path. The C ABI now accepts `RTDL_DEVICE_HOST` metadata with null context/stream handles, rejects malformed host metadata, and continues to reject CUDA runtime handles. This advances the control-plane embedding boundary without authorizing CUDA stream, OptiX/Embree runtime, device-buffer, stable ABI, SDK, release, or performance claims.

## Support Matrix

| Surface | Status |
| --- | --- |
| `host_external_runtime_metadata` | `validated` |
| `malformed_host_runtime` | `rejected_invalid_argument` |
| `cuda_external_runtime` | `rejected_unsupported` |
| `external_cuda_stream_semantics` | `blocked` |
| `optix_embree_c_abi_runtime` | `blocked` |
| `device_buffer_c_abi` | `blocked` |

## Runtime Cases

| Case | Passed |
| --- | --- |
| `host_external_runtime_metadata_ok` | `True` |
| `malformed_host_runtime_rejected` | `True` |
| `cuda_runtime_rejected` | `True` |

## Checks

| Check | Passed |
| --- | --- |
| `header_documents_host_only_external_runtime` | `True` |
| `source_accepts_host_runtime_metadata` | `True` |
| `source_rejects_non_host_runtime` | `True` |
| `source_rejects_malformed_host_runtime` | `True` |
| `c_abi_doc_names_goal4591_and_boundary` | `True` |
| `ownership_doc_names_no_runtime_ownership_transfer` | `True` |
| `example_validates_success_and_rejections` | `True` |
| `stage_target_copies_host_runtime_example` | `True` |
| `staging_contract_lists_host_runtime_example` | `True` |
| `embedding_readme_documents_host_runtime_example` | `True` |
| `c_compiler_available` | `True` |
| `cxx_compiler_available` | `True` |
| `shared_library_build_ok` | `True` |
| `c_client_compile_ok` | `True` |
| `c_client_run_ok` | `True` |
| `runtime_validated_all_cases` | `True` |

## Boundary

- Host runtime metadata is validated for the current C ABI proof.
- CUDA streams, OptiX/Embree C ABI runtime adoption, device-buffer routes, stable ABI, packaged SDK, release, and performance wording remain blocked.
