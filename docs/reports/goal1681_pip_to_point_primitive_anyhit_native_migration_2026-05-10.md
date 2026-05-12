# Goal1681 PIP-To-Point-Primitive-Anyhit Native Migration

Date: 2026-05-10

Status: third local source migration from app-shaped native terminology to
generic primitive terminology; first migration of the
`generic_geometry_anyhit` family classified by Goal1672.

## Verdict

The native PIP (point-in-polygon) entry points across all backends no longer
export `pip`-shaped symbols. The native ABI now describes the operation as
generic point/primitive any-hit packets:

- `rtdl_embree_run_point_primitive_anyhit_packet`
- `rtdl_hiprt_run_point_primitive_anyhit_packet`
- `rtdl_optix_run_point_primitive_anyhit_packet`
- `rtdl_oracle_run_point_primitive_anyhit_packet`
- `rtdl_vulkan_run_point_primitive_anyhit_packet`

The HIPRT internal kernel filename hint was renamed from
`rtdl_hiprt_pip_2d.cu` to `rtdl_hiprt_point_primitive_anyhit_2d.cu` so the
strict native scan no longer flags `rtdl_hiprt_pip_2d`.

This is a local source migration only. It does not claim new performance
evidence, because no pod was used and the OptiX SDK headers and
`librtdl_optix.so` remained unavailable at the time of the migration.

## Boundary

The Python layer continues to call into the renamed exports via
`embree_runtime.py`, `hiprt_runtime.py`, `optix_runtime.py`,
`oracle_runtime.py`, and `vulkan_runtime.py`. The high-level
point-in-polygon Python API (`_run_pip_*`, `_run_pip` in
`python_rtdl_app_purity.py`) still exists at the Python layer and continues
to express point-in-polygon semantics; the native ABI no longer encodes the
`pip` term.

`_run_point_primitive_anyhit_packet` was added to
`_GENERIC_NATIVE_SYMBOL_FRAGMENTS` in
`src/rtdsl/python_rtdl_app_purity.py` so the audit classifies the new
exports as generic primitive-shaped native ABI rather than as legacy
engine-customized.

## App-Agnostic Impact

Goal1672 classified the old PIP-shaped native symbols under
`generic_geometry_anyhit`. This migration removes that family from the
strict native release-surface scan by renaming the six callables/exports
into generic point/primitive any-hit packet language.

The broader app-agnostic gate still fails. Database, graph, polygon/GIS,
KNN, and Hausdorff app-shaped native symbols remain and still block any
full native app-agnostic claim.

## Validation

Local validation:

```text
py -3 -m unittest tests.goal1603_v1_6_stable_native_path_app_leakage_audit_test \
  tests.goal1672_native_app_leakage_migration_classification_test \
  tests.goal1673_optix_pose_to_group_native_migration_test \
  tests.goal1676_native_leakage_delta_regression_test \
  tests.goal1680_current_native_app_leakage_gap_test \
  tests.goal1681_pip_to_point_primitive_anyhit_native_migration_test
py -3 -m py_compile src/rtdsl/embree_runtime.py src/rtdsl/hiprt_runtime.py \
  src/rtdsl/optix_runtime.py src/rtdsl/oracle_runtime.py \
  src/rtdsl/vulkan_runtime.py src/rtdsl/python_rtdl_app_purity.py
git diff --check
```

Current source audit:

- `src/native/embree/rtdl_embree_api.cpp`: no `_run_pip` term remains.
- `src/native/embree/rtdl_embree_prelude.h`: no `_run_pip` term remains.
- `src/native/hiprt/rtdl_hiprt_api.cpp`: no `_run_pip` term remains.
- `src/native/hiprt/rtdl_hiprt_core.cpp`: no `rtdl_hiprt_pip_2d` filename
  hint remains.
- `src/native/optix/rtdl_optix_api.cpp`: no `_run_pip` term remains.
- `src/native/optix/rtdl_optix_prelude.h`: no `_run_pip` term remains.
- `src/native/oracle/rtdl_oracle_abi.h`: no `_run_pip` term remains.
- `src/native/oracle/rtdl_oracle_api.cpp`: no `_run_pip` term remains.
- `src/native/vulkan/rtdl_vulkan_api.cpp`: no `_run_pip` term remains.
- `src/native/vulkan/rtdl_vulkan_prelude.h`: no `_run_pip` term remains.

No pod validation was run. Native rebuild and runtime validation on a host
with each backend's prerequisites (Embree, HIPRT, OptiX SDK, Oracle/CPU,
Vulkan) is the next evidence step before treating this as
hardware-proven.

## Counts Delta

Before Goal1681 (post-Goal1673/Goal1674):

| Measure | Count |
| --- | ---: |
| Strict regex unique symbols | 99 |
| Strict regex occurrences | 190 |
| Remaining app-shaped callable/export symbols | 90 |
| `pip` family unique symbols | 6 |

After Goal1681:

| Measure | Count |
| --- | ---: |
| Strict regex unique symbols | 93 |
| Strict regex occurrences | 180 |
| Remaining app-shaped callable/export symbols | 84 |
| `pip` family unique symbols | 0 |

False-positive uppercase `RTDL_DB_*` constants are unchanged at 9 unique /
14 occurrences.

## Blocked Wording

Still blocked:

```text
RTDL native internals are fully app-agnostic.
```

Allowed wording after Goal1681:

```text
RTDL has migrated the `pip` / point-in-polygon native exports into generic
point/primitive any-hit packet exports; remaining app-shaped native
families (`db`, `polygon`, `knn`, `bfs`, `hausdorff`) still block the full
app-agnostic native-engine release claim.
```
