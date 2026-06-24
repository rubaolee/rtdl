# Goal4587 / V3 M188 C ABI Stage Archive

Status: `c_abi_stage_archive_checked`

## Conclusion

Goal4587 adds and validates `make package-c-api-stage`, a versioned archive of the source-tree C ABI staging bundle. The pod evidence builds the archive, extracts it elsewhere, compiles the staged direct-link C client via the extracted pkg-config metadata, and runs it against the extracted library. This is a movable source-tree stage archive, not a packaged SDK, system install, stable ABI, generated binding, or release claim.

## Smoke

- OK: `True`
- Archive: `build/rtdl-c-api-stage-0.1.3.tar.gz`
- Archive size bytes: `14777`
- Output: `direct_link_ok 0.1.3 ok`

## Checks

| Check | Passed |
| --- | --- |
| `makefile_declares_package_stage_target` | `True` |
| `package_stage_target_depends_on_stage` | `True` |
| `package_stage_archive_name_is_versioned` | `True` |
| `staging_contract_documents_archive_target` | `True` |
| `embedding_readme_documents_archive_target` | `True` |
| `make_package_stage_ok` | `True` |
| `archive_exists_and_nonempty` | `True` |
| `extracted_archive_pkg_config_cflags_ok` | `True` |
| `extracted_archive_pkg_config_libs_ok` | `True` |
| `extracted_archive_direct_link_compiles` | `True` |
| `extracted_archive_direct_link_runs` | `True` |

## Boundary

- This validates a movable source-tree stage archive only.
- It does not authorize a packaged SDK, system install, stable ABI, generated binding, or release claim.
