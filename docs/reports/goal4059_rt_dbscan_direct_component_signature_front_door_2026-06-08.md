# Goal4059 Direct Component-Size Signature Front Door

Status: implemented, local tests pass, RTX 4000 Ada pod probe recorded.

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

## Pod Evidence

Artifact:
`docs/reports/goal4059_direct_numba_component_signature_front_door_pod_probe.json`.

Environment: RTX 4000 Ada pod, commit `16be56b7`.

Validation:

- `road3d`, 1024 points, threshold 64: `matches_reference: true`;
- strategy: `numba_direct_component_signature_counts`;
- `materializes_component_labels: false`;
- `rt_core_accelerated: true`.

Timing rows:

| Dataset | Points | Threshold | Elapsed sec | Adapter sec | Signature sec | All core | Labels materialized |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `road3d` | 4,096 | 64 | 0.001565 | 0.001108 | 0.000456 | false | false |
| `clustered3d` | 65,536 | 12 | 0.093696 | 0.088825 | 0.004870 | true | false |

The 65,536-point row is a diagnostic comparison against the prior same-pod
Goal4056/4057 label-count route (`0.100937s`), giving `1.077x`. That is useful
engineering evidence that avoiding label materialization helps this path, but
it is not a release, paper, whole-app, broad RT-core, or true-zero-copy claim.
