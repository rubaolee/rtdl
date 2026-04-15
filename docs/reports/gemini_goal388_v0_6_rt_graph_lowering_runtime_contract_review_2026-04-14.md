# Gemini Review: Goal 388 v0.6 RT Graph Lowering And Runtime Contract

**Verdict:** Approved

## Findings

1. **Clear Lowering/Runtime Boundary:** The separation is well-defined.
   Lowering is responsible for translating the kernel into a graph-aware IR
   that preserves semantics like `graph_expand` and `rt.bfs_discover`, while
   the runtime owns the physical preparation step that converts logical CSR
   into RT encodings and acceleration structures.

2. **Strict Preservation of RTDL Kernel Model:** The design successfully
   defends the kernel authoring model. It explicitly prohibits regressing into
   detached runtime helpers such as a raw `bfs(graph)` API as the primary
   interface, ensuring authors continue to write logical RTDL graph kernels.

3. **Honest Host/Runtime/Backend Split:** State ownership is properly
   delineated. The host retains control over algorithmic outer loops and state,
   the runtime manages the state for a single bounded RT step, and the backend
   contract remains narrow and backend-independent.

## Final Decision

Proceed with the defined lowering and runtime contract. The boundaries map the
logical graph kernel surface to backend execution while preserving the core
RTDL philosophy.
