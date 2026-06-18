# Goal4559 / V3 M160 C ABI Example Client

Status: `c_abi_example_client_checked`

## Conclusion

Goal4559 promotes the C ABI host AABB2 overlap proof into a readable example client under `examples/current/embedding/`. Pod evidence builds `librtdl_c_api`, compiles the C example, runs it, and observes the expected single overlap pair. This is still a source-tree example, not a packaged SDK or OptiX/Embree/device-buffer claim.

## Run Result

- OK: `True`
- Executable: `build/rtdl_c_api_aabb2_overlap_client`
- Artifact: `build/librtdl_c_api.so`

## Checks

| Check | Passed |
| --- | --- |
| `example_exists` | `True` |
| `example_includes_public_header` | `True` |
| `example_uses_dynamic_library_loading` | `True` |
| `example_builds_aabb2_index` | `True` |
| `example_executes_overlap_query` | `True` |
| `example_checks_expected_pair` | `True` |
| `make_available` | `True` |
| `cc_available` | `True` |
| `make_build_ok` | `True` |
| `example_compile_ok` | `True` |
| `example_run_ok` | `True` |

## Boundary

- This is a source-tree C client example for host AABB2 overlap only.
- No packaged SDK, OptiX, Embree, device-buffer query, frozen ABI, or release claim is authorized.
