# Goal 32 Local LSI Sort-Sweep Optimization (2026-04-02)

## Scope

Goal 32 is the immediate follow-up to Goal 31.

Goal 31 fixed correctness by replacing the broken local BVH `lsi` path with a parity-safe native analytic loop. Goal 32 improves that local path without changing the current local runtime contract:
- local `lsi` remains `native_loop`
- local `lsi` remains parity-first
- BVH-backed local `lsi` is still out of scope for this round

## Codex Optimization Proposal

Codex proposed:
- keep the same native analytic segment-intersection refine rule
- replace the brute-force left-by-right scan with a double-precision sort-sweep candidate pass
- keep row emission in original left/right order after candidate filtering

Accepted local implementation details:
- build segments are sorted by `min_x`
- probe segments are sorted by `min_x`
- an active build window is maintained while probe `min_x` advances
- candidate pruning uses:
  - `x` interval overlap
  - `y` interval overlap
- surviving candidates still go through the same analytic `segment_intersection(...)`

So Goal 32 changes candidate enumeration, not final intersection semantics.

## Current Local Result

### Correctness

The optimized path is parity-clean on:
- Goal 31 minimal exact-source reproducer
- Goal 31 frozen `k=5` exact-source slice
- a larger localized synthetic `lsi` case

Relevant local regression commands:
- `python3 -m unittest tests.goal31_lsi_gap_closure_test tests.goal15_compare_test tests.goal19_compare_test tests.rtdsl_embree_test`
- `python3 -m unittest tests.goal32_lsi_sort_sweep_test`

### Native benchmark against Goal 31 brute-force path

Using a localized synthetic `lsi` dataset with:
- `1200` left segments
- `2200` right segments
- same output pairs before and after optimization

Observed native timings:
- Goal 31 brute-force native path: `0.003466417 s`
- Goal 32 sort-sweep native path: `0.0012185 s`
- speedup vs Goal 31 native path: `2.84x`

Observed output comparison:
- same emitted pairs: `true`

## Honest Status

Goal 32 is not yet formally closed.

Why:
- Claude quota was exhausted before the optimization review step could finish

So the round is currently:
- implemented locally
- tested locally
- benchmarked locally
- pending Claude review before consensus closure

Gemini monitoring note already required that any final Goal 32 closure keep these boundaries explicit:
- local `lsi` remains `native_loop`
- the optimization must not regress Goal 31 parity
- any performance claim must compare against the Goal 31 brute-force native path, not against the older broken BVH path
