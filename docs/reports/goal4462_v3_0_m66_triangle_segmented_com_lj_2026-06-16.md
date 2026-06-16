# Goal4462 V3.0 M66 Triangle Segmented Paper Dataset

## Result

Goal4462 validates the new segmented RT-2A1 route on a real RT-Graph/SNAP
paper dataset that previously blocked RTDL.

Dataset: `com-lj`

| item | value |
| --- | ---: |
| input edges | 34,681,189 |
| expected triangles | 177,820,130 |
| segmented RTDL observed triangles | 177,820,130 |
| directed edge triangles | 33,895,259 |
| duplicate two-hop rays | 928,731,472 |
| segments | 186 |
| max segment duplicate two-hop rays | 5,000,000 |
| global two-hop summary materialized | false |

The route matched the known RT-Graph/SNAP triangle count exactly.

## Why This Matters

Goal2593 failed both RTDL paper-dataset routes on `com-lj` before traversal:

| old route | status | failure |
| --- | --- | --- |
| RTDL 2A1 global summary | failed | `MemoryError`, CUDA allocation of 7,429,851,776 bytes |
| RTDL 1A2 global summary | failed | `MemoryError`, CUDA allocation of 7,429,851,776 bytes |

In other words, the old `com-lj` blocker was a 7,429,851,776-byte CUDA allocation failure before the RT query could be the meaningful bottleneck.

Goal4462 does not use that global two-hop summary route. It builds the directed
CSR, estimates per-edge two-hop row counts, prepares one generic OptiX 3-D
triangle scene, and sends duplicate two-hop rays in bounded batches to the
existing generic weighted any-hit primitive.

## Timing

Formal command:

```bash
PYTHONPATH=src:. python3 scripts/v3_0_m66_triangle_segmented_paper_dataset_measure.py \
  --input com_lj build/goal2593_snap_edges/com-lj.edge 177820130 \
  --warmup 1 \
  --repeat 3 \
  --segment-max-two-hop-rows 5000000 \
  --hardware 'RTX 4000 Ada pod' \
  --output docs/reports/goal4462_v3_0_m66_triangle_segmented_com_lj_2026-06-16.json
```

Measured timing:

| phase | time |
| --- | ---: |
| directed CSR contract build | 2.473 s |
| segment planning + triangle columns | 7.802 s |
| OptiX scene prepare | 0.679 s |
| segment ray build median | 0.737 s |
| RT query median across 186 segments | 2.006 s |
| total command row | 22.048 s |

For context, Goal2593 measured `com-lj` cuGraph at 1.713 s median total,
authors' `rt_tc` at about 40.802 s pipeline excluding file read, and authors'
`bs_tc` at about 40.759 s pipeline excluding file read. These timings came from
the older Goal2593 environment and are context only; Goal4462 is not yet a
full refreshed paper-dataset performance matrix.

## Claim Boundary

This is a correctness and scalability milestone, not a public speedup claim.
It proves that the previous `com-lj` RTDL OOM was caused by global two-hop
summary materialization, and that the generic RTDL primitive path can run the
same paper-dataset triangle-count contract when the app/partner lowering is
segmented.

The design boundary remains intact:

- Graph orientation, directed CSR construction, and segmentation are app/partner
  responsibilities.
- The native engine still receives only generic `Triangle3D` columns, generic
  `Ray3D` columns, unit weights, and a scalar weighted any-hit summary.
- No graph-specific OptiX shader, graph-specific native ABI, automatic partner
  selection, or public paper-dataset speedup wording is authorized.

Next validation targets are `soc-LiveJournal1` and `com-orkut`, followed by a
single refreshed comparison table against CuPy global-summary where it fits,
Numba global-summary reference where it fits, cuGraph, and authors' RT-Graph
code under one timing contract.

Evidence:

- `docs/reports/goal4462_v3_0_m66_triangle_segmented_com_lj_2026-06-16.json`
- `docs/reports/goal4462_snap_prepare_com_lj_2026-06-16.json`
