# Goal4059 Direct Component-Size Signature Front Door

Status: local implementation, pod timing pending.

Goal4059 adds a generic signature-only continuation for prepared fixed-radius
graph components:

- lower adapter:
  `radius_graph_component_signature_3d_optix_numba_prepared_grouped_stream_partner_columns`;
- v2.8 front door:
  `fixed_radius_graph_component_size_signature_3d_v2_8`;
- RT-DBSCAN app route:
  Numba column-signature modes call the signature front door directly.

The v2.8 component-label front door still supports both CuPy and Numba. This
new signature-only front door is deliberately narrower: it only accepts an
explicitly prepared `partner="numba"` handle because the direct root-count
continuation is a Numba implementation.

The continuation reuses the existing app-agnostic OptiX grouped-union pass. It
then counts component roots directly from the parent workspace and optional
border-candidate workspace, producing `label_counts`, `flag_true_count`, and
`negative_label_count`.

## Why

Goal4056 removed host materialization from mixed-label signatures, but it still
ran the full component-label path first. Goal4059 gives signature-only users a
direct generic path that does not materialize component-label columns when the
caller only needs component-size summaries.

## Boundary

This does not add a DBSCAN native ABI, does not add app-specific native engine
logic, does not change the OptiX grouped-union primitive, does not choose a partner automatically, and does not authorize release, public speedup,
whole-app speedup, broad RT-core speedup, or true-zero-copy claims.

Expected app metadata for Numba column-signature mode:

- `column_signature_strategy: numba_direct_component_signature_counts`;
- `column_signature_uses_numba_direct_component_signature: true`;
- `materializes_component_labels: false`.
