# Goal4579 / V3 M180 C ABI Direct-Link Example

Status: `c_abi_direct_link_example_checked`

## Conclusion

Goal4579 promotes the direct-link C ABI smoke into a real source-tree example and stages it with `make stage-c-api`. The pod evidence compiles the staged example with the staged pkg-config metadata and runs it against the staged library. This remains a draft source-tree embedding example, not a packaged SDK or stable ABI claim.

## Smoke

- OK: `True`
- Output: `direct_link_ok 0.1.3 ok`

## Checks

| Check | Passed |
| --- | --- |
| `direct_link_example_exists` | `True` |
| `example_uses_public_header_and_capability_queries` | `True` |
| `example_creates_and_destroys_context` | `True` |
| `makefile_stages_direct_link_example` | `True` |
| `staging_contract_documents_direct_link_example` | `True` |
| `embedding_readme_documents_direct_link_example` | `True` |
| `stage_bundle_smoke_ok` | `True` |
| `pkg_config_available` | `True` |
| `cc_available` | `True` |
| `staged_direct_link_example_compiles` | `True` |
| `staged_direct_link_example_runs` | `True` |

## Boundary

- This validates a staged direct-link C example only.
- No packaged SDK, stable ABI, general backend query, generated language binding, or release claim is authorized.
