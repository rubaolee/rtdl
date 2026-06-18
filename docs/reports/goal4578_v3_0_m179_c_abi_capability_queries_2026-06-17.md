# Goal4578 / V3 M179 C ABI Capability Queries

Status: `c_abi_capability_queries_checked`

## Conclusion

Goal4578 adds draft C ABI capability queries for the currently supported backend and primitive/query/device route surface. The runtime smoke proves AUTO/CPU and host AABB2 overlap return supported, while OptiX, CUDA-device AABB2 overlap, and segment/ray routes fail closed. This is discovery metadata for the source-tree draft, not authorization for broader backend execution.

## Symbols

- `rtdl_backend_is_supported`
- `rtdl_route_is_supported`

## Checks

| Check | Passed |
| --- | --- |
| `header_version_is_0_1_3` | `True` |
| `header_declares_capability_queries` | `True` |
| `source_implements_backend_and_route_queries` | `True` |
| `source_documents_current_route_shape_in_code` | `True` |
| `current_manifest_has_capability_symbols` | `True` |
| `previous_manifest_lacks_capability_symbols` | `True` |
| `goal4552_runtime_smoke_checks_capabilities` | `True` |
| `goal4556_exports_capability_symbols` | `True` |
| `docs_name_capability_queries` | `True` |
| `runtime_shared_library_ok` | `True` |
| `runtime_capability_smoke_ok` | `True` |

## Boundary

- Capability queries expose current draft support metadata only.
- They do not authorize dynamic backend loading, OptiX/Embree C ABI queries, device buffers, stable ABI wording, or release claims.
