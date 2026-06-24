# Goal4482 / V3.0 M86: Triangle Grouped Unique-Count Feasibility

## Verdict

Do not implement an "already sorted source group" skip-sort fast path for the current Triangle Counting route.

The idea was attractive because Goal4479 made the unique/count boundary the remaining segment-ray construction hotspot. If each source group's two-hop destination stream were already sorted, RTDL could skip or greatly reduce the current sort/RLE work. The pod scout says that condition almost never covers the actual work: sorted source groups account for only 0.131% / 0.617% / 0.001% of two-hop rows on `com-lj`, `soc-LiveJournal1`, and `com-orkut`.

This is a negative feasibility result, not a route change. The current internal route remains:

- `unique_weighted`
- `numba_direct_sort_rle`
- `prepared_segment_replay`
- full ray columns
- `cupy_vectorized` output builder

## Source-Group Matrix

The scout uses the same lightweight directed-CSR contract used by the segmented route: `materialize_two_hop_summary=False`, no global two-hop table, and a 15M two-hop row segment cap.

| Dataset | Segments | Source groups | Two-hop rows | Group edges p50/p99/max | Group two-hop p50/p99/max | Sorted two-hop coverage |
|---|---:|---:|---:|---:|---:|---:|
| com-lj | 62 | 3,204,408 | 928,731,472 | 7 / 61 / 524 | 94 / 3,500 / 69,880 | 0.131% |
| soc-LiveJournal1 | 93 | 4,244,167 | 1,383,299,326 | 5 / 70 / 742 | 76 / 4,538 / 96,990 | 0.617% |
| com-orkut | 572 | 3,004,513 | 8,579,930,671 | 32 / 197 / 535 | 1,386 / 35,064 / 118,057 | 0.001% |

The source groups are numerous and usually small to medium. That makes "one source group, one tiny operation" unattractive because launch/scheduling overhead would dominate. At the same time, the sorted fast path is too rare to matter at whole-route scale.

## Interpretation

M86 rules out a simple shortcut, not the broader grouped/local unique-count direction.

The useful next Triangle Counting optimization is a true lower-overhead grouped/local unique-count strategy that processes many groups inside a bounded number of kernels or library calls. It must avoid per-source kernel launches, avoid relying on already-sorted group streams, and preserve the app-agnostic primitive boundary. A custom CUDA/C++ implementation might be fastest, but for the V3 no-C++ lane the next serious candidate would need a Numba/CuPy partner implementation with explicit workspace and bounded materialization.

## Claim Boundary

- no current-best route change;
- no public speedup claim;
- no broad Triangle Counting RT-core acceleration claim;
- no automatic partner selection;
- no app-specific native engine callback;
- no claim that Triangle Counting partner materialization is solved.

## Artifact

- `goal4482_v3_0_m86_triangle_grouped_unique_source_group_stats_2026-06-16.json`
