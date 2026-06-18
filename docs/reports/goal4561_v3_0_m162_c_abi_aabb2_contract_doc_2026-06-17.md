# Goal4561 / V3 M162 C ABI AABB2 Contract Doc

Status: `c_abi_aabb2_contract_doc_checked`

## Conclusion

Goal4561 documents the exact current C ABI host AABB2 overlap contract: F32 `[count,4]` input rows, U64 `[hit_count,2]` result rows, ownership, and unsupported-route boundaries. It remains a narrow source-tree V3 draft contract, not a frozen or GPU-backend claim.

## Checks

| Check | Passed |
| --- | --- |
| `c_abi_doc_names_current_contract_section` | `True` |
| `c_abi_doc_defines_f32_aabb2_input_layout` | `True` |
| `c_abi_doc_defines_u64_pair_result_layout` | `True` |
| `c_abi_doc_defines_ownership` | `True` |
| `c_abi_doc_blocks_unsupported_routes` | `True` |
| `example_readme_repeats_layout` | `True` |
| `example_source_matches_documented_layout` | `True` |

## Boundary

- This documents the current host AABB2 overlap C ABI contract.
- No OptiX, Embree, device-buffer query, frozen general query contract, or release claim is authorized.
