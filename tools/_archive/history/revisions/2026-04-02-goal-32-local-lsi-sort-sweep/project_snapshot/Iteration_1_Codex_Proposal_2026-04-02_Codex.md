# Iteration 1 Codex Proposal

Codex proposed a parity-safe local optimization:
- keep the native analytic `segment_intersection(...)` refine rule from Goal 31
- replace the brute-force left-by-right scan with a double-precision sort-sweep candidate pass
- preserve the CPU-oracle row set exactly
- preserve the original left/right output ordering after candidate filtering

Reasoning:
- Goal 31 solved correctness but left local `lsi` as a naive `O(N*M)` nested loop
- a sort-sweep candidate pass is still purely native and deterministic
- this is a bounded optimization that does not reintroduce BVH candidate fragility
