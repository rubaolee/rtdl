# Goal3668 v2.9 Closeout And Next-Direction Refresh

Date: 2026-06-06

Status: internal closeout/direction refresh; not a release packet, not public
speedup wording, and not final 3-AI roadmap consensus.

## Purpose

Goal3619/3622 proposed the next-version direction while Claude was quota
blocked. Since then, Goals3658/3660/3663/3665 changed the RayJoin PIP picture
materially. This refresh records the current state without rewriting the older
reviewed packet in place.

## What Changed After Goal3622

RayJoin PIP is no longer accurately summarized as a CuPy-owned route for the
project-owned validated-domain contracts.

New evidence:

| Goal | Evidence | Meaning |
| --- | --- | --- |
| Goal3658 | Tuned RTDL/OptiX prepared-points positive count with `eps=1e-9`: exact `1417`, `0.283574ms` on the 512 county slice | The one-shot/sequential RTDL route beats the prior project-owned CuPy dense baseline, but still trails RayJoin `query_exec` reported query timing. |
| Goal3660 | Persistent generic prepared-point batch executor: exact `1417`, `0.034225ms/request` on 512 | Strong batched repeated-request throughput evidence; not one-shot latency. |
| Goal3663 | Cross-slice batch executor: exact `11331`, `0.051139ms/request` on 4096 | The batch result is not a one-slice accident. |
| Goal3665 | Validated-domain guard: 512 passes `1417 == 1417`; full county fails `47264 != 47262` before RayJoin timing starts | The fast route is validated-domain evidence only; broad CDB PIP needs topology-aware correction/fallback. |

The v2.9 RayJoin reading is now:

1. RTDL/OptiX is strong for LSI count, overlay active-count, and validated-domain
   batched PIP repeated-request throughput.
2. One-shot/sequential PIP improved over the prior project-owned CuPy dense
   baseline but still trails RayJoin's reported query timing.
3. Full-county PIP is a correctness-contract problem, not another easy timing
   knob. The fast path must fail closed until a topology-aware contract or
   correction route exists.
4. No single whole-RayJoin performance claim is authorized.

## Closeout Decision For v2.9

Stop the current v2.9 tuning loop unless a proposed task satisfies at least one
condition:

- fixes a correctness mismatch or fail-closed contract hole;
- has a credible path to a large material end-to-end gain;
- creates a reusable generic primitive/runtime capability;
- supplies missing same-contract evidence needed for a claim boundary.

The last work item, Goal3665, satisfied the first condition by making the large
full-county PIP mismatch fail before RayJoin timing. More small PIP timing
tweaks should stop.

## Updated Next-Version Direction

The Goal3619/3622 recommendation still stands, but with the RayJoin PIP update
folded in:

1. **Contract first.** Publish primitive contracts before public claims.
2. **Residency first.** Keep typed primitive outputs resident when downstream
   work can consume them there, but do not claim true zero-copy without proof.
3. **Partner freedom.** Users choose supported partners; RTDL provides measured
   support and reference routes, not automatic public defaulting.
4. **Benchmark pressure tests.** Benchmarks should force reusable generic
   primitive/runtime capabilities, not app-shaped native-engine logic.

First contract targets for the next version:

| Target | Why |
| --- | --- |
| `segment_pair_*` count/intersection contracts | RayJoin LSI repair showed fast routes need explicit endpoint, collinear, tiny-segment, and tolerance policy before public wording. |
| topology-aware closed-shape membership / containment | Goal3665 showed broad CDB PIP needs face/ring/chain identity, deterministic boundary ownership, and duplicate policy. |
| typed resident primitive output columns | Needed so downstream partner/native continuations can consume primitive results without unnecessary host materialization. |
| deterministic grouped reductions / witness contracts | Needed for nearest-neighbor, Hausdorff, RTNN, and grouped continuation benchmarks. |

## Consensus Status

This refresh is Codex's current internal position after the Goal3658-3665
RayJoin PIP work.

- Codex: `accept-with-boundary`.
- Gemini: pending fresh review of this refresh.
- Claude: still required for strict 3-AI next-version consensus when available.

Until the fresh reviews are reconciled, the next-version direction remains a
candidate, not final consensus.

## Boundary

Goal3668 does not authorize:

- release or tag action;
- public v2.9 speedup claims;
- whole-app RayJoin speedup claims;
- RayJoin paper reproduction wording;
- broad RT-core speedup wording;
- RTDL-beats-RayJoin wording;
- true zero-copy wording;
- automatic partner/backend selection;
- app-specific native-engine logic.

