# Goal982 Graph Same-Scale Timing Repair

Date: 2026-04-26

Goal982 repairs the graph timing baseline after Goal981 repaired local Embree graph correctness. It does not authorize public RTX speedup claims.

- status: `ok`
- copies: `20000`
- repeats: `3`
- native query median sec: `0.5672194170765579`
- wrote artifact: `True`
- public speedup authorized: `False`
- claim effect: Graph now has a positive same-scale non-OptiX timing baseline; Goal978 can classify it by timing.

## Summary

```json
{
  "bfs": {
    "discovered_edge_count": 40000,
    "discovered_vertex_count": 40000,
    "max_level": 1
  },
  "triangle_count": {
    "touched_vertex_count": 60000,
    "triangle_count": 20000
  },
  "visibility_edges": {
    "blocked_edge_count": 60000,
    "visible_edge_count": 20000
  }
}
```
