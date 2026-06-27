# Codex Consensus: Goal 393 v0.6 Embree RT Graph Mapping And BFS Closure

Date: 2026-04-14
Status: accepted

## Conclusion

Goal 393 is accepted.

This is the first real RT backend closure for the corrected v0.6 graph line.
The implementation does not hide behind the oracle path: it uses an
Embree-specific point-query mapping for bounded BFS expansion and proves parity
against the established truth paths.

## Why Acceptance Is Justified

- `run_embree(...)` now supports RT-kernel BFS
- `prepare_embree(...)` also accepts the bounded BFS graph kernel
- the implementation uses Embree point queries for candidate generation
- parity is proven against Python and native/oracle
- focused backend tests and core-quality regression both pass
- Gemini provided the required external acceptance artifact

## Remaining Boundary

This goal does not provide:

- Embree `triangle_count`
- OptiX graph support
- Vulkan graph support
- graph lowering across all backends

Those remain later goals.
