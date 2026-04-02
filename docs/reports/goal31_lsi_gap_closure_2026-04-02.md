# Goal 31 LSI Gap Closure (2026-04-02)

## Scope

Goal 31 solved the exact-source `lsi` false-negative problem that remained after Goal 30.

The round was intentionally structured as:
- Codex writes one concrete fix proposal
- Claude writes an independent fix proposal
- Codex reviews Claude's proposal
- Gemini monitors the decision and closure criteria
- one implementation path is chosen and validated

## Proposal Comparison

### Codex proposal

Codex proposed a parity-first local fix:
- stop using the current `rtcIntersect1` segment-as-ray candidate path for local `lsi`
- replace it with a native analytic segment loop in `rtdl_embree_run_lsi(...)`
- mark the current local `lsi` backend as `native_loop`
- treat any future BVH-backed redesign as a later optimization round

### Claude proposal

Claude independently reached the same structural conclusion:
- the current BVH/`rtcIntersect1` path should not remain the active local `lsi` candidate mechanism
- the current fix should be a parity-safe native double-precision candidate path
- Claude preferred a native sort-sweep implementation as the stronger long-term local optimization

### Consensus

The accepted consensus was:
- remove the broken BVH candidate path from the active local `lsi` runtime now
- land the smallest parity-clean native fix first
- keep future sort-sweep or BVH redesign work as a separate optimization goal

So Goal 31 closes on:
- a native analytic nested-loop `lsi` path
- explicit `native_loop` local lowering metadata
- full parity restoration on the known exact-source reproducers

## Implemented Change

The active local `lsi` runtime in `src/native/rtdl_embree.cpp` was changed so that:
- `rtdl_embree_run_lsi(...)` no longer uses `rtcIntersect1`
- rows are produced by a native analytic left-by-right segment loop
- the active segment-intersection denominator guard now uses a dedicated `1e-7` epsilon aligned more closely with the CPU oracle

Supporting metadata was updated:
- `src/rtdsl/lowering.py`
- `src/rtdsl/baseline_contracts.py`
- `tests/golden/county_zip_join/plan.json`
- `tests/golden/county_zip_join/host_launcher.cpp`

These now state the honest current local contract:
- `lsi` is presently a `native_loop` workload on the local backend
- BVH-backed local candidate traversal is suspended pending a parity-safe redesign

## Verification

Targeted regression passed:
- `python3 -m unittest tests.goal31_lsi_gap_closure_test`

Broader regression passed:
- `python3 -m unittest tests.goal15_compare_test tests.goal19_compare_test tests.goal30_precision_abi_test tests.goal31_lsi_gap_closure_test`
- `python3 -m unittest tests.goal28d_execution_test`
- `make build`
- `make verify`

## Measured Result

### Minimal exact-source reproducer

After the patch:
- CPU pairs:
  - `(24, 368)`
  - `(25, 367)`
  - `(26, 365)`
  - `(111, 345)`
- Embree pairs:
  - `(24, 368)`
  - `(25, 367)`
  - `(26, 365)`
  - `(111, 345)`

Result:
- parity restored on the minimal exact-source reproducer

### Frozen `k=5` exact-source slice

After the patch:
- CPU count: `7`
- Embree count: `7`
- CPU-only pairs: none
- Embree-only pairs: none

Result:
- parity restored on the frozen larger exact-source slice

## Honest Boundary

Goal 31 fixes correctness, not performance.

The current local `lsi` backend is now:
- parity-safe
- native
- deterministic

But it is also now explicitly:
- `native_loop`
- not BVH-backed on the local runtime path

So Goal 31 should not be read as:
- “Embree BVH traversal for local `lsi` is now fixed”

It should be read as:
- “the broken local BVH candidate path was removed from active use, and local `lsi` correctness was restored through a native analytic implementation”

## Final Closure

Claude approved the implemented patch as an acceptable Goal 31 closure.

Gemini approved closure with one explicit reporting boundary:
- all reports must continue to state that the local `lsi` backend now uses `native_loop`, not BVH-backed traversal

So Goal 31 closes successfully as:
- a correctness-restoration round
- not a BVH-performance round
