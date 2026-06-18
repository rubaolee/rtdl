# Goal4599 / V3 M200 Python Ctypes Layout Audit

Status: `python_ctypes_layout_audit_checked`

## Conclusion

Goal4599 adds a C/Python layout audit for the current draft C ABI descriptor structs used by the Python `ctypes` examples. The pod evidence compiles a tiny C `sizeof`/`offsetof` probe against `docs/history/v4_preparatory_embedding/staging/include/rtdl/rtdl.h` and compares it with Python `ctypes` layout for external runtime, buffer view, context, index, and query descriptors. This catches binding-offset drift without authorizing stable ABI, generated binding, cross-platform layout, SDK, or release wording.

## Probe

- OK: `True`
- C compiler: `/usr/bin/cc`

## Checked Types

| C type | Size | Fields |
| --- | --- | --- |
| `rtdl_external_runtime` | `32` | `device_type:0, device_id:4, context:8, stream:16, user_data:24` |
| `rtdl_buffer_view` | `176` | `data:0, byte_count:8, device_type:16, device_id:20, dtype:24, ndim:28, shape:32, strides:96, release:160, user_data:168` |
| `rtdl_context_desc` | `48` | `abi_version_major:0, abi_version_minor:4, backend:8, external_runtime:16` |
| `rtdl_index_desc` | `32` | `abi_version_major:0, abi_version_minor:4, primitive_kind:8, primitives:16, primitive_count:24` |
| `rtdl_query_desc` | `32` | `abi_version_major:0, abi_version_minor:4, query_kind:8, inputs:16, input_count:24` |

## Checks

| Check | Passed |
| --- | --- |
| `header_declares_layout_types` | `True` |
| `python_aabb2_example_declares_all_layout_types` | `True` |
| `python_cuda_example_declares_buffer_view` | `True` |
| `python_examples_share_buffer_view_layout` | `True` |
| `stability_policy_names_layout_audit` | `True` |
| `c_compiler_available` | `True` |
| `c_layout_probe_compiles` | `True` |
| `c_layout_probe_runs` | `True` |
| `c_layout_matches_python_ctypes_layout` | `True` |

## Boundary

- This is a same-platform layout audit for the current draft C ABI and Python `ctypes` examples.
- It does not authorize stable ABI, generated bindings, cross-platform layout guarantees, packaged SDK, or release claims.
