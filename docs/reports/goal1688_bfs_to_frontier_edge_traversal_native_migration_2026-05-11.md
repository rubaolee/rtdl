# Goal1688 BFS-To-Frontier-Edge-Traversal Native Migration (Narrow Slice)

Date: 2026-05-11

Status: fifth local source migration from app-shaped native terminology to
generic primitive terminology; narrow first slice of the
`frontier_edge_traversal` family classified by Goal1672.

Follow-up: Goal1690 completed the Apple RT remainder that this report
deliberately deferred. The historical Goal1688 counts below describe the
post-Goal1688/pre-Goal1690 state; the current superseding gap is recorded in
`docs/reports/goal1680_current_native_app_leakage_gap_2026-05-10.md`.

## Verdict

Eight of the ten `bfs`-shaped native callables/exports across Embree,
HIPRT, OptiX, Oracle, and Vulkan no longer carry the `bfs` term in their
ABI names. The native ABI now describes the operation as generic
frontier/edge traversal packets:

- `rtdl_embree_run_frontier_edge_traversal_packet`
- `rtdl_hiprt_run_frontier_edge_traversal_packet`
- `rtdl_hiprt_run_prepared_frontier_edge_traversal_packet`
- `rtdl_optix_run_frontier_edge_traversal_packet`
- `rtdl_oracle_run_frontier_edge_traversal_packet`
- `rtdl_oracle_summarize_frontier_traversal_rows`
- `rtdl_vulkan_run_frontier_edge_traversal_packet`

The HIPRT internal kernel filename hint string was renamed from
`rtdl_hiprt_bfs_expand.cu` to
`rtdl_hiprt_frontier_edge_traversal_packet.cu` so the strict native
scan no longer flags `rtdl_hiprt_bfs_expand`.

This is a local source migration only. It does not claim new
performance evidence, because no pod was used.

### Narrow-Slice Scope

The two Apple RT discover variants
(`rtdl_apple_rt_run_bfs_discover_compute` and the internal Metal kernel
function name `rtdl_bfs_discover`) are **deferred** to a later goal.
The Metal kernel source is embedded as a runtime string compiled through
`MTLLibrary`, and renaming the kernel function requires touching both
the embedded Metal source and the `[library newFunctionWithName:@"..."]`
lookup site. That belongs in its own narrow Apple RT slice rather than
in this five-backend rename.

## Boundary

The Python layer continues to expose its existing BFS helpers:

- `rt.run_embree(rtdl_graph_bfs.bfs_expand_kernel, **case)` and the
  example app `examples.rtdl_graph_bfs` keep their public Python
  surface — BFS semantics live in the Python expression layer, not in
  the native ABI;
- the ctypes binding strings in `embree_runtime.py`,
  `hiprt_runtime.py`, `optix_runtime.py`, `oracle_runtime.py`, and
  `vulkan_runtime.py` were repointed to the new generic native names
  inside the same migration commit;
- the Python ctypes row structures (`_RtdlBfsExpandRow`,
  `_RtdlFrontierVertex`, `_RtdlEdgeSeed`) are CamelCase types and are
  intentionally retained — the strict `\brtdl_<lowercase>_` regex does
  not flag CamelCase types.

`_run_frontier_edge_traversal_packet`,
`_run_prepared_frontier_edge_traversal_packet`, and
`_summarize_frontier_traversal_rows` were added to
`_GENERIC_NATIVE_SYMBOL_FRAGMENTS` in
`src/rtdsl/python_rtdl_app_purity.py` so the audit classifies the new
exports as generic primitive-shaped native ABI rather than as legacy
engine-customized.

## App-Agnostic Impact

Goal1672 classified the old `bfs`-shaped native symbols under
`frontier_edge_traversal`. This migration removes eight of the ten
symbols from the strict native release-surface scan by renaming them
into generic frontier/edge traversal packet language. The remaining
two `bfs`-flagged symbols (`rtdl_apple_rt_run_bfs_discover_compute` and
`rtdl_bfs_discover`) remain blocked for app-agnostic release claims and
are tracked in `docs/reports/goal1680_current_native_app_leakage_gap_2026-05-10.md`.

