# V4 Goal4631 Tier-3 Spike Execution Decision

Date: 2026-06-24

Status: `goal4631_tier3_spike_executed_deferred_not_supported`

Decision: Tier-3 remains spike-only/deferred and is not V4.0 public support.

## Purpose

Goal4631 closes scorecard gate G6 from Goal4626:

> Tier-3 must remain spike-only unless the protocol gates all pass and a later review authorizes support.

The current evidence is enough to settle the V4.0 boundary: Tier-3 cannot be used as a release dependency, cannot be documented as supported, and cannot authorize raw OptiX callback wording.

## Evidence Summary

Protocol:

- `future/v4/tier3_callback_spike_protocol_2026-06-24.md`

Stage 1 evidence:

- `future/v4/evidence/v4_tier3_numba_ptx_probe_2026-06-24.json`
- `future/v4/evidence/v4_tier3_numba_ptx_probe_2026-06-24.md`
- `future/v4/tier3_numba_ptx_spike.md`

Observed result:

- one scalar Numba device callback generated PTX;
- PTX header records NVIDIA NVVM / CUDA 12.9;
- this is narrow evidence, not a protocol pass.

Protocol gap:

- required: at least 20 compile attempts across at least 4 accepted scalar callback variants;
- observed: one callback attempt.

Stage 2 evidence:

- `future/v4/evidence/v4_tier3_optix_module_link_probe_2026-06-24.json`
- `future/v4/evidence/v4_tier3_optix_module_link_probe_2026-06-24.md`
- `future/v4/tier3_optix_module_link_spike.md`

Observed result:

- Numba PTX generated: true;
- C++ OptiX loader compiled: true;
- `optixModuleCreate` attempted: true;
- `optixModuleCreate` succeeded: false;
- blocked stage: `optix_module_create`;
- OptiX error: `Invalid input`;
- OptiX log key phrase: `No functions with semantic types found`.

Interpretation:

- bare Numba helper PTX is not an OptiX module by itself;
- a future Tier-3 path needs a real OptiX wrapper or direct-callable ABI spike;
- correctness and overhead stages cannot run until link and launch work.

## Stage Decision Table

| Stage | Status | Decision |
|---|---|---|
| Stage 0 planner boundary | passed | Planner and push-down recognizer keep scalar callbacks spike-only and action callbacks rejected. |
| Stage 1 Numba PTX generation | narrow evidence only | One PTX generation is useful evidence, but does not pass the protocol's 20-attempt / 4-variant gate. |
| Stage 2 OptiX wrapper/direct-callable ABI | blocked | Direct `optixModuleCreate` on bare helper PTX failed. |
| Stage 3 correctness parity | not attempted | Cannot start until Stage 2 links and launches. |
| Stage 4 overhead ceiling | not attempted | Cannot measure callback overhead until a linked route launches. |
| Stage 5 review gate | this document requests review | Review must preserve spike-only/non-support boundary. |

## Code And Tests

Code:

- `src/rtdsl/v4_tier3_spike_decision.py`

Tests:

- `tests/v4_goal4631_tier3_spike_decision_test.py`

Focused test command:

```powershell
py -m unittest tests.v4_tier3_callback_spike_protocol_test tests.v4_tier3_numba_ptx_probe_test tests.v4_tier3_optix_module_link_probe_test tests.v4_goal4631_tier3_spike_decision_test tests.v4_goal4630_pushdown_recognizer_test
```

Result:

- 24 tests passed.

## Decision

Goal4631 closes G6 as:

- `defer_tier3_not_v4_0_supported`

Allowed:

- continue Tier-3 as V4.x research/spike;
- build a real OptiX wrapper/direct-callable ABI spike later;
- rerun the full protocol only after the implementation exists.

Not allowed:

- V4.0 public Tier-3 support;
- raw OptiX callback support;
- measured-catalog promotion;
- release wording depending on Tier-3;
- arbitrary Python/Numba callback claims.

## Required Future Tier-3 Work

Before any future support claim, the project must:

- build a real OptiX wrapper or direct-callable ABI spike;
- run at least 20 compile/link attempts across 4 scalar callback variants;
- prove program-group, pipeline, and launch reliability at 95% or better;
- prove 100% correctness parity on dense, sparse, and empty datasets;
- measure callback route overhead against a matching hand-written Tier-2 baseline.

## Goal-Level Decision Self-Audit

Decision: defer Tier-3 as not supported in V4.0.

1. Am I being foolish?
   - No. The evidence reaches a concrete blocked stage, so support would be overclaiming.

2. What actions would make this foolish?
   - Claiming "Numba PTX generated" means OptiX callback support.
   - Ignoring that `optixModuleCreate` failed.
   - Treating a future wrapper ABI as already implemented.

3. Is there another path that avoids being stuck on one idea?
   - Yes. Keep Tier-3 as V4.x spike work and do not make V4.0 depend on it.

4. Can I start a different path that truly solves the problem?
   - Yes. Goal4632 can now decide V4 using Tier-2 measured/candidate surfaces only, with Tier-3 explicitly out of the release dependency path.

## Non-Authorization

Goal4631 does not authorize:

- V4 release
- V4 release-candidate status
- measured-catalog promotion
- broad V4 speedup claims
- whole-application speedup claims
- true-zero-copy public wording
- Tier-3 callback support
- raw OptiX callback support
- CuPy performance claims
- C ABI / embedding / non-Python-host work
- app-specific native kernels

