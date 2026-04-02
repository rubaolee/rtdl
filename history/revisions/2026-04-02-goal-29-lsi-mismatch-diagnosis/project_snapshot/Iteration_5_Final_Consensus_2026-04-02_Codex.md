# Goal 29 Final Consensus (Codex)

Result:
- Goal 29 closes as a diagnosis-only round
- no runtime patch is accepted from this round

Accepted diagnosis:
1. the larger exact-source `k=5` `lsi` mismatch is reproducible
2. the mismatch can be reduced to a minimal exact-source segment reproducer
3. float32 truncation in the active native geometry ABI is one confirmed contributing factor
4. the current Embree-side `lsi` candidate-generation path still has unresolved false-negative behavior on exact-source geographic data

Why no code change was kept:
- multiple local runtime experiments were attempted
- none produced a regression-clean, reviewable parity fix
- preserving repo integrity was more important than publishing speculative backend changes

Next required round:
- redesign or instrument the exact-source `lsi` broad phase, with explicit attention to native precision policy and candidate completeness