The broader app-agnostic gate still fails. Database (`db`),
polygon/GIS (`polygon`), KNN (`knn`), and the two pending Apple RT BFS
discover symbols remain and still block any full native app-agnostic
claim.

## Validation

Local validation:

```text
py -3 -m unittest tests.goal1603_v1_6_stable_native_path_app_leakage_audit_test \
  tests.goal1668_native_engine_app_agnostic_directive_test \
  tests.goal1672_native_app_leakage_migration_classification_test \
  tests.goal1676_native_leakage_delta_regression_test \
  tests.goal1680_current_native_app_leakage_gap_test \
  tests.goal1681_pip_to_point_primitive_anyhit_native_migration_test \
  tests.goal1682_hausdorff_to_max_distance_nearest_candidate_native_migration_test \
  tests.goal1688_bfs_to_frontier_edge_traversal_native_migration_test
py -3 -m py_compile src/rtdsl/embree_runtime.py src/rtdsl/hiprt_runtime.py \
  src/rtdsl/optix_runtime.py src/rtdsl/oracle_runtime.py \
  src/rtdsl/vulkan_runtime.py src/rtdsl/python_rtdl_app_purity.py
git diff --check
```

Current source audit:

- `src/native/embree/rtdl_embree_api.cpp`: no `_run_bfs_expand` term remains.
- `src/native/embree/rtdl_embree_prelude.h`: no `_run_bfs_expand` term remains.
- `src/native/hiprt/rtdl_hiprt_api.cpp`: no `_run_bfs_expand` or
  `_run_prepared_bfs_expand` term remains.
- `src/native/hiprt/rtdl_hiprt_core.cpp`: no `rtdl_hiprt_bfs_expand`
  kernel-filename hint remains.
- `src/native/optix/rtdl_optix_api.cpp`: no `_run_bfs_expand` term remains.
- `src/native/optix/rtdl_optix_prelude.h`: no `_run_bfs_expand` term remains.
- `src/native/oracle/rtdl_oracle_abi.h`: no `_run_bfs_expand` or
  `_summarize_bfs_rows` term remains.
- `src/native/oracle/rtdl_oracle_api.cpp`: no `_run_bfs_expand` or
  `_summarize_bfs_rows` term remains.
- `src/native/vulkan/rtdl_vulkan_api.cpp`: no `_run_bfs_expand` term remains.
- `src/native/vulkan/rtdl_vulkan_prelude.h`: no `_run_bfs_expand` term remains.

No pod validation was run. Native rebuild and runtime validation on a
host with each backend's prerequisites is the next evidence step before
treating this as hardware-proven.

## Counts Delta

Before Goal1688 (post-Goal1682):

| Measure | Count |
| --- | ---: |
| Strict regex unique symbols | 92 |
| Strict regex occurrences | 178 |
| Remaining app-shaped callable/export symbols | 83 |
| `bfs` family unique symbols | 10 |

After Goal1688:

| Measure | Count |
| --- | ---: |
| Strict regex unique symbols | 84 |
| Strict regex occurrences | 164 |
| Remaining app-shaped callable/export symbols | 75 |
| `bfs` family unique symbols | 2 (Apple RT discover, deferred) |

False-positive uppercase `RTDL_DB_*` constants are unchanged at 9 unique /
14 occurrences.

## Blocked Wording

Still blocked:

```text
RTDL native internals are fully app-agnostic.
```

Allowed wording after Goal1688:

```text
RTDL has migrated the BFS-expand and BFS-row-summary native exports
across Embree, HIPRT, OptiX, Oracle, and Vulkan into generic
frontier/edge traversal packet native exports; remaining app-shaped
native families (`db`, `polygon`, `knn`) and the two pending Apple RT
BFS discover symbols still block the full app-agnostic native-engine
release claim.
```

Superseding wording after Goal1690:

```text
RTDL has migrated the BFS-shaped native callable/export family to generic
frontier traversal and frontier discovery native terminology; remaining
app-shaped native families (`db`, `polygon`, and `knn`) still block the full
app-agnostic native-engine release claim.
```
