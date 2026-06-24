# Goal4586 / V3 M187 C ABI pkg-config Relocatable Stage

Status: `c_abi_pkg_config_relocatable_stage_checked`

## Conclusion

Goal4586 proves the staged pkg-config metadata is relocatable within the source-tree staging contract. The pod evidence builds `build/c_api_stage`, copies that stage to a temporary directory, uses the copied `lib/pkgconfig/rtdl-c-api.pc` to compile the staged direct-link C client, and runs it against the copied library. This is still not a system install, packaged SDK, stable ABI, generated binding, or release claim.

## Smoke

- OK: `True`
- Copied stage: `/tmp/rtdl_c_api_stage_reloc_q19ce008/c_api_stage`
- Output: `direct_link_ok 0.1.3 ok`

## Checks

| Check | Passed |
| --- | --- |
| `pkg_config_template_uses_pcfiledir_relative_prefix` | `True` |
| `pkg_config_template_does_not_embed_repo_path` | `True` |
| `docs_describe_source_tree_staging_not_install` | `True` |
| `stage_bundle_smoke_ok` | `True` |
| `pkg_config_available` | `True` |
| `cc_available` | `True` |
| `relocated_pkg_config_cflags_ok` | `True` |
| `relocated_pkg_config_libs_ok` | `True` |
| `relocated_direct_link_client_compiles` | `True` |
| `relocated_direct_link_client_runs` | `True` |
| `relocated_flags_point_at_copied_stage` | `True` |

## Boundary

- This validates relocatability of the source-tree staging bundle only.
- It does not authorize a system install, packaged SDK, stable ABI, generated binding, or release claim.
