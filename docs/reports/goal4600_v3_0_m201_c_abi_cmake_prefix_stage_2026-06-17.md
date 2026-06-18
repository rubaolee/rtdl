# Goal4600 / V3 M201 C ABI CMake Prefix Stage

Status: `c_abi_cmake_prefix_stage_checked`

## Conclusion

Goal4600 adds relocatable CMake package metadata to the C ABI stage and prefix-stage layouts. The pod evidence stages RTDL under a temporary `/opt/rtdl` prefix, configures an external CMake consumer with `find_package(rtdl-c-api CONFIG REQUIRED)`, builds it against the imported `rtdl::c_api` target, and runs it against the staged shared library. This authorizes CMake prefix-stage consumption only, not a system install, package-manager artifact, packaged SDK, stable ABI, or release claim.

## Smoke

- OK: `True`
- CMake: `/usr/bin/cmake`
- Prefix dir: `/tmp/rtdl_c_api_cmake_prefix_j1p4gt73/stage/opt/rtdl`
- Output: `cmake_direct_link_ok 0.1.3 ok`

## Checks

| Check | Passed |
| --- | --- |
| `cmake_config_is_relocatable` | `True` |
| `cmake_config_exports_imported_target` | `True` |
| `makefile_stages_cmake_config` | `True` |
| `staging_contract_documents_cmake_config` | `True` |
| `embedding_readme_documents_cmake_config` | `True` |
| `doctor_checks_cmake_metadata_presence` | `True` |
| `doctor_doc_names_cmake_metadata_boundary` | `True` |
| `make_prefix_stage_ok` | `True` |
| `cmake_available` | `True` |
| `cmake_configure_ok` | `True` |
| `cmake_build_ok` | `True` |
| `cmake_consumer_runs` | `True` |

## Boundary

- This validates CMake prefix-stage consumption only.
- It does not authorize a system install, package-manager artifact, packaged SDK, stable ABI, or release claim.
