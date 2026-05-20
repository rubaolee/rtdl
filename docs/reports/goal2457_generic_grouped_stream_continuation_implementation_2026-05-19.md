# Goal2457 Generic Grouped Stream Continuation Implementation

Date: 2026-05-19

Status: implemented and pod-smoked, with release boundary still closed.

## Purpose

Goal2455 identified the next RT-DBSCAN bottleneck: full directed adjacency is
fast when it fits GPU memory, but dense rows can create an edge table too large
to be the right runtime contract. Chunked adjacency avoids that large table but
is launch-heavy. Goal2457 implements the first generic grouped-stream
continuation proof so RT traversal can update caller-owned continuation
workspaces directly.

This is not a DBSCAN-specific native extension. The native ABI is a generic
fixed-radius predicate/grouped-union contract:

```text
rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_device_outputs
```

## What Changed

### Native OptiX Contract

Added a prepared OptiX path that accepts:

- query and search point rows;
- caller-owned `predicate_flags`;
- caller-owned `parent_out`;
- caller-owned `fallback_candidate_out`;
- `query_index_offset`, `item_count`, and `radius`.

During fixed-radius traversal, the kernel:

- unions predicate-true source/target pairs by monotonic `atomicMin`;
- captures one predicate-true fallback candidate for predicate-false sources;
- avoids materializing a directed neighbor-index table;
- records metadata under
  `generic_prepared_fixed_radius_grouped_union_3d_device_workspaces`.

No Goal2457-added native symbol contains `dbscan`. This goal does not claim to
remove older legacy/proof `db_scan` names elsewhere in the OptiX tree; it only
proves that the new grouped-stream continuation is generic and does not add new
app-shaped native ABI.

### Python/Partner Contract

Added `PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D` and the public
helpers:

```python
prepare_optix_cupy_radius_graph_grouped_stream_continuation_3d(...)
radius_graph_components_3d_optix_cupy_prepared_grouped_stream_partner_columns(...)
```

The adapter keeps the app policy outside the engine:

1. OptiX count-threshold columns compute exact degree counts.
2. CuPy creates generic predicate flags from those counts.
3. OptiX grouped-stream traversal updates parent and fallback candidate columns.
4. CuPy resolves component labels from the parent/fallback workspaces.

The RT-DBSCAN app exposes this through manual mode:

```text
optix_rt_core_grouped_stream_cupy_components_3d
```

### Planner Policy

The explicit continuation planner now uses a three-branch policy:

| Condition | Selected mode |
| --- | --- |
| Tiny correctness fixture | `cpu_reference` |
| Estimated full stream fits directed-edge budget | `optix_rt_core_adjacency_cupy_components_3d` |
| Estimated full stream exceeds directed-edge budget | `optix_rt_core_grouped_stream_cupy_components_3d` |

Chunked adjacency remains available as a manual memory-control diagnostic. It is
no longer the default over-budget branch after Goal2457 because grouped stream
is faster on the intended dense-row case.

## Pod Evidence

Pod:

```text
ssh root@69.30.85.177 -p 22055 -i ~/.ssh/id_ed25519
```

Recorded environment:

- GPU: NVIDIA RTX A5000
- Driver: 570.211.01
- CUDA: `/usr/local/cuda-12`
- OptiX SDK: `/root/vendor/optix-sdk`
- Build command:
  `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12`
- Runtime library: `/root/rtdl_goal2457/build/librtdl_optix.so`
- Source baseline: `b60f179a` plus the local Goal2457 patch

Artifacts:

- `docs/reports/goal2457_grouped_stream_pod/summary.json`
- `docs/reports/goal2457_grouped_stream_pod/clustered3d_32768_summary.json`
- `docs/reports/goal2457_grouped_stream_pod/clustered3d_65536_summary.json`
- `docs/reports/goal2457_grouped_stream_pod/planned_65536.json`
- `docs/reports/goal2457_grouped_stream_pod/tiny_final.json`
- `docs/reports/goal2457_grouped_stream_pod/planned_65536_final.json`

The perf probe process exited nonzero only because the shell script had a stray
trailing heredoc marker after writing all JSON artifacts. The build, tiny smoke,
and measured rows had already completed, and the summary artifacts were copied
back for tests.

A separate clean planned-mode smoke then ran:

```text
planned_rt_dbscan_continuation, clustered3d, 65,536 points
selected optix_rt_core_grouped_stream_cupy_components_3d
full_stream_fits_budget false
native_execution_path prepared_rt_core_grouped_union_3d
materializes_directed_adjacency_stream false
```

After adding final workspace-size validation, the pod rebuilt
`librtdl_optix.so`, reran the Goal2457 static test on the pod, reran a tiny
correctness smoke with `matches_reference=true`, and reran the 65,536-point
planned-mode smoke with the same grouped-stream selection.

## Results

Tail medians below exclude the first warmup/compile-heavy repeat.

| Dataset | Points | Mode | Tail median sec | Signature |
| --- | ---: | --- | ---: | --- |
| clustered3d | 32,768 | full adjacency | 0.009364 | matched |
| clustered3d | 32,768 | grouped stream | 0.074144 | matched |
| clustered3d | 32,768 | chunked adjacency | 0.177750 | matched |
| clustered3d | 65,536 | grouped stream | 0.189778 | matched |
| clustered3d | 65,536 | chunked adjacency | 0.625379 | matched |

Interpretation:

- At 32,768 points, full adjacency still wins when it fits memory.
- At 32,768 points, grouped stream is about 2.40x faster than chunked
  adjacency, but about 7.92x slower than full adjacency.
- At 65,536 points, grouped stream is about 3.30x faster than chunked
  adjacency on the dense over-budget row.
- All measured signatures matched the reference signature.

This confirms the intended planner rule: do not replace full adjacency when the
full stream fits; use grouped stream when the full stream exceeds the explicit
budget.

## Boundary

Verdict: `accept-with-boundary`.

Allowed conclusions:

- RTDL now has a first generic grouped-stream continuation proof for
  fixed-radius graph/component workloads.
- The new path avoids materializing a full neighbor-index table.
- The new path improves the dense over-budget continuation branch versus
  chunked adjacency on the RTX A5000 probe.

Not allowed yet:

- no DBSCAN paper-reproduction claim;
- no broad RT-core speedup claim;
- no whole-app speedup claim;
- no v2.x release authorization from this single goal;
- no claim that grouped stream should replace full adjacency when full
  adjacency fits.

## Next Work

- Seek independent Gemini/Claude review of the generic ABI, planner policy, and
  pod evidence.
- Add broader datasets for the grouped-stream branch after the first review.
- Study a lower-overhead union primitive or segmented reduction form if grouped
  stream becomes the standard over-budget graph continuation.
