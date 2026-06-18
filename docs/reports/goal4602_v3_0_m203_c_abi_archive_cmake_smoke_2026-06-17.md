# Goal4602 / V3 M203 C ABI Archive CMake Smoke

Status: `c_abi_archive_cmake_smoke_checked`

## Conclusion

Goal4602 validates that the movable source-tree C ABI archive is consumable by an external CMake project after extraction. The smoke builds `package-c-api-stage`, unpacks `rtdl-c-api-stage-0.1.3.tar.gz`, configures an external consumer with `find_package(rtdl-c-api CONFIG REQUIRED)` via `CMAKE_PREFIX_PATH`, builds against `rtdl::c_api`, and runs against the extracted shared library. This authorizes archive CMake-stage consumption only; it is still not a system install, package-manager artifact, packaged SDK, stable ABI, or release claim.

## Smoke

- OK: `True`
- CMake: `/usr/bin/cmake`
- Extract dir: `/tmp/rtdl_c_api_archive_cmake_yvxjb7l0/extracted/rtdl-c-api-stage-0.1.3`
- Output: `cmake_archive_direct_link_ok 0.1.3 ok`

## Checks

| Check | Passed |
| --- | --- |
| `makefile_archive_stages_cmake_config` | `True` |
| `staging_contract_documents_archive_cmake_consumer` | `True` |
| `embedding_readme_documents_archive_cmake_consumer` | `True` |
| `prior_archive_pkg_config_smoke_ok` | `True` |
| `prior_prefix_cmake_smoke_ok` | `True` |
| `make_package_stage_ok` | `True` |
| `archive_exists_and_nonempty` | `True` |
| `archive_contains_cmake_config` | `True` |
| `archive_cmake_configure_ok` | `True` |
| `archive_cmake_build_ok` | `True` |
| `archive_cmake_consumer_runs` | `True` |

## Boundary

- This validates CMake consumption from the extracted source-tree stage archive only.
- It does not authorize a system install, package-manager artifact, packaged SDK, stable ABI, or release claim.
