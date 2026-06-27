# V4 Goal4685 Tier-3 Wrapper/Direct-Callable ABI Protocol Gate

Date: 2026-06-25

Status: `goal4685_tier3_wrapper_direct_callable_abi_protocol_gate_no_pod`

## Decision

Goal4685 defines the next real Tier-3 experiment, but does not implement it and does not authorize POD.

The old Tier-3 evidence showed that Numba can emit PTX, but bare helper PTX fails direct `optixModuleCreate` because it has no OptiX semantic entry functions. Therefore the next experiment must not repeat that path. It must compose Numba scalar callback PTX with a semantic OptiX traversal shell or direct-callable ABI.

## Required Stages

| Stage | Required Evidence | Pass Condition | Kill Condition |
| --- | --- | --- | --- |
| `stage0_planner_boundary` | scalar Numba device callback is spike-only; action-shaped callback is rejected; no API surface; flags false | planner fails closed except spike-only scalar reduce candidates | planner exposes Tier-3 public API or accepts action-shaped callbacks |
| `stage1_ptx_generation_reliability` | 20 compile attempts, at least 4 scalar variants, PTX headers/symbols, classified failures | Numba reliably emits scalar PTX with `>=95%` reliability | compile reliability `<95%` or callback symbol cannot be identified |
| `stage2_semantic_optix_wrapper_or_direct_callable` | Numba PTX composed with semantic OptiX wrapper/direct-callable ABI; module, program group, pipeline, launch succeed | semantic route succeeds with `>=95%` reliability | only bare helper PTX is tested, or wrapper reliability `<95%` |
| `stage3_correctness_parity` | dense-hit, sparse-hit, no-hit datasets; named CPU/Tier-2 reference; frozen tolerance | `100%` correctness parity | any parity case fails |
| `stage4_overhead_ceiling` | matching hand-written fused baseline; sizes `32768` and `131072`; repeat `>=10`; warmup `>=2` | median callback route `<=1.50x` matching fused route at every size | median overhead `>1.50x` at any required size or any size `>2.00x` |

## What Goal4686 May Do

Goal4686 may implement only a local spike scaffold for the semantic wrapper/direct-callable ABI.

Allowed:

- build a semantic OptiX wrapper/direct-callable plan;
- extract or pin the Numba callback symbol contract;
- compile local dry-run/generated artifacts where possible;
- keep planner fail-closed behavior.

Not allowed:

- POD before the local structure/protocol gate is complete;
- public Tier-3 support wording;
- raw OptiX callbacks as user API;
- app-specific native kernels;
- C ABI/embedding/non-Python-host work;
- declaring V4 release or speedup.

## Goal-Level Decision Audit

1. Was I being stupid?

No. This goal does not repeat the old failed probe; it explicitly forbids treating bare helper PTX as success.

2. If yes, what action made it stupid?

The stupid action would be to rerun `scripts/v4_tier3_optix_module_link_probe.py` and pretend a different result is likely. That old probe already answered the bare-PTX question.

3. Is there another path that avoids getting stuck on a bad premise?

Yes. Use a semantic OptiX wrapper or direct-callable ABI, because OptiX requires semantic entry functions.

4. Can I now try the different path that actually solves the problem?

Yes. Goal4686 can implement the local scaffold for wrapper/direct-callable composition while preserving spike-only boundaries.

## Non-Authorization

Goal4685 does not authorize POD, implementation completion, V4 release, Tier-3 public support, raw OptiX callbacks, public speedup wording, whole-app speedup wording, app-specific native kernels, C ABI, embedding, true-zero-copy, or non-Python host claims.
