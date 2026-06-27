# Goal 1599: v1.6 Python+RTDL Historical Milestone Readiness

## Verdict

RTDL should treat `v1.6` as the first historical Python+RTDL closure milestone,
but current `main` is not ready to publish that closure yet.

The intended `v1.6` claim is narrow and valuable:

```text
RTDL is a Python-hosted eDSL/runtime that provides a high-performance,
reviewed Embree+OptiX path for the RT-shaped primitive portion of supported
Python caller code that invokes RTDL-managed RT primitives, plus an explicit
bridge between Python control code and native RT execution.
```

The intended claim is not:

```text
RTDL optimizes arbitrary Python code, whole applications, SQL engines, graph
systems, partner tensor programs, or every workload using --backend optix.
```

`v1.6` should close only after the supported Python+RTDL surface is documented,
measured, app-generic at the stable primitive boundary, and accepted by 3-AI
consensus.

## Historical Definition

`v1.6` is the first public milestone where RTDL should be described as really
available as Python+RTDL:

- Python remains the app/control/lowering layer.
- RTDL owns the RT-shaped primitive contract and native backend bridge.
- Embree is the CPU RT backend and same-contract fallback.
- OptiX is the NVIDIA RT backend for the measured RT primitive path.
- Native stable paths should know primitives, buffers, traversal contracts, and
  backend capabilities; they should not require app names or app-specific
  business semantics.
- RTDL does not take responsibility for optimizing arbitrary user Python code.

This matches the accepted roadmap:

```text
v1.5.1-v1.5.10: finish Python+RTDL
v1.6: close and publish Python+RTDL
v1.7-v2.0: build Python+partner+RTDL
```

## Current Evidence

Current `main` already has a strong foundation. The items below are foundation
evidence for a future closure package, not proof that `v1.6` is already ready
to publish:

- `v1.5` is released as the standalone Embree+OptiX language/runtime
  completion release for the supported surface.
- Stable v1.5 primitives are `ANY_HIT`, `COUNT_HITS`,
  `REDUCE_FLOAT(MIN|MAX|SUM)`, and `REDUCE_INT(COUNT|SUM)`.
- `COLLECT_K_BOUNDED` has progressed from experimental semantics into a
  measured Python+RTDL promotion track with generic i64 ABI work, typed host
  buffers, prepared host-output buffers, reduced-copy evidence, and OptiX
  gated-candidate performance experiments.
- The project has explicit public-claim rules blocking whole-app speedup,
  broad RTX acceleration, true zero-copy, package-install support, and release
  actions unless separately reviewed.
- `v1.5.3` and `v1.5.4` artifacts correctly separate reduced-copy and
  allocation/device-memory evidence from true zero-copy claims.
- The threshold-4 OptiX collect-k gated candidate is internally closed as an
  experimental opt-in and does not change defaults or public claims.

Useful anchor artifacts:

- `docs/release_reports/v1_5/release_statement.md`
- `docs/release_reports/v1_5/support_matrix.md`
- `docs/reports/v1_5_1_to_v2_0_python_rtdl_partner_roadmap_proposal_2026-05-06.md`
- `docs/reports/three_ai_v1_5_1_to_v2_0_python_rtdl_partner_roadmap_consensus_2026-05-06.md`
- `docs/reports/v1_5_1_collect_primitives_zero_copy_data_movement_architecture_2026-05-06.md`
- `docs/reports/three_ai_v1_5_1_collect_primitives_zero_copy_architecture_consensus_2026-05-06.md`
- `docs/reports/goal1598_v1_5_4_post_pod_collect_k_consolidation_2026-05-09.md`

## Supported Claim Boundary

The safe `v1.6` public statement should be scoped to exact primitive surfaces:

- Supported stable primitive set.
- Supported backends for each primitive.
- Same-contract correctness evidence for each claimed backend pair.
- Exact measured RT subpaths, not whole applications.
- Explicit Python/native and host/device copy behavior.
- Source-tree usage unless packaging metadata is added and validated.

Allowed wording should say that RTDL accelerates the RT-shaped traversal or
primitive portion where evidence exists. It should not imply that RTDL compiles
or optimizes the user's whole Python application.

## Must Not Claim

Before a separate reviewed gate authorizes otherwise, `v1.6` must not claim:

- whole-app speedup;
- broad database, graph, GIS, ANN, robot, or Barnes-Hut acceleration;
- that every OptiX backend run is an RT-core performance win;
- public speedup for the threshold-4 OptiX collect-k gated candidate;
- stable `COLLECT_K_BOUNDED` promotion unless explicitly promoted by a later
  release-surface decision;
- true zero-copy unless a measured GPU-resident or externally shareable
  device-memory path exists;
- partner tensor handoff or DLPack interoperability;
- package-install support unless packaging metadata is present and validated;
- app-agnostic native internals if compatibility/proof entry points remain.
  Here, compatibility/proof entry points means native symbols, wrappers, or
  dispatch paths kept for historical application-shaped tests that still carry
  app names or app-specific semantics instead of only primitive-level contracts.

## Closure Blockers

The following items block a clean `v1.6` public closure today:

- `COLLECT_K_BOUNDED` still needs an explicit release-surface decision:
  stable primitive, documented experimental surface, or excluded surface.
- The native engine boundary still needs a release audit proving no stable
  primitive path depends on app-specific names or semantics.
- The public docs need a single `v1.6` user-facing story that distinguishes
  Python+RTDL from Python+partner+RTDL.
- Reduced-copy and device-memory language must be harmonized so users do not
  read host typed-buffer reuse as true zero-copy.
- The OptiX gated-candidate mode must remain clearly experimental unless a new
  default-change review accepts it.
- Windows, local Linux, and real NVIDIA pod validation need a final release
  matrix for the exact `v1.6` surface.
- 3-AI consensus is required before declaring the `v1.6` closure.

## No-Pod Work Queue

The next useful local work does not require a GPU pod:

- Write the `v1.6` release-surface proposal with the exact supported primitive
  list, backend matrix, claim wording, and blocked claims.
- Audit docs for wording that suggests whole-app acceleration, broad RTX
  acceleration, true zero-copy, or partner support.
- Audit native and Python wrapper symbol names for stable-path app leakage.
- Create regression tests that lock the `v1.6` blocked-claim flags.
- Prepare the final pod runbook so GPU time validates several closure items in
  one session.

## Pod Work Queue

Do not start a pod for this report alone.

The next pod should be used only after local preparation has a batched command
list. The pod batch should cover:

- final OptiX build preflight from Git;
- exact `v1.6` primitive-surface tests;
- same-contract Embree/OptiX parity where claimed;
- selected performance measurements for exact RT subpaths only;
- copy or transfer-count probes if any device-memory wording is proposed.

## Release Recommendation

Proceed toward `v1.6`, but do not publish it yet.

The project should now convert the current evidence into a formal `v1.6`
release-surface proposal, request Claude and Gemini review, resolve blockers,
and only then decide whether `v1.6` is ready to publish.
