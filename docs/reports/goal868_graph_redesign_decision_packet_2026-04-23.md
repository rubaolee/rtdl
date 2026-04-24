# Goal868 Graph Redesign Decision Packet

- app: `graph_analytics`
- recommended status: `native_graph_ray_packaged_needs_rtx_artifact`
- blocker: `needs_real_rtx_artifact`

## Current Truth

- BFS OptiX path: `explicit_native_graph_ray_rtx_gated`
- triangle OptiX path: `explicit_native_graph_ray_rtx_gated`
- public app RT-core status: `rejected`

## Evidence

- BFS host-indexed helper present: `True`
- triangle host-indexed helper present: `True`
- public app require-rt-core rejects: `True`
- support matrix marks host-indexed fallback: `True`
- support matrix calls for redesign or exclusion: `False`

## Required Work

- Run the combined Goal889/905 RTX graph gate for visibility, native BFS graph-ray, and native triangle graph-ray.
- Keep --require-rt-core rejected for BFS/triangle until the strict RTX artifact passes independent review.
- Keep shortest-path, graph database, distributed analytics, and whole-app graph-system claims excluded.

## Boundary

This packet does not authorize graph_analytics for RT-core claims. It records that native OptiX graph-ray candidate generation is now packaged but remains RTX-gated before promotion.

