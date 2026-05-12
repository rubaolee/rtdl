# Goal1695 KNN-To-K-Closest-Hits Native Migration

Date: 2026-05-11

Status: seventh local source migration from app-shaped native terminology to
generic primitive terminology; completes the `bounded_nearest_candidate_collection`
family classified by Goal1672.

## Verdict

KNN family is now zero in the strict real native app-shaped symbol scan.

Goal1695 migrated the fourteen KNN-shaped native ABI names across Embree,
OptiX, Oracle, and Vulkan to generic `k_closest_hits` terminology:

| Old native name | New native name |
| --- | --- |
| `rtdl_embree_knn_rows_2d_create` | `rtdl_embree_k_closest_hits_2d_create` |
| `rtdl_embree_knn_rows_2d_run` | `rtdl_embree_k_closest_hits_2d_run` |
| `rtdl_embree_knn_rows_2d_destroy` | `rtdl_embree_k_closest_hits_2d_destroy` |
| `rtdl_embree_run_knn_rows` | `rtdl_embree_run_k_closest_hits` |
| `rtdl_embree_run_knn_rows_3d` | `rtdl_embree_run_k_closest_hits_3d` |
| `rtdl_optix_run_knn_rows` | `rtdl_optix_run_k_closest_hits` |
| `rtdl_optix_run_knn_rows_3d` | `rtdl_optix_run_k_closest_hits_3d` |
| `rtdl_oracle_run_knn_rows` | `rtdl_oracle_run_k_closest_hits` |
| `rtdl_oracle_run_knn_rows_3d` | `rtdl_oracle_run_k_closest_hits_3d` |
| `rtdl_oracle_run_bounded_knn_rows` | `rtdl_oracle_run_bounded_k_closest_hits` |
| `rtdl_oracle_run_bounded_knn_rows_3d` | `rtdl_oracle_run_bounded_k_closest_hits_3d` |
| `rtdl_oracle_summarize_knn_rows` | `rtdl_oracle_summarize_k_closest_hits` |
| `rtdl_vulkan_run_knn_rows` | `rtdl_vulkan_run_k_closest_hits` |
| `rtdl_vulkan_run_knn_rows_3d` | `rtdl_vulkan_run_k_closest_hits_3d` |

The Vulkan embedded shader names were also renamed from `knn.comp` and
`knn3d.comp` to `k_closest_hits.comp` and `k_closest_hits3d.comp`.

This is a local source migration only. It does not claim new performance
evidence, because no pod was used and no native hardware validation was run for
this local slice.

## Compatibility Boundary

Python-facing KNN semantics remain in Python:

- `knn_rows` and `bounded_knn_rows` remain DSL predicate names;
- `prepare_embree_knn_rows_2d` remains the prepared Embree helper;
- `_run_knn_rows_*`, `_call_knn_rows_*`, and bounded variants remain Python
  compatibility helpers;
- `_RtdlKnnNeighborRow` remains the Python ctypes row shape;
- only the native ABI strings and binding targets changed to
  `k_closest_hits` names.

The native ABI now describes generic k-closest candidate collection, while KNN
meaning stays at the Python expression layer.

`_run_k_closest_hits`, `_run_bounded_k_closest_hits`, `_k_closest_hits_2d`, and
`_summarize_k_closest_hits` are present in `_GENERIC_NATIVE_SYMBOL_FRAGMENTS`.
The old `_run_knn_rows`, `_knn_rows_`, `_bounded_knn_rows`, and
`_summarize_knn_rows` fragments are retained as app-shaped guards against
reintroducing KNN-named native ABI.

## Counts Delta

Before Goal1695 (post-Goal1690):

| Measure | Count |
| --- | ---: |
| Strict regex unique symbols | 82 |
| Strict regex occurrences | 159 |
| Remaining app-shaped callable/export symbols | 73 |
| `knn` family unique symbols | 14 |

After Goal1695:

| Measure | Count |
| --- | ---: |
| Strict regex unique symbols | 68 |
| Strict regex occurrences | 131 |
| Known uppercase `RTDL_DB_*` constant false-positive symbols | 9 |
| Known uppercase `RTDL_DB_*` constant false-positive occurrences | 14 |
| Remaining app-shaped callable/export symbols | 59 |
| `knn` family unique symbols | 0 |

Remaining real app-shaped native callable/export families:

| Family term | Unique symbols |
| --- | ---: |
| `db` | 30 |
| `polygon` | 29 |

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src'
py -3 -m unittest tests.goal1695_knn_to_k_closest_hits_native_migration_test
```

No pod validation was run. Native rebuild and runtime validation on Embree,
OptiX, Oracle, and Vulkan remain future evidence, not a claim made by this
report.

## Blocked Wording

Still blocked:

```text
RTDL native internals are fully app-agnostic.
```

Allowed wording after Goal1695:

```text
RTDL has migrated the KNN-shaped native callable/export family to generic
k-closest-hit candidate terminology. Remaining app-shaped native families
(`db` and `polygon`) still block the full app-agnostic native-engine release
claim.
```
