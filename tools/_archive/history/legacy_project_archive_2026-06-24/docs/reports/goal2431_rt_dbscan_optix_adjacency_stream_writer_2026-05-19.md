# Goal2431 RT-DBSCAN Generic OptiX Adjacency Stream Writer

Date: 2026-05-19

Status: implemented and pod-smoked, with boundary.

## Purpose

Goal2430 proved that a prepared device-resident directed radius-graph adjacency
stream is a useful generic continuation substrate for RT-DBSCAN-style workloads:
once the stream exists, CuPy grouped-union labeling avoids repeated radius-grid
candidate traversal. Goal2431 tests the next architecture step: can the OptiX
RTDL backend write that same generic adjacency stream into caller-owned partner
device columns without adding a DBSCAN-specific native ABI?

Answer: yes. This closes the architecture gap, but it is not yet the final
performance leap.

## What Changed

Native OptiX now exports:

- `rtdl_optix_write_prepared_fixed_radius_adjacency_3d_device_outputs`

The symbol is intentionally generic. It takes a prepared 3-D fixed-radius search
scene, host query point rows, a radius, caller-owned device `edge_offsets`, and
caller-owned device `neighbor_indices_out`. The any-hit traversal writes
primitive indices into the supplied directed edge stream.

Python now exposes:

- `PreparedOptixFixedRadiusCountThreshold3D.write_device_adjacency_columns(...)`
- `PreparedOptixCupyRadiusGraphAdjacency3D`
- `prepare_optix_cupy_radius_graph_adjacency_3d(...)`
- `radius_graph_components_3d_optix_cupy_prepared_adjacency_partner_columns(...)`

The RT-DBSCAN benchmark app adds:

- `optix_rt_core_adjacency_cupy_components_3d`

The repeat probe adds the same mode for warm/steady-state comparison against
the prepared pure-CuPy adjacency stream.

## App-Agnostic Boundary

No DBSCAN-native ABI was added. The native contract is fixed-radius graph
adjacency:

1. A prepared RT scene represents a generic 3-D point set.
2. A first RT pass writes exact per-query neighbor counts to CuPy columns.
3. CuPy builds an `edge_offsets` prefix-sum column.
4. A second RT pass writes generic neighbor indices into caller-owned CuPy
   storage.
5. CuPy consumes the stream with the existing generic grouped-union component
   continuation.

The benchmark app still supplies the DBSCAN interpretation: `min_neighbors`,
core flags, and cluster labels. The engine does not contain DBSCAN-specific
control flow.

## Pod Evidence

Pod:

```text
ssh root@69.30.85.177 -p 22055 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
```

GPU and build:

```text
NVIDIA RTX A5000, driver 570.211.01
CUDA build prefix: /usr/local/cuda-12
OptiX SDK: /root/vendor/optix-sdk
RTDL OptiX library: /root/rtdl_goal2415/build/librtdl_optix.so
```

Build result:

```text
make build-optix CUDA_PREFIX=/usr/local/cuda-12 OPTIX_PREFIX=/root/vendor/optix-sdk
```

completed successfully.

Artifacts:

- `docs/reports/goal2431_rt_dbscan_optix_adjacency_stream_pod/tiny_app.json`
- `docs/reports/goal2431_rt_dbscan_optix_adjacency_stream_pod/clustered4096_repeat.json`
- `docs/reports/goal2431_rt_dbscan_optix_adjacency_stream_pod/clustered8192_repeat.json`
- `docs/reports/goal2431_rt_dbscan_optix_adjacency_stream_pod/road8192_repeat.json`

## Correctness

The tiny exact fixture passed:

- mode: `optix_rt_core_adjacency_cupy_components_3d`
- `matches_reference`: `true`
- `rt_core_accelerated`: `true`
- native symbol:
  `rtdl_optix_write_prepared_fixed_radius_adjacency_3d_device_outputs`
- native contract:
  `generic_prepared_fixed_radius_adjacency_3d_device_columns`
- directed edges: `33`

The three repeat probes also reported `signatures_match: true`.

## Performance Snapshot

The table uses tail median steady-state `outer_elapsed_sec`, dropping the first
repeat. Lower is better. Ratio is OptiX adjacency divided by prepared pure-CuPy
adjacency.

| Dataset | Points | Directed edges | CuPy prepared adjacency tail median (s) | OptiX RT adjacency tail median (s) | Ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| `clustered3d` | 4096 | 2,114,816 | 0.007471 | 0.006908 | 0.925x |
| `clustered3d` | 8192 | 8,429,946 | 0.014859 | 0.014304 | 0.963x |
| `road3d` | 8192 | 2,678,162 | 0.013574 | 0.013801 | 1.017x |

Interpretation:

- The new OptiX path is correct and uses RT traversal.
- It is near parity to slightly faster for clustered rows at these scales.
- It is slightly slower on the road row.
- This is not a broad speedup claim.

One-time preparation/fill remains heavier for the OptiX adjacency path in these
artifacts. For example, at 8192 clustered points, the prepared pure-CuPy
adjacency build was about `0.598s`, while the OptiX adjacency composite build
was about `0.804s`.

## Design Conclusion

Goal2431 clears the missing architecture problem from Goal2430: RTDL now has a
generic RT-produced device adjacency stream path. The remaining performance
problem is not solved by merely moving stream fill to OptiX. Dense rows can
still produce very large directed streams, and the grouped continuation still
needs a better bounded/chunked or grouped aggregation design.

Therefore the next useful runtime work is:

1. Keep `optix_rt_core_adjacency_cupy_components_3d` as a correctness and
   architecture probe.
2. Add bounded/chunked adjacency-stream continuation so dense graphs do not
   require one huge materialized neighbor-index array.
3. Explore grouped RT continuation that aggregates by query block or cell group
   before writing partner-visible edges.
4. Continue rejecting DBSCAN-native engine shortcuts.

## Verdict

`accept-with-boundary`.

The generic OptiX adjacency writer landed and passed pod smoke tests. It does
not authorize a broad RT-core speedup claim, a paper-reproduction claim, or a
v2.x release claim by itself.
