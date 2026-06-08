# Goal3990 Dense Fixed-Radius Grouped-Union Primitive Design

Date: 2026-06-08

## Verdict

`accept-with-boundary`

Goal3987, Goal3988, and Goal3989 have narrowed the RT-DBSCAN performance problem to a generic runtime primitive gap. The current RTDL/OptiX grouped stream is already the fastest available route on the measured profile, and partner-only opponents are much slower. The next improvement should therefore be a generic dense fixed-radius grouped-union primitive, not another app-specific benchmark tweak.

This report is a design packet. It does not change native ABI, promote a route, or authorize public speedup wording.

## Evidence Base

| Goal | Evidence | Design consequence |
| --- | --- | --- |
| Goal3987 | Blocked query ranges, direct side effects, and same-root toggles were probed. None beat the current grouped stream. | Existing knobs are exhausted; do not spend more pod time on simple route flips. |
| Goal3988 | RTDL/OptiX grouped stream was about `20x` faster than the Numba-only prepared-grid opponent and about `86x` faster than the CuPy-only prepared-grid opponent at `65536` points. | The correct direction remains primitive-first RTDL/OptiX, not partner substitution. |
| Goal3989 | Parent atomic attempts were about `1.24` per point; same-root culling remained faster than disabling it. | Atomics are not the sole bottleneck. Candidate traversal, root reads, and remaining unions must be optimized together. |

## Primitive Contract

Working name:

`fixed_radius_grouped_union_dense_3d`

The primitive consumes:

- prepared fixed-radius query/search geometry,
- a stable group key per element,
- a deterministic component-root policy,
- optional prepared cell/partition metadata when available,
- optional root-cache snapshot metadata with explicit staleness rules.

The primitive produces:

- component parent/root columns or an equivalent component summary,
- convergence/status counters,
- candidate/union telemetry counters,
- explicit failure/status flags when convergence, staleness, capacity, or determinism rules are not satisfied.

The primitive must remain generic. It may use terms such as fixed-radius pairs, groups, roots, components, partitions, candidate pairs, and union events. It must not use native ABI names or native implementation vocabulary tied to DBSCAN, clustering policy, epsilon/min-points semantics, noise/core labels, or benchmark application names.

## Candidate Implementation Directions

| Direction | Potential win | Risk / acceptance need |
| --- | --- | --- |
| Component-aware root-cache snapshot | Reduces repeated root reads during dense same-root culling. | Must expose snapshot staleness and prove convergence; stale roots cannot silently alter components. |
| Multi-pass contraction | Reduces repeated dense candidate work after components begin to merge. | Requires deterministic convergence policy and bounded iteration metadata. |
| Candidate compaction before union | Reduces union/root-read pressure for duplicate or already-same-component candidate pairs. | Needs a generic compaction contract and same-contract parity against the existing route. |
| Cell/partition-assisted grouped union | Uses prepared spatial partitions to skip or summarize dense local pairs. | Only legal when the prepared structure exposes safe partitions; must fail closed otherwise. |

## Acceptance Criteria

Before this design can become an implementation goal, the next packet should define:

1. A native ABI naming proposal that contains no DBSCAN or clustering vocabulary.
2. A deterministic root/component policy, including tie-breaks and output order.
3. Staleness/convergence metadata when root snapshots or multi-pass contraction are used.
4. Same-contract parity tests against the current grouped-stream route on dense and sparse fixtures.
5. Pod performance evidence on the current `clustered3d` profile and at least one sparse or mixed-density profile.
6. A claim-boundary block that keeps release, broad RT-core speedup, whole-app speedup, true-zero-copy, automatic partner selection, and app-specific native-engine claims unauthorized.
7. Independent external review before native ABI changes are treated as promoted.

## Boundary

This is internal design evidence only. It does not authorize release, public speedup wording, broad RT-core speedup wording, paper-reproduction wording, whole-app acceleration wording, true-zero-copy wording, automatic backend/partner selection, or app-specific native-engine logic.

