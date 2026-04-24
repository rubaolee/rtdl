# Goal868 Graph Redesign Decision Packet

- app: `graph_analytics`
- recommended status: `needs_graph_rt_redesign_or_exclusion`
- blocker: `host_indexed_graph_paths_not_rt_core`

## Current Truth

- BFS OptiX path: `host_indexed_correctness_path`
- triangle OptiX path: `host_indexed_correctness_path`
- public app RT-core status: `rejected`

## Evidence

- BFS host-indexed helper present: `True`
- triangle host-indexed helper present: `True`
- public app require-rt-core rejects: `True`
- support matrix marks host-indexed fallback: `True`
- support matrix calls for redesign or exclusion: `True`

## Required Work

- Design a real graph-to-RT lowering for BFS and triangle expansion instead of host-indexed CSR helpers inside the OptiX module.
- Add a local correctness gate that proves the redesigned graph path matches the bounded graph semantics.
- Keep graph_analytics out of active RTX app benchmarking until the redesigned path exists and passes a real OptiX artifact gate.

## Boundary

This packet does not authorize graph_analytics for RT-core claims. It records that the current OptiX-facing graph paths are host-indexed correctness paths and therefore require redesign or explicit exclusion.

