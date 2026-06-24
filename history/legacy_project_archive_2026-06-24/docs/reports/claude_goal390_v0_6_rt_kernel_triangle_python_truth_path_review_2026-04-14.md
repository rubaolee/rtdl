# Claude Review: Goal 390 RT-Kernel Triangle Count Python Truth Path

## Verdict: APPROVE

### Finding 1 — Correct algorithm, correctly bounded

`triangle_probe_cpu` implements the edge-intersection approach: for each seed
`(u, v)` it computes `neighbors(u) ∩ neighbors(v)` and emits `(u, v, w)`
triples. The `id_ascending` guard (`u < v < w`) enforces strict ordering and
the `seen` set prevents duplicates. This is the right algorithm for undirected
triangle detection and the boundary is clearly enforced.

### Finding 2 — `run_cpu` guard is honest

`_validate_oracle_supported_inputs` immediately raises a clear error for both
`bfs_discover` and `triangle_match`. The boundary between the Python truth path
and unsupported oracle/native graph execution is explicit and tested.

### Finding 3 — `_normalize_records` is correct but slightly type-fragile

The dispatch order is correct: graph types are handled before the general
iterable path. The only mild debt is that `graph_csr` returns a single
`CSRGraph` object while most other branches return tuples. This is fine for the
current bounded slice, but it is a type-coherence note for later cleanup.

### Finding 4 — Test coverage matches the stated scope

The six tests cover surface export, compile-time IR inspection, execution
correctness for tuple and mapping inputs, invalid seed rejection, and the
`run_cpu` honesty guard. The regression suite also remains clean.

## Final Decision

Accept.

The implementation is honest, bounded, and consistent with the corrected `v0.6`
RTDL graph-kernel direction.
