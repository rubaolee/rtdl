# Goal4420 / V3.0 M23 DBSCAN component-label bridge

Status: `accept-with-boundary`

M23 carries the existing generic fixed-radius graph component front door into the current DBSCAN app. The new app backend is `optix_grouped_stream_components`: DBSCAN's 2D point fixture is lifted to generic 3D point rows with `z=0`, RTDL/OptiX runs the prepared grouped-stream component-label route, and the selected partner owns the device columns consumed by app-level label densification and validation.

This is an internal V3 integration step, not a public speedup claim.

## What Changed

| Piece | Result |
|---|---|
| App backend | `optix_grouped_stream_components` in `rtdl_dbscan_clustering_app.py`. |
| RTDL primitive | `prepare_v2_8_fixed_radius_graph_component_continuation_3d` plus `fixed_radius_graph_component_labels_3d_v2_8`. |
| Partners | CuPy and Numba: CuPy as the practical CUDA partner and Numba as the no-C++/no-RawKernel reference. |
| App logic | 2D-to-3D lifting, label densification, DBSCAN row schema, and oracle validation stay in the app layer. |
| Boundary | This is not a DBSCAN-specific native engine ABI, callback, or hidden partner selection. |

## Pod Evidence

Artifacts:

```text
docs/reports/goal4420_v3_0_m23_dbscan_component_bridge_65536_2026-06-15.json
docs/reports/goal4420_v3_0_m23_dbscan_component_bridge_524288_2026-06-15.json
```

Hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.08, 20 GB.

Commands:

```bash
python scripts/v3_0_m23_dbscan_component_bridge_measure.py \
  --copies 8192 \
  --warmups 2 \
  --repeats 5 \
  --numba-cuda-home /tmp/rtdl_cuda124_home \
  --output docs/reports/goal4420_v3_0_m23_dbscan_component_bridge_65536_2026-06-15.json

python scripts/v3_0_m23_dbscan_component_bridge_measure.py \
  --copies 65536 \
  --warmups 1 \
  --repeats 3 \
  --numba-cuda-home /tmp/rtdl_cuda124_home \
  --output docs/reports/goal4420_v3_0_m23_dbscan_component_bridge_524288_2026-06-15.json
```

| Points | Partner | Hot component-label median | Post-window row materialization | Prepare | Oracle | Cluster signature |
|---:|---|---:|---:|---:|---|---|
| 65,536 | CuPy | 0.000376s | 0.147479s | 1.137162s | matched | 8,192 clusters of 3 and 8,192 clusters of 4 |
| 65,536 | Numba | 0.000484s | 0.164367s | 0.455952s | matched | same |
| 524,288 | CuPy | 0.000679s | 0.775733s | 2.085866s | matched | 65,536 clusters of 3 and 65,536 clusters of 4 |
| 524,288 | Numba | 0.000679s | 0.764361s | 1.584229s | matched | same |

Both scale rows passed:

```text
all_match_oracle: true
cluster_size_signatures_match: true
core_counts_match: true
noise_counts_match: true
native_continuation_active: true
rt_core_accelerated: true
public_claim_authorized: false
```

## Interpretation

The DBSCAN app now has a real RTDL+partner route for full cluster labels, not only core-count/core-flag summaries. The hot prepared grouped-stream component-label operation is sub-millisecond at both 65,536 and 524,288 points on this tiled workload. The visible app cost is now the intentionally post-window Python row materialization needed to emit the traditional DBSCAN row schema.

That distinction matters: M23 validates the V3 design goal that the generic RTDL primitive can feed app-owned DBSCAN semantics through explicit partners. It does not yet prove that the public app should materialize Python rows for performance reporting. A future production-facing DBSCAN path should prefer a compact device-side component-size signature or downstream device consumer when the user does not need every row in Python.

## Allowed Wording

The DBSCAN app now has an internal V3 route that uses the generic RTDL/OptiX fixed-radius graph component front door and explicit CuPy or Numba partner continuation to produce DBSCAN cluster rows.

## Forbidden Wording

Do not claim public speedup, broad RT-core superiority, whole-app acceleration, true zero-copy, automatic partner selection, or a DBSCAN-specific native engine implementation from this milestone.
