# Goal4575 / V3 M176 C ABI Version Negotiation

Status: `c_abi_version_negotiation_checked`

## Conclusion

Goal4575 adds a draft C ABI version-negotiation guard. Clients can call `rtdl_abi_is_compatible(major, minor, patch)` before using the library; current descriptor entrypoints also reject mismatched major/minor values. The rule is intentionally fail-closed for the 0.x source-tree ABI and does not authorize stable SDK wording.

## Version Surface

- Current ABI: `0.1.2`
- Current manifest: `docs/learn/v3_0_c_abi_symbol_manifest_v0_1_2.json`
- Previous manifest: `docs/learn/v3_0_c_abi_symbol_manifest_v0_1_1.json`

## Checks

| Check | Passed |
| --- | --- |
| `header_version_is_0_1_2` | `True` |
| `header_declares_compatibility_function` | `True` |
| `source_implements_patch_compatible_guard` | `True` |
| `descriptor_entrypoints_use_minor_guard` | `True` |
| `policy_documents_0x_compatibility_rule` | `True` |
| `draft_mentions_compatibility_guard` | `True` |
| `manifest_is_0_1_2_with_16_symbols` | `True` |
| `previous_manifest_retained_as_history` | `True` |
| `goal4552_report_has_runtime_compatibility_checks` | `True` |
| `goal4556_export_audit_includes_compat_symbol` | `True` |
| `goal4566_manifest_gate_accepts_current_manifest` | `True` |
| `goal4574_retains_m175_history` | `True` |
| `runtime_shared_library_ok` | `True` |
| `runtime_compatibility_smoke_ok` | `True` |

## Boundary

- This is a draft 0.x fail-closed compatibility guard.
- It does not freeze binary compatibility, publish a packaged SDK, promise cross-minor compatibility, or authorize release wording.
