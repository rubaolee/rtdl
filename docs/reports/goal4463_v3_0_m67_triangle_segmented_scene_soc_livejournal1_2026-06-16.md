# Goal4463 V3.0 M67 Triangle Segmented Scene Paper Dataset

## Result

Goal4463 extends the segmented RT-2A1 route from ray batching to source-range
triangle-scene batching. This is needed when the directed-edge triangle scene
itself is too large for one OptiX scene.
In short, this milestone adds source-range triangle-scene segmentation.

Dataset: `soc-LiveJournal1`

| item | value |
| --- | ---: |
| input edges | 68,993,773 |
| expected triangles | 285,730,264 |
| segmented RTDL observed triangles | 285,730,264 |
| directed edge triangles | 42,260,523 |
| duplicate two-hop rays | 1,383,299,326 |
| source-range scenes | 6 |
| ray segments | 280 |
| max directed-edge triangles per scene | 8,000,000 |
| max duplicate two-hop rays per ray segment | 5,000,000 |
| global two-hop summary materialized | false |
| global triangle scene materialized | false |

The route matched the known RT-Graph/SNAP triangle count exactly.

## Why M65/M66 Was Not Enough

M65/M66 segmented duplicate two-hop rays but still prepared one global
directed-edge triangle scene. That was enough for `com-lj`, but the first
`soc-LiveJournal1` attempt failed at scene preparation with `CUDA driver error:
out of memory`.

M67 partitions by source vertex range. For each source range, the app/partner
builds a generic triangle scene only for directed edges whose source is in that
range, then sends only duplicate two-hop rays with sources in that same range.
This preserves correctness because the RT-2A1 ray for `(src, dst)` can only hit
the directed closing edge `(src, dst)`.

## Goal2593 Blocker Removed

Goal2593 failed both RTDL paper-dataset routes on `soc-LiveJournal1` before
traversal:

| old route | status | failure |
| --- | --- | --- |
| RTDL 2A1 global summary | failed | `MemoryError`, CUDA allocation of 11,066,394,608 bytes |
| RTDL 1A2 global summary | failed | `MemoryError`, CUDA allocation of 11,066,394,608 bytes |

M67 replaces that global two-hop and global-scene shape with bounded generic RT
batches and completes the same triangle-count contract.

## Timing

Formal command:

```bash
PYTHONPATH=src:. python3 scripts/v3_0_m66_triangle_segmented_paper_dataset_measure.py \
  --input soc_livejournal1 build/goal2593_snap_edges/soc-LiveJournal1.edge 285730264 \
  --mode segmented_scenes \
  --warmup 1 \
  --repeat 3 \
  --segment-max-two-hop-rows 5000000 \
  --scene-max-directed-edges 8000000 \
  --hardware 'RTX 4000 Ada pod' \
  --output docs/reports/goal4463_v3_0_m67_triangle_segmented_scene_soc_livejournal1_2026-06-16.json
```

Measured timing:

| phase | time |
| --- | ---: |
| directed CSR contract build | 4.574 s |
| source/ray segment planning | 13.645 s |
| triangle column build median | 0.001 s |
| OptiX scene prepare median | 0.253 s |
| segment ray build median | 1.112 s |
| RT query median across 6 scenes / 280 ray segments | 3.021 s |
| total command row | 36.523 s |

For context, Goal2593 measured `soc-LiveJournal1` cuGraph at 2.378 s total,
authors' `rt_tc` at about 65.658 s pipeline excluding file read, and authors'
`bs_tc` at about 63.205 s pipeline excluding file read. These are context rows
from the older Goal2593 environment, not a refreshed public performance matrix.

## Claim Boundary

This is a correctness and scalability milestone, not a public speedup claim.
It proves that RTDL can keep the native engine generic while moving both
previous large intermediates behind explicit app/partner segmentation:

- No global two-hop summary relation.
- No global triangle scene.
- No graph-specific OptiX shader or graph-specific native ABI.
- No automatic partner selection or public paper-dataset speedup wording.

Next target: `com-orkut`, the largest Goal2593 OOM row.

Evidence:

- `docs/reports/goal4463_v3_0_m67_triangle_segmented_scene_soc_livejournal1_2026-06-16.json`
- `docs/reports/goal4463_snap_prepare_soc_livejournal1_2026-06-16.json`
