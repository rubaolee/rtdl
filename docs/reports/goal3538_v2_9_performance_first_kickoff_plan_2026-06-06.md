# Goal3538: v2.9 Performance-First Kickoff Plan

Date: 2026-06-06

Status: v2.9 kickoff plan; not implementation evidence and not public release
authorization.

## Goal

v2.9 is the performance-first version. Its job is not to add another layer of
architecture labels. Its job is to make the benchmark apps faster in a way that
is measurable, repeatable, app-agnostic in the engine, and honest against v2.3
and v2.8 evidence.

The starting point is Goal3536:

- six rows reached 10-second steady-state evidence;
- five rows remained partial because they need repeat hooks or resident loops;
- the true 10s subset is near parity, not a performance leap;
- Barnes-Hut and LibRTS remain weak rows;
- RayDB's previous large sum speedup was short-run noise.

## Engineering Rules

1. Primitive-first remains the default.
2. App-specific native-engine code is forbidden.
3. Users choose partners explicitly; the runtime must not silently choose
   PyTorch, CuPy, Numba, or Triton.
4. Performance claims must name app, contract, backend, partner, scale, phase,
   commit, hardware, artifact, and correctness oracle.
5. Sub-millisecond rows cannot be headline evidence unless they are stretched
   by resident loops, repeat hooks, or larger scale.
6. Do not compare evolved contracts as fake same-contract ratios.
7. Prefer one RTX pod profile per packet, with progress logs and timeouts.
8. No public release, speedup, broad RT-core, true-zero-copy, package-install,
   or paper-reproduction claim is authorized by this plan.
9. Hardware continuity is required for comparison packets: use the same A5000
   class evidence chain when possible, or mark cross-hardware rows with an
   explicit caveat and do not mix them into a single speedup aggregate.

## Workstream 1: Complete The 10s Harness Coverage

Add app-level repeat hooks or resident loops for the five Goal3536 partial rows:

| Priority | App row | Required v2.9 work |
| --- | --- | --- |
| P0 | Barnes-Hut node coverage | Add repeat/resident loop, preserve oracle, diagnose `0.464x`, recover to at least parity or classify as honest regression. |
| P0 | spatial RayJoin promoted contracts | Add large-scale resident loops for count/parity, relation columns, payload continuation, and overlay continuation. |
| P1 | Hausdorff X-HD threshold | Add repeat hook and larger-scale prepared query loop; separate RT threshold path from exact continuation. |
| P1 | robot collision prepared buffers | Replace runaway repeat behavior with bounded resident-loop accounting. |
| P2 | LibRTS AABB index | Add repeat hook, larger scale, and setup/query phase split. |

Acceptance:

- every promoted benchmark row has either 10-second hot-loop evidence or an
  explicit reason why 10-second evidence is invalid for that contract;
- no row is silently partial;
- all rows record observed repeat count, target seconds, measured hot-loop
  seconds, wall seconds, timeout, and correctness status.

## Workstream 2: Repair Weak Rows Before New Feature Work

v2.9 P0 performance targets:

| Row | Current Goal3536 reading | v2.9 close rule |
| --- | ---: | --- |
| Barnes-Hut node coverage | 0.464x | recover to at least 0.95x against v2.3 same-contract evidence, or write a bounded root-cause/honest-regression report |
| LibRTS AABB index | 0.894x | recover to at least 0.95x, or prove the deficit is measurement/setup dominated |
| spatial RayJoin | 1.046x partial | replace with large-scale promoted-contract table; no single noisy RayJoin number |
| RayDB count/sum | 0.973x / 0.998x | keep separate; decide whether launch floor is already the lower bound |

Acceptance:

- no weak row is hidden behind an average;
- any regression below 0.95x is named in the summary table;
- repaired rows include before/after artifacts on the same hardware class.
- an `honest_regression` classification, especially for Barnes-Hut, requires at
  least one independent external AI review before the row can be considered
  closed for v2.9 planning.

## Workstream 3: Resident Execution And Batching

v2.9 should prioritize reusable runtime mechanics that reduce launch, packing,
and host orchestration overhead:

- resident prepared-query loops;
- bounded repeat hooks in app runners;
- batched prepared handles where the contract naturally repeats;
- CUDA graph replay only if correctness is fail-closed;
- persistent stream or executor pools only where they preserve determinism;
- device-resident grouped reductions only when they remain generic primitives.

This work must remain app-agnostic. A benchmark can motivate a primitive, but
the native ABI must expose a generic contract.

Sequencing boundary: Workstream 3 starts only after V2.9-G2 produces and
reviewers accept a full 10-second table with no silent partial rows. Until then,
new resident pools, CUDA graph replay, and device-resident grouped-reduction
features are design candidates, not implementation targets.

## Workstream 4: Benchmark Table Policy

The v2.9 table must contain two views:

1. **same-contract diagnostic view**: v2.3/v2.8/v2.9 where the contract is
   truly identical;
2. **promoted-contract view**: current best v2.9 reference implementation,
   explicitly marked as evolved-contract or capability-new when needed.

For each app, the table must provide a reader-facing summary row, but the
artifact must keep contract-level rows underneath it. A single app summary may
use a weighted or scenario-specific aggregate only if the weighting rule is
written down before measurement.

## Initial v2.9 Goal Sequence

| Goal | Purpose |
| --- | --- |
| V2.9-G1 | Add repeat/resident hooks for the five Goal3536 partial rows. |
| V2.9-G2 | Rerun the A5000 10s steady-state table with no silent partial rows. |
| V2.9-G3 | Barnes-Hut P0 diagnosis and repair/classification. |
| V2.9-G4 | Spatial RayJoin promoted-contract large-scale packet. |
| V2.9-G5 | LibRTS scale and phase-split repair/classification. |
| V2.9-G6 | RayDB lower-bound/launch-floor study for count and sum. |
| V2.9-G7 | Final v2.9 performance packet with same-contract and promoted-contract views. |

## Review Questions

External reviewers should answer:

1. Is v2.9 correctly scoped as performance-first?
2. Are the P0 priorities right?
3. Does the plan preserve the app-agnostic engine boundary?
4. Does it avoid fake same-contract ratios for evolved contracts?
5. Are the repeat-hook and 10-second evidence rules strong enough?
6. Is anything missing before implementation starts?

## Codex Position

Codex recommends `accept-with-boundary`.

v2.9 should start with repeat/resident coverage and weak-row repair before new
partner, discovery, or documentation work. The result we want is not a prettier
table; it is real, stable, reproducible performance.
