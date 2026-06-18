# Goal4581 / V3 M182 C ABI Python ctypes Example

Status: `c_abi_python_ctypes_example_checked`

## Conclusion

Goal4581 adds a staged Python ctypes client over the draft C ABI. The pod evidence runs the staged Python file against the staged shared library and validates version compatibility, capability queries, and CPU context create/destroy. This proves the C ABI can serve as a thin language-binding base, but it is not a generated Python package, stable ABI, device-buffer binding, or OptiX/Embree C ABI query surface.

## Smoke

- OK: `True`
- Output: `python_ctypes_ok 0.1.3 ok`
- Command: `['/usr/bin/python3', 'build/c_api_stage/examples/python_ctypes_client.py', 'build/c_api_stage/lib/librtdl_c_api.so']`

## Checks

| Check | Passed |
| --- | --- |
| `python_ctypes_example_exists` | `True` |
| `example_loads_shared_library_with_ctypes` | `True` |
| `example_declares_context_desc_shape` | `True` |
| `example_uses_public_version_capability_and_context_symbols` | `True` |
| `makefile_stages_python_ctypes_example` | `True` |
| `staging_contract_documents_python_ctypes_example` | `True` |
| `embedding_readme_documents_python_ctypes_example` | `True` |
| `c_abi_draft_names_goal4581` | `True` |
| `stage_bundle_smoke_ok` | `True` |
| `staged_python_ctypes_example_exists` | `True` |
| `staged_library_exists` | `True` |
| `staged_python_ctypes_example_runs` | `True` |

## Boundary

- This validates a staged Python ctypes example over the draft C ABI only.
- It does not authorize a generated language-binding package, stable ABI, packaged SDK, device-buffer binding, OptiX/Embree C ABI query execution, or release claim.
