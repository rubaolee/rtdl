# Goal 32 Local LSI Sort-Sweep Optimization

Goal 32 continues from Goal 31.

Goal 31 restored exact-source local `lsi` correctness by replacing the broken BVH path with a parity-safe native analytic loop. That left one immediate follow-up problem:
- the current local `lsi` path was still a naive `O(N*M)` nested loop

Goal 32 scope:
- keep the Goal 31 parity fix intact
- optimize the current local `lsi` native loop without reintroducing BVH candidate fragility
- preserve the current local `native_loop` contract
- compare a Codex optimization proposal against a Claude optimization proposal
- keep Gemini monitoring the round

Current state of this round:
- Codex implemented a double-precision sort-sweep candidate pass
- parity remains intact on the minimal reproducer, frozen `k=5` slice, and a larger localized synthetic case
- a native benchmark against the Goal 31 brute-force implementation showed a measurable speedup
- Claude review is still pending because the Claude CLI hit a quota limit before the optimization review could be completed

So Goal 32 is currently:
- implemented locally
- verified locally
- not yet consensus-closed
