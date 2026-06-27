# Goal4595 / V3 M196 C ABI Prefix Stage

Status: `c_abi_prefix_stage_checked`

## Conclusion

Goal4595 adds and validates `make stage-c-api-prefix`, a DESTDIR/prefix-style C ABI staging layout. The pod evidence stages the bundle under a temporary root with prefix `/opt/rtdl`, uses only that staged prefix's `lib/pkgconfig/rtdl-c-api.pc` metadata to compile the staged direct-link C client, and runs it against the staged library. This authorizes a prefix-layout staging proof only; it is not a privileged system install, package-manager artifact, packaged SDK, stable ABI, generated binding, or release claim.

## Smoke

- OK: `True`
- Prefix: `/opt/rtdl`
- Prefix dir: `/tmp/rtdl_c_api_prefix_stage_so63eem3/opt/rtdl`
- Output: `direct_link_ok 0.1.3 ok`

## Checks

| Check | Passed |
| --- | --- |
| `makefile_declares_prefix_stage_target` | `True` |
| `makefile_declares_prefix_stage_controls` | `True` |
| `makefile_prefix_stage_uses_install_like_layout` | `True` |
| `pkg_config_template_remains_pcfiledir_relocatable` | `True` |
| `staging_contract_documents_prefix_stage` | `True` |
| `embedding_readme_documents_prefix_stage` | `True` |
| `docs_preserve_not_installed_sdk_boundary` | `True` |
| `prefix_stage_make_ok` | `True` |
| `pkg_config_available` | `True` |
| `cc_available` | `True` |
| `prefix_pkg_config_cflags_ok` | `True` |
| `prefix_pkg_config_libs_ok` | `True` |
| `prefix_direct_link_client_compiles` | `True` |
| `prefix_direct_link_client_runs` | `True` |
| `prefix_flags_point_at_staged_prefix` | `True` |

## Boundary

- This validates a DESTDIR/prefix-style C ABI staging layout only.
- It does not authorize a privileged system install, package-manager artifact, packaged SDK, stable ABI, generated binding, or release claim.
