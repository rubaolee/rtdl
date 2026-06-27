# V4 Goal4749 Final Same-Semantics RT-Core Protocol

Status: `goal4749_final_same_semantics_rt_core_protocol_frozen_not_run`

This freezes the final V4.0 benchmark protocol before the full POD matrix.
It supersedes older V2-vs-V4-only matrices for release evidence.

## Hard Rules

- Primary performance denominators must be NVIDIA OptiX/RT-core routes, not Embree.
- No user-facing `n/a` rows are allowed.
- V4.0 is a V2.14/V3.0.2 superset release line.
- Correctness parity is required before speed credit.
- Inherited compatibility is support; it is not automatically V4-new speedup.

## App Rows

| App | Semantic Contract | V4.0 Status | V4.0 Support Class |
| --- | --- | --- | --- |
| rt_dbscan | fixed-radius count-threshold neighbors plus component labels | runnable_protocol_template | v4_inherited_compatibility_plus_new_operator |
| raydb_style | ray/triangle primitive grouped i64 count/sum reduction | runnable_protocol_template | v4_inherited_compatibility_plus_new_operator |
| triangle_counting | graph triangle/cycle count lowered to ray-triangle weighted any-hit sum | runnable_protocol_template | v4_inherited_compatibility_plus_new_operator |
| librts_spatial_index | prepared AABB spatial index query count/all-ops | runnable_protocol_template | v4_inherited_compatibility_plus_new_operator |
| hausdorff_xhd | directed Hausdorff threshold-decision RT-core route for three-version fairness | runnable_protocol_template | v4_inherited_compatibility_plus_new_operator |
| robot_collision | prepared any-hit collision flags/count | runnable_protocol_template | v4_superset_inherited_compatibility |
| contact_manifold | bounded contact/witness collect-k route with fail-closed output semantics | runnable_protocol_template | v4_superset_inherited_compatibility |
| rtnn | fixed-radius ranked nearest-summary aggregate | runnable_protocol_template | v4_inherited_compatibility_plus_new_operator |
| spatial_rayjoin | relation/topology rayjoin counts using prepared point/shape/segment RT-core primitives | runnable_protocol_template | v4_superset_inherited_compatibility |
| barnes_hut | aggregate-frontier membership plus weighted vector continuation | runnable_protocol_template | v4_inherited_compatibility_plus_new_operator |

## V4.0 Repair Rows Before Final Matrix

- None.

## Validation

- status: `passed`
- error_count: `0`

## Next

Goal4750 builds the unified dry-run/POD runner from this protocol. Goal4753 runs the final matrix.
