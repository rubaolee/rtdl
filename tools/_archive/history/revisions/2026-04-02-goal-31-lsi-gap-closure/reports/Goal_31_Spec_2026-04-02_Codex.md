# Goal 31 Spec

Goal 31 solves the exact-source `lsi` false-negative gap that remained after Goal 30.

Required structure:
- Codex writes one solution proposal
- Claude writes an independent solution proposal
- Codex reviews Claude's proposal and selects an implementation path
- Gemini monitors the whole round
- the round closes only if the minimal reproducer and frozen `k=5` slice both become parity-clean

Required boundary:
- keep `rt.run_cpu(...)` as the oracle
- do not weaken the CPU reference
- do not claim a BVH-backed local fix if the accepted implementation is native-loop based
