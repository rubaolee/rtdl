# Goal4597 / V3 M198 Prefix-Stage Python Ctypes Smoke

Status: `prefix_stage_python_ctypes_checked`

## Conclusion

Goal4597 validates that the prefix-style C ABI stage is usable from the staged Python `ctypes` examples, not only from a direct-link C client. The pod evidence builds a temporary `/opt/rtdl` prefix stage and runs the lifecycle, host AABB2 query, CUDA metadata, and DLPack-like metadata bridge examples against the staged shared library. This authorizes a prefix-stage Python `ctypes` smoke only; it is not a generated Python package, system install, packaged SDK, stable ABI, or release claim.

## Smoke

- OK: `True`
- Prefix: `/opt/rtdl`
- Prefix dir: `/tmp/rtdl_c_api_prefix_python_e36_6hug/opt/rtdl`

| Script | OK | Stdout |
| --- | --- | --- |
| `python_ctypes_client.py` | `True` | `python_ctypes_ok 0.1.3 ok` |
| `python_ctypes_aabb2_query_client.py` | `True` | `python_ctypes_hit_count=1 first_pair=(0,0)` |
| `python_ctypes_cuda_buffer_metadata_client.py` | `True` | `python_ctypes_cuda_metadata_shape=(3,4) query_route_rejected=invalid argument` |
| `python_ctypes_dlpack_like_metadata_client.py` | `True` | `python_ctypes_dlpack_like_metadata_shape=(2,3) query_route_rejected=invalid argument` |

## Checks

| Check | Passed |
| --- | --- |
| `prefix_stage_target_exists` | `True` |
| `prefix_stage_copies_python_ctypes_examples` | `True` |
| `staging_contract_documents_prefix_python_examples` | `True` |
| `embedding_readme_documents_prefix_python_examples` | `True` |
| `prefix_stage_report_accepts` | `True` |
| `prefix_stage_report_keeps_system_install_false` | `True` |
| `prefix_stage_make_ok` | `True` |
| `all_prefix_python_examples_run` | `True` |
| `python_ctypes_lifecycle_stdout_matches` | `True` |
| `python_ctypes_aabb2_stdout_matches` | `True` |
| `python_ctypes_cuda_metadata_stdout_matches` | `True` |
| `python_ctypes_dlpack_like_metadata_stdout_matches` | `True` |

## Boundary

- This validates prefix-stage Python `ctypes` examples only.
- It does not authorize a generated Python package, system install, package-manager artifact, packaged SDK, stable ABI, or release claim.
