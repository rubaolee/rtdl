# Goal1716 Goal1659 Current Pod Rows After GEOS and Graph Binding Fix

Date: 2026-05-12

Status: current-version Goal1659 active pod-row execution evidence.

## Context

Goal1714 validated source recovery, Embree/OptiX builds, smoke tests, and the
Goal1659/Goal1660 manifest gates on the RTX 4000 Ada pod. The next release
evidence layer was to run the 16 active Goal1659 current-version pod rows.

The pod workspace was:

```text
/workspace/rtdl_goal1714
```

The pod hardware was:

```text
NVIDIA RTX 4000 Ada Generation
driver 550.163.01
CUDA 12.8
OptiX SDK v8.0.0
```

## Fixes Needed Before The Matrix Could Run

The first Goal1659 row attempt showed a shared dynamic-load failure:

```text
OSError: /workspace/rtdl_goal1714/build/librtdl_optix.so: undefined symbol: GEOSPreparedGeom_destroy_r
```

The pod had `libgeos_c.so`, but no `pkg-config`. The Makefile had depended on
`pkg-config --libs geos`, so `GEOS_LIBS` was empty and `librtdl_optix.so` was
built without a GEOS C API dependency.

The Makefile was updated to prefer `geos-c`, fall back to `geos`, and finally
fall back to `-lgeos_c` when `/usr/lib/x86_64-linux-gnu/libgeos_c.so` exists.
The Python dynamic build helpers in `src/rtdsl/embree_runtime.py` and
`src/rtdsl/oracle_runtime.py` were aligned to prefer `geos_c` before `geos` as
well, preserving the same GEOS C API fallback behavior outside the Makefile
path.

After copying the patched Makefile to the pod, the OptiX rebuild linked GEOS C:

```bash
make build-optix OPTIX_PREFIX=/opt/optix CUDA_PREFIX=/usr/local/cuda CUDA_LIB=/usr/local/cuda/targets/x86_64-linux/lib NVCC=/usr/local/cuda/bin/nvcc
```

The link line included:

```text
-L/usr/local/cuda/targets/x86_64-linux/lib -lcuda -lnvrtc -lgeos_c
```

`ldd build/librtdl_optix.so` then reported:

```text
libgeos_c.so.1 => /lib/x86_64-linux-gnu/libgeos_c.so.1
libgeos.so.3.12.1 => /lib/x86_64-linux-gnu/libgeos.so.3.12.1
```

A small fixed-radius OptiX probe passed after this link fix and wrote:

```text
docs/reports/goal1716_probe_outlier_after_geos_link.json
```

The second issue was isolated to the graph row. The graph OptiX gate still used
the stale Python keyword:

```text
PackedGraphCSR(..., column_index_count=...)
```

after the app-agnostic native migration had renamed that packet field to:

```text
field_index_count
```

`src/rtdsl/optix_runtime.py` was updated to construct `PackedGraphCSR` with
`field_index_count=len(normalized.column_indices)`. A focused graph gate then
passed on the pod:

```bash
PYTHONPATH=src:. /usr/bin/python3 scripts/goal889_graph_visibility_optix_gate.py \
  --copies 20000 \
  --output-mode summary \
  --validation-mode analytic_summary \
  --chunk-copies 0 \
  --strict \
  --output-json docs/reports/goal1716_graph_visibility_optix_after_binding_fix.json
```

Result:

```text
{"output_json": "docs/reports/goal1716_graph_visibility_optix_after_binding_fix.json", "status": "pass", "strict_pass": true}
```

## Goal1659 Current Pod Rows

The 16 active Goal1659 current-version pod rows were then rerun on the same pod
with:

```text
PATH=/usr/local/cuda/bin:/usr/bin:/bin
LD_LIBRARY_PATH=/workspace/rtdl_goal1714/build:/usr/lib/x86_64-linux-gnu:/usr/local/cuda/targets/x86_64-linux/lib:/usr/local/cuda/lib64
PYTHONPATH=src:.
```

The raw runner summary is:

```text
docs/reports/goal1716_goal1659_current_pod_rows_raw_2026-05-12.json
docs/reports/goal1716_goal1659_current_pod_rows_raw_2026-05-12.log
```

The final clean run completed every active row:

```text
completed_count: 16
entry_count: 16
failures: []
```

Per-row results:

| App | Return Code | Artifact |
| --- | ---: | --- |
| `database_analytics` | 0 | `docs/reports/goal1659_db_sales_risk_optix.json` |
| `graph_analytics` | 0 | `docs/reports/goal1659_graph_visibility_optix.json` |
| `service_coverage_gaps` | 0 | `docs/reports/goal1659_service_coverage_optix.json` |
| `event_hotspot_screening` | 0 | `docs/reports/goal1659_event_hotspot_optix.json` |
| `facility_knn_assignment` | 0 | `docs/reports/goal1659_facility_coverage_optix.json` |
| `road_hazard_screening` | 0 | `docs/reports/goal1659_road_hazard_optix.json` |
| `segment_polygon_hitcount` | 0 | `docs/reports/goal1659_segment_polygon_hitcount_optix.json` |
| `segment_polygon_anyhit_rows` | 0 | `docs/reports/goal1659_segment_polygon_anyhit_rows_optix.json` |
| `polygon_pair_overlap_area_rows` | 0 | `docs/reports/goal1659_pair_overlap_optix.json` |
| `polygon_set_jaccard` | 0 | `docs/reports/goal1659_jaccard_optix.json` |
| `hausdorff_distance` | 0 | `docs/reports/goal1659_hausdorff_threshold_optix.json` |
| `ann_candidate_search` | 0 | `docs/reports/goal1659_ann_candidate_optix.json` |
| `outlier_detection` | 0 | `docs/reports/goal1659_outlier_fixed_radius_optix.json` |
| `dbscan_clustering` | 0 | `docs/reports/goal1659_dbscan_fixed_radius_optix.json` |
| `robot_collision_screening` | 0 | `docs/reports/goal1659_robot_pose_count_optix.json` |
| `barnes_hut_force_app` | 0 | `docs/reports/goal1659_barnes_hut_node_coverage_optix.json` |

The graph row's final artifact reports:

```text
status: pass
strict_pass: true
optix_native_graph_ray_bfs: status ok, parity_vs_analytic_expected true
optix_native_graph_ray_triangle_count: status ok, parity_vs_analytic_expected true
```

## Verdict

The Goal1659 active current-version pod row rule is now satisfied for this pod
run:

```text
all 16 active current-version pod rows completed and wrote artifacts
```

This is accepted RTX pod evidence for current-version Goal1659 row execution
after source recovery and the app-agnostic native migration.

## Boundary

This does not complete the full v1.6.11 release process by itself.

It is current-version pod evidence, not a full v1.6.11-versus-v1.0 timed
cross-version performance comparison. Goal1660's manifest gate now passes when
`.git` metadata and the `v1.0` tag are present, but the timed v1.0 baseline rows
still need to be run from an appropriate tagged checkout before public
cross-version speedup wording or release/tag action is authorized.

Release readiness remains:

```text
needs-more-evidence
```
