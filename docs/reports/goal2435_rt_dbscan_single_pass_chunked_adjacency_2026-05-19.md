# Goal2435 RT-DBSCAN Single-Pass Chunked Adjacency

Date: 2026-05-19

Status: implemented and pod-smoked, with boundary.

## Purpose

Goal2433 introduced a memory-bounded chunked adjacency continuation, but it
filled each adjacency chunk twice: one pass for core-core union and a second
pass for border/core labeling after final parent roots were available.

Goal2435 removes the second RT adjacency fill. During the chunked union pass,
the CuPy continuation now also captures one core-neighbor candidate for each
non-core border point. After all core-core unions finish, a lightweight label
kernel maps:

- core points to their final parent root;
- border points to the final parent root of their captured core candidate;
- points without a core candidate to noise.

This is still generic radius-graph component labeling. No DBSCAN-native engine
ABI was added.

## What Changed

`src/rtdsl/partner_adapters.py` now adds two CuPy kernels for the chunked path:

- `radius_graph_3d_chunk_adjacency_union_border_candidate_kernel`
- `radius_graph_3d_border_candidate_label_kernel`

The public app mode remains:

- `optix_rt_core_chunked_adjacency_cupy_components_3d`

Metadata now reports:

- `adjacency_write_pass_count: 1`
- `border_label_policy:
  one_core_neighbor_candidate_per_border_point_captured_during_union_pass`

## Pod Evidence

Pod:

```text
ssh root@69.30.85.177 -p 22055 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
```

Artifacts:

- `docs/reports/goal2435_rt_dbscan_single_pass_chunked_adjacency_pod/tiny_app.json`
- `docs/reports/goal2435_rt_dbscan_single_pass_chunked_adjacency_pod/clustered4096_repeat.json`
- `docs/reports/goal2435_rt_dbscan_single_pass_chunked_adjacency_pod/clustered8192_repeat.json`
- `docs/reports/goal2435_rt_dbscan_single_pass_chunked_adjacency_pod/clustered32768_chunked.json`

The tiny exact fixture passed:

- `matches_reference`: `true`
- `adjacency_write_pass_count`: `1`
- `total_directed_edge_count`: `33`

All repeat probes reported `signatures_match: true`.

## Performance Snapshot

The table uses tail median steady-state `outer_elapsed_sec` where repeats exist.
Lower is better.

| Dataset | Points | Old chunked runtime (s) | Single-pass chunked runtime (s) | Total edges | Max chunk edges | Chunks |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `clustered3d` | 4096 | 0.022417 | 0.015865 | 2,114,816 | 2,114,816 | 1 |
| `clustered3d` | 8192 | 0.053785 | 0.035058 | 8,429,946 | 4,222,317 | 2 |
| `clustered3d` | 32768 | 0.746450 | 0.612652 | 136,345,984 | 17,197,789 | 8 |

Interpretation:

- The single-pass chunked continuation is correct.
- It improves the chunked path by avoiding the second RT fill.
- It remains slower than full adjacency when full adjacency fits in memory.
- Its value is bounded memory, not raw speed.

## Design Conclusion

Goal2435 clears the immediate inefficiency found in Goal2433. The remaining
performance problem is now lower-level: chunked streams still launch multiple
RT fills and multiple CuPy kernels. The next useful work is a generic grouped
stream continuation or an explicit planner that chooses:

- prepared CuPy grid when grid traversal is fastest;
- full OptiX adjacency when the full stream fits and reuse matters;
- chunked OptiX adjacency when peak memory matters.

The planner must be explicit and explainable, not an invisible dispatcher.

## Verdict

`accept-with-boundary`.

This improves a generic continuation primitive. It does not authorize a broad
RT-core speedup claim, a DBSCAN paper-reproduction claim, or a release claim.
