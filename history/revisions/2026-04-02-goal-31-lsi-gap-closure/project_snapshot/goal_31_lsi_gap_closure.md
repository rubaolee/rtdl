# Goal 31 LSI Gap Closure

Goal 31 closes the larger exact-source `lsi` false-negative gap that remained after Goal 30.

Scope:
- write an explicit Codex fix proposal
- obtain an independent Claude fix proposal
- compare the two proposals under Gemini monitoring
- implement the accepted solution path
- restore CPU-vs-Embree parity on:
  - the minimal exact-source reproducer
  - the frozen `k=5` exact-source slice
- update the local backend documentation to reflect the real runtime contract

Problem statement:
- Goal 29 proved that the current Embree-side `lsi` path was dropping true pairs on exact-source GIS geometry
- Goal 30 fixed the float32 ABI loss, but the `lsi` mismatch remained
- the historical local `lsi` implementation still depended on `rtcIntersect1` segment-as-ray traversal over user geometry, which was not candidate-complete for the frozen reproducer

Accepted solution boundary:
- keep `rt.run_cpu(...)` as the oracle
- do not claim that the current local `lsi` path is still BVH-backed
- replace the broken local candidate path with a parity-safe native path
- preserve the public DSL surface and the native ABI shape

Closure conditions:
- minimal exact-source reproducer becomes parity-clean
- frozen `k=5` exact-source slice becomes parity-clean
- Claude approves the implemented patch
- Gemini approves the monitored closure
- docs and baseline metadata explicitly state that local `lsi` now uses `native_loop`
