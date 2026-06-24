# Goal2459 Threshold-Capped Core Flags For Grouped Stream

Date: 2026-05-19

Status: implemented and pod-smoked, with release boundary still closed.

## Purpose

Goal2457 proved a generic grouped-stream continuation for dense fixed-radius
graph workloads. The first implementation computed exact full degree counts
during preparation and then derived core flags from those counts. That was more
work than RT-DBSCAN-style labels need: component labels only need to know
whether each point has at least `min_neighbors` neighbors.

Goal2459 changes the grouped-stream adapter to use threshold-capped core flags:

```text
fixed-radius count threshold = min_neighbors
```

The native grouped-stream ABI is unchanged and remains generic.

## Design

The prepared adapter now:

1. prepares the generic OptiX fixed-radius scene;
2. delays the count-threshold pass until `run(min_neighbors=...)`;
3. writes threshold-capped `neighbor_counts` and `threshold_flags` into
   reusable CuPy output columns;
4. caches those flags per `min_neighbors` for repeated grouped-stream runs;
5. passes the cached predicate flags into the same generic grouped-union native
   function from Goal2457.

This changes the metadata policy for this mode from exact full degree to:

```text
threshold_capped_at_min_neighbors_not_exact_full_degree
```

The labels and core/noise classification remain exact for the DBSCAN-style
contract. The displayed `neighbor_count` column is threshold-capped in this
mode, matching the already reviewed RT count-threshold bridge modes.

## Pod Evidence

Pod:

```text
ssh root@69.30.85.177 -p 22055 -i ~/.ssh/id_ed25519
```

Artifacts:

- `docs/reports/goal2459_grouped_stream_threshold_capped_pod/summary.json`
- `docs/reports/goal2459_grouped_stream_threshold_capped_pod/clustered3d_32768_grouped_stream_threshold_capped.json`
- `docs/reports/goal2459_grouped_stream_threshold_capped_pod/clustered3d_65536_grouped_stream_threshold_capped.json`
- `docs/reports/goal2459_grouped_stream_threshold_capped_pod/tiny.json`
- `docs/reports/goal2459_grouped_stream_threshold_capped_pod/planned_65536.json`

Environment matched Goal2457: RTX A5000, driver `570.211.01`, CUDA 12, OptiX
SDK under `/root/vendor/optix-sdk`, and `RTDL_OPTIX_LIBRARY` pointed at
`/root/rtdl_goal2457/build/librtdl_optix.so`.

## Results

### Native Count-Threshold Phase

| Points | Goal2457 threshold | Goal2457 count native sec | Goal2459 threshold | Goal2459 count native sec | Native count speedup |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 32,768 | 32,768 | 0.017711 | 12 | 0.003156 | 5.61x |
| 65,536 | 65,536 | 0.064712 | 12 | 0.005116 | 12.65x |

This validates the intended local optimization: the core-flag phase no longer
walks the whole neighbor set just to answer a threshold predicate.

### End-To-End Grouped-Stream Probe

| Points | Prepare sec | Repeat 1 sec | Tail median sec | Signature |
| ---: | ---: | ---: | ---: | --- |
| 32,768 | 0.972688 | 0.461841 | 0.072831 | matched |
| 65,536 | 0.158348 | 0.337285 | 0.218252 | matched |

Interpretation:

- The threshold-count phase improved strongly.
- The full grouped-stream pass is still dominated by generic grouped union over
  RT hits, so steady-state tail time did not improve materially.
- The planned 65,536-point run selected
  `optix_rt_core_grouped_stream_cupy_components_3d`, kept
  `full_stream_fits_budget=false`, and completed in `0.578006` seconds in the
  warmed pod process.
- Tiny correctness still matched the CPU reference.

## Boundary

Verdict: `accept-with-boundary`.

Allowed conclusion:

- RTDL now uses the minimal threshold predicate needed by the grouped-stream
  continuation instead of exact full degree counts.

Not allowed:

- no broad RT-core speedup claim;
- no paper-reproduction claim;
- no v2.x release authorization from this goal;
- no claim that this solves the remaining grouped-union atomic overhead.

## Next Work

The next real performance target is the grouped-union pass itself. The count
predicate is now cheap enough that optimizing it further is not the binding
problem. Future v2.x work should examine generic segmented/warp-local union,
tile-local union compression, or a reusable component-continuation primitive
that reduces global atomic pressure without introducing DBSCAN-specific native
logic.
