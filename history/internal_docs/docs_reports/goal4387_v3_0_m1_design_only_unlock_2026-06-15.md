# Goal4387 V3.0 M1 Design-Only Unlock

Date: 2026-06-15

Status: M1 design-only unlock after v2.14 closeout. V3.0 implementation remains blocked.

## Decision

The v2.14 closeout required by Goal4384/Goal4385 is complete. Therefore V3.0 may proceed to M1 design work only.

Allowed:

- write the V3.0 execution-graph IR design document;
- define graph value types, residency annotations, stream/lifetime rules, phase markers, and non-goals;
- write tests that validate the design document and forbid app-specific API names;
- define the partner-dependent benchmark rule: current best partner plus Numba reference on the same contract;
- prepare review packets for Claude/Gemini over the M1 IR spec.

Blocked:

- native V3.0 fused execution code;
- V3.0 planner implementation;
- app-specific V3.0 Python public API names;
- app-specific native semantics;
- V3.0 public performance claims;
- any claim that same-stream/device-resident/zero-copy behavior is proven without CUDA-event or Nsight-level evidence.

## Next Gate

V3.0 implementation may start only after:

1. the M1 execution-graph IR design document is frozen;
2. tests verify no app-specific public Python API names or native names;
3. partner-dependent benchmark plans name both the best-performance partner and Numba reference;
4. the M1 packet receives external review if it changes architecture or public-facing APIs.

Until then, the project state is:

`v3_0_m1_design_allowed_implementation_blocked`
