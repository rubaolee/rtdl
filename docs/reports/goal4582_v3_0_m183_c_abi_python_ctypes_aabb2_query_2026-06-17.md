# Goal4582 / V3 M183 C ABI Python ctypes AABB2 Query

Status: `c_abi_python_ctypes_aabb2_query_checked`

## Conclusion

Goal4582 proves the staged Python ctypes path can run the current real C ABI query route, not just load lifecycle symbols. The pod evidence stages the C ABI bundle, imports host F32 AABB2 primitive and query buffers from Python, builds an index, executes host AABB2 overlap, exports the U64 result pair, and validates `(0,0)`. This still remains a source-tree draft example; it is not a generated Python package, stable ABI, device-buffer binding, OptiX/Embree C ABI execution surface, or performance claim.

## Smoke

- OK: `True`
- Output: `python_ctypes_hit_count=1 first_pair=(0,0)`
- Command: `['/usr/bin/python3', 'build/c_api_stage/examples/python_ctypes_aabb2_query_client.py', 'build/c_api_stage/lib/librtdl_c_api.so']`

## Checks

| Check | Passed |
| --- | --- |
| `python_ctypes_query_example_exists` | `True` |
| `example_defines_buffer_index_and_query_descriptors` | `True` |
| `example_runs_real_host_aabb2_query_symbols` | `True` |
| `example_checks_u64_result_pair` | `True` |
| `makefile_stages_python_ctypes_query_example` | `True` |
| `staging_contract_documents_python_ctypes_query_example` | `True` |
| `embedding_readme_documents_python_ctypes_query_example` | `True` |
| `c_abi_draft_names_goal4582` | `True` |
| `stage_bundle_smoke_ok` | `True` |
| `staged_python_ctypes_query_example_exists` | `True` |
| `staged_library_exists` | `True` |
| `staged_python_ctypes_query_example_runs` | `True` |

## Boundary

- This validates a staged Python ctypes host AABB2 query example over the draft C ABI only.
- It does not authorize a generated language-binding package, stable ABI, packaged SDK, device-buffer binding, OptiX/Embree C ABI query execution, performance wording, or release claim.
