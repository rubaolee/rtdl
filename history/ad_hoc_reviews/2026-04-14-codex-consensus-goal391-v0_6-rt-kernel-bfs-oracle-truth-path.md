# Codex Consensus: Goal 391 v0.6 RT-Kernel BFS Oracle Truth Path

Date: 2026-04-14
Status: accepted

## Conclusion

Goal 391 is accepted.

This is the first bounded native/oracle execution closure for the corrected
RTDL graph-kernel line. The implementation stays narrow and technically honest:

- only RT-kernel `bfs_discover(...)` is enabled in `rt.run_cpu(...)`
- `triangle_match(...)` remains blocked
- the native ABI mirrors the Python truth-path step semantics instead of
  pretending graph lowering or RT backend mapping already exists

## Why Acceptance Is Justified

- the new native oracle ABI is bounded and explicit
- the Python runtime binding matches that ABI directly
- BFS graph inputs now flow through `run_cpu(...)` with row-level parity
- deterministic output ordering is preserved across Python and native paths
- the focused test suite and core-quality regression both pass
- Gemini provided the external acceptance artifact required for a coding goal

## Remaining Boundary

This goal does not provide:

- native/oracle `triangle_count`
- graph lowering
- Embree / OptiX / Vulkan graph execution

Those remain later goals in the corrected RT graph ladder.
