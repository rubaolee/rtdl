# Goal1758 Legacy LSI / Overlay / Triangle-Probe Native Cleanup

Date: 2026-05-12

## Verdict

`legacy_app_shaped_native_support_migrated_to_generic_terms`

The remaining legacy native app-shaped support symbols identified after
Goal1757 have been migrated across Apple RT, HIPRT, Oracle, and Vulkan.
The cleanup also removes the old `lsi`, `overlay`, and `triangle_probe`
source vocabulary from `src/native/**`, keeping the public Python
compatibility layer intact.

## Native ABI Renames

| Backend | Old native name | New native name |
| --- | --- | --- |
| Apple RT | `rtdl_apple_rt_run_lsi` | `rtdl_apple_rt_run_segment_pair_intersection` |
| HIPRT | `rtdl_hiprt_run_lsi` | `rtdl_hiprt_run_segment_pair_intersection` |
| HIPRT | `rtdl_hiprt_run_overlay` | `rtdl_hiprt_run_shape_pair_relation_flags` |
| HIPRT | `rtdl_hiprt_run_triangle_probe` | `rtdl_hiprt_run_triangle_cycle_candidates` |
| HIPRT | `rtdl_hiprt_run_prepared_triangle_probe` | `rtdl_hiprt_run_prepared_triangle_cycle_candidates` |
| HIPRT kernel hint | `rtdl_hiprt_lsi_2d` | `rtdl_hiprt_segment_pair_intersection_2d` |
| HIPRT kernel hint | `rtdl_hiprt_overlay_2d` | `rtdl_hiprt_shape_pair_relation_flags_2d` |
| HIPRT kernel hint | `rtdl_hiprt_triangle_probe` | `rtdl_hiprt_triangle_cycle_candidates` |
| Oracle | `rtdl_oracle_run_lsi` | `rtdl_oracle_run_segment_pair_intersection` |
| Oracle | `rtdl_oracle_run_overlay` | `rtdl_oracle_run_shape_pair_relation_flags` |
| Oracle | `rtdl_oracle_run_triangle_probe` | `rtdl_oracle_run_triangle_cycle_candidates` |
| Vulkan | `rtdl_vulkan_run_lsi` | `rtdl_vulkan_run_segment_pair_intersection` |
| Vulkan | `rtdl_vulkan_run_overlay` | `rtdl_vulkan_run_shape_pair_relation_flags` |
| Vulkan | `rtdl_vulkan_run_triangle_probe` | `rtdl_vulkan_run_triangle_cycle_candidates` |

## Internal Native Terminology

The native implementation vocabulary was also tightened:

- `RtdlLsiRow` -> `RtdlSegmentPairIntersectionRow`
- `RtdlOverlayRow` -> `RtdlShapePairRelationRow`
- `GpuLsiRecord` -> `GpuSegmentPairIntersectionRecord`
- `GpuOverlayFlags` -> `GpuShapePairRelationFlags`
- `LsiQueryState` -> `SegmentPairIntersectionQueryState`
- `OverlayQueryState` -> `ShapePairRelationQueryState`
- `triangle_probe` helpers -> `triangle_cycle_candidates` helpers

Public Python workload names such as `lsi`, `overlay`, and
`triangle_match` remain compatibility-level app semantics. They now bind
to generic native exports.

## Source Scan

Post-cleanup source scan over `src/native/**`:

- old lower-case native ABI hits for `lsi`, `overlay`, `triangle_probe`: `0`
- old source vocabulary hits for `lsi`, `overlay`, `triangle_probe`, `Lsi`,
  `Overlay`, `LSI`: `0`
- replacement generic native symbols present across the affected backends:
  `segment_pair_intersection`, `shape_pair_relation_flags`, and
  `triangle_cycle_candidates`

## Validation

- `py -3 -m py_compile` passed for the touched Python runtime files:
  Apple RT, HIPRT, Oracle, Vulkan, and `python_rtdl_app_purity.py`.
- Focused native leakage gate passed:
  `tests.goal1603_v1_6_stable_native_path_app_leakage_audit_test`,
  `tests.goal1668_native_engine_app_agnostic_directive_test`,
  `tests.goal1676_native_leakage_delta_regression_test`,
  `tests.goal1680_current_native_app_leakage_gap_test`,
  `tests.goal1704_legacy_purity_symbol_cleanup_test`,
  `tests.goal1708_source_recovery_and_semantic_cleanup_test`.
- Local Linux Embree build passed on `192.168.1.20`:
  `make build-embree` reported `Embree 4.3.0`.

## Boundary

This is source, Python-binding, scan, and Embree build evidence. It is not
pod/hardware evidence for every backend. HIPRT, Vulkan, Apple RT, and
OptiX full hardware/toolchain validation still require their respective
SDK/platform environments.

The specific blocker identified in Goal1757 is resolved: the multi-backend
native tree no longer carries the older lower-case `lsi`, `overlay`, or
`triangle_probe` app-shaped native support symbols.
