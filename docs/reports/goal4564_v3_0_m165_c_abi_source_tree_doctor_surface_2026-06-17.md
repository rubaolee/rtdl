# Goal4564 / V3 M165 C ABI Source-Tree Doctor Surface

Status: `c_abi_source_tree_doctor_surface_checked`

## Conclusion

Goal4564 wires the V3 C ABI embedding surface into the source-tree doctor as a required layout/entrypoint check. The doctor now verifies that the public header, source implementation, Makefile target, and embedding example are discoverable, while still leaving actual library builds and runtime validation to the dedicated C ABI evidence packets.

## Checks

| Check | Passed |
| --- | --- |
| `doctor_ok` | `True` |
| `c_abi_surface_check_present` | `True` |
| `c_abi_surface_check_passes` | `True` |
| `c_abi_surface_detail_names_header` | `True` |
| `c_abi_surface_detail_names_make_target` | `True` |
| `doctor_checks_header_source_make_and_example` | `True` |
| `doctor_doc_explains_c_abi_surface_boundary` | `True` |
| `process_doc_current_goal_span_refreshed` | `True` |
| `required_failures_empty` | `True` |

## Boundary

- The doctor checks source-tree files and entrypoints only.
- It does not build the C ABI shared library or execute runtime/benchmark code.
- No release or stable-ABI wording is authorized.
