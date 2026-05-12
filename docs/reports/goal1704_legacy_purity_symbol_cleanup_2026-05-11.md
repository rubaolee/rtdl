# Goal1704 Legacy Purity Symbol Cleanup

Date: 2026-05-11

## Verdict

The six legacy purity symbols are now generic at the native ABI and Python
binding boundary.

This goal removes the non-strict blocker set identified by Goal1702:

| Old native name | New native name |
| --- | --- |
| `rtdl_embree_run_lsi` | `rtdl_embree_run_segment_pair_intersection` |
| `rtdl_optix_run_lsi` | `rtdl_optix_run_segment_pair_intersection` |
| `rtdl_embree_run_overlay` | `rtdl_embree_run_shape_pair_relation_flags` |
| `rtdl_optix_run_overlay` | `rtdl_optix_run_shape_pair_relation_flags` |
| `rtdl_embree_run_triangle_probe` | `rtdl_embree_run_edge_neighbor_intersection_packet` |
| `rtdl_optix_run_triangle_probe` | `rtdl_optix_run_edge_neighbor_intersection_packet` |

Python-facing compatibility names remain unchanged. LSI, overlay, and triangle
probe semantics still live at the Python/app orchestration layer; the native
engine ABI now describes generic segment-pair intersection, shape-pair relation
flags, and edge-neighbor intersection packets.

## Purity Audit

`native_symbol_purity_audit(repo_root=...)` now reports zero
`legacy_engine_customized_symbols`. The product checkpoint still remains
fail-closed because experimental/app-level product blockers and release
validation requirements remain.

The strict tracked-family scan remains `9/14/0`:

- strict regex unique symbols: `9`
- strict regex occurrences: `14`
- known uppercase `RTDL_DB_*` false-positive symbols: `9`
- known uppercase `RTDL_DB_*` false-positive occurrences: `14`
- real lowercase app-shaped callable/export symbols: `0`

## Expanded-Term Boundary

The `table` and `column` expanded-term findings from Goal1702 are not fully
closed by this goal.

Current disposition:

- HIPRT `hiprtFuncTable table` occurrences are SDK structural terminology, not
  RTDL app semantics.
- OptiX row-width `column` loops are generic row-buffer indexing.
- Apple RT `column index` messages are CSR adjacency/edge-array structural
  checks.
- Embree/OptiX/Vulkan columnar-payload internals still contain DB-era type and
  variable names such as `RtdlDbColumn`, `column_count`, and DB-shaped error
  messages. These require a separate expanded semantic cleanup if the release
  gate requires zero internal `table`/`column` vocabulary.

## Release Boundary

This is source and Python-binding evidence only. No pod or hardware validation
was run.

The absolute release claim remains blocked and must still be treated as
`needs-more-evidence`:

```text
RTDL native internals are fully app-agnostic.
```

Allowed wording:

```text
The strict tracked-family ABI cleanup and the six legacy purity-symbol ABI
renames are locally complete. Release readiness remains blocked pending the
expanded semantic cleanup decision, independent review, and pod/hardware
validation.
```
