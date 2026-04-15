# Claude Review: Goal 389 v0.6 RT-Kernel BFS Python Truth Path

## Verdict: PASS with two minor notes

The implementation is honest, bounded, and consistent with the corrected v0.6
graph-kernel direction. The scope is exactly what the goal claims: one BFS
expansion step, Python truth-path only.

## Findings

### 1. `run_cpu` needed an honesty guard

The initial implementation allowed RT graph kernels to fall through to
`run_oracle(...)`, which produced a cryptic failure for `CSRGraph` inputs.
This is now fixed by raising a clear boundary error:

- `run_cpu does not support RT graph kernels yet`

### 2. `accel="bvh"` is still metadata in the Python truth path

The RTDL kernel surface carries `accel="bvh"` and `mode="graph_expand"`, but
the Python truth path still executes direct CSR adjacency lookup rather than RT
traversal. This is acceptable for the bounded truth path and is consistent with
the goal's honesty boundary.

### 3. CSR validation and BFS step are correctly bounded

Structural graph validation is complete for the intended slice, and the BFS step
is bounded to one frontier expansion with deterministic ordering, visited
filtering, and same-step dedupe.

### 4. Tests are focused and adequate

The new suite covers exports, compile-time graph metadata, frontier expansion
behavior, mapping inputs, graph validation rejection, invalid frontier rejection,
and the `run_cpu` honesty guard. Existing focused and core tests remain green.

## Final Decision

Accept.

This is a good first executable slice for the corrected RTDL graph line.
