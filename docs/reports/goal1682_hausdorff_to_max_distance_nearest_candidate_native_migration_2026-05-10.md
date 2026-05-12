# Goal1682 Hausdorff-To-Max-Distance-Nearest-Candidate Native Migration

Date: 2026-05-10

Status: fourth local source migration from app-shaped native terminology to
generic primitive terminology; first migration of the
`app_level_distance_reduction` family classified by Goal1672.

## Verdict

The native Embree directed-Hausdorff entry point no longer exports a
`hausdorff`-shaped symbol. The native ABI now describes the operation as a
generic max-over-queries nearest-candidate reduction:

- `rtdl_embree_run_max_distance_nearest_candidate_2d`

Hausdorff semantics — directedness, witness-direction selection, exact vs.
threshold-decision distinction, public-wording boundaries — remain in the
Python `directed_hausdorff_2d_embree` helper in
`src/rtdsl/embree_runtime.py` and in the example app, not in the native
ABI.

This is a local source migration only. It does not claim new performance
evidence, because no pod was used.

## Boundary

The Python layer continues to expose the Hausdorff helper unchanged:

- `rt.directed_hausdorff_2d_embree(query_points, search_points)` keeps the
  same Python API and return shape (`distance`, `source_id`, `target_id`,
  `row_count`, `distance_reduction_rows`);
- the underlying ctypes binding now resolves
  `rtdl_embree_run_max_distance_nearest_candidate_2d` instead of
  `rtdl_embree_run_directed_hausdorff_2d`;
- the optional argtypes/restype configuration block in
  `_install_embree_argtypes` was renamed to
  `optional_max_distance_nearest_candidate_2d`;
- the C++ row struct `RtdlDirectedHausdorffRow` is unchanged; the strict
  native scan does not flag CamelCase types because the regex anchors on
  `\brtdl_<lowercase>_…`.

`_run_max_distance_nearest_candidate_2d` was added to
`_GENERIC_NATIVE_SYMBOL_FRAGMENTS` in
`src/rtdsl/python_rtdl_app_purity.py` so the audit classifies the new
export as generic primitive-shaped native ABI rather than as legacy
engine-customized.

## App-Agnostic Impact

Goal1672 classified the old `hausdorff`-shaped native symbol under
`app_level_distance_reduction`. This migration removes that single-symbol
family from the strict native release-surface scan by renaming the export
to generic max-distance nearest-candidate terminology and pushing the
Hausdorff semantics into Python.

The broader app-agnostic gate still fails. Database (`db`),
polygon/GIS (`polygon`), KNN (`knn`), and graph/BFS (`bfs`) app-shaped
native symbols remain and still block any full native app-agnostic claim.

## Validation

Local validation:

```text
py -3 -m unittest tests.goal1603_v1_6_stable_native_path_app_leakage_audit_test \
  tests.goal1668_native_engine_app_agnostic_directive_test \
  tests.goal1672_native_app_leakage_migration_classification_test \
  tests.goal1676_native_leakage_delta_regression_test \
  tests.goal1680_current_native_app_leakage_gap_test \
  tests.goal1681_pip_to_point_primitive_anyhit_native_migration_test \
  tests.goal1682_hausdorff_to_max_distance_nearest_candidate_native_migration_test
py -3 -m py_compile src/rtdsl/embree_runtime.py src/rtdsl/python_rtdl_app_purity.py
git diff --check
```

Current source audit:

- `src/native/embree/rtdl_embree_api.cpp`: no `hausdorff` term remains in
  any `\brtdl_…` lowercase symbol name; the only `Hausdorff` substring in
  the file is the unchanged CamelCase `RtdlDirectedHausdorffRow` row type.
- `src/native/embree/rtdl_embree_prelude.h`: the prelude declaration was
  renamed; only the CamelCase `RtdlDirectedHausdorffRow` row type retains
  the historical name.

No pod validation was run. Native rebuild and runtime validation on an
Embree host is the next evidence step before treating this as
hardware-proven.

## Counts Delta

Before Goal1682 (post-Goal1681):

| Measure | Count |
| --- | ---: |
| Strict regex unique symbols | 93 |
| Strict regex occurrences | 180 |
| Remaining app-shaped callable/export symbols | 84 |
| `hausdorff` family unique symbols | 1 |

After Goal1682:

| Measure | Count |
| --- | ---: |
| Strict regex unique symbols | 92 |
| Strict regex occurrences | 178 |
| Remaining app-shaped callable/export symbols | 83 |
| `hausdorff` family unique symbols | 0 |

False-positive uppercase `RTDL_DB_*` constants are unchanged at 9 unique /
14 occurrences.

## Blocked Wording

Still blocked:

```text
RTDL native internals are fully app-agnostic.
```

Allowed wording after Goal1682:

```text
RTDL has migrated the `hausdorff` directed-distance native export into a
generic max-distance nearest-candidate native export, with Hausdorff
semantics retained at the Python layer; remaining app-shaped native
families (`db`, `polygon`, `knn`, `bfs`) still block the full
app-agnostic native-engine release claim.
```
