# Goal4205: RT-DBSCAN Single-Pass Multi-Seed Parity Gate

Date: 2026-06-09

## Purpose

Goal4202 proved that the fast one-pass grouped-stream route matches the
Goal4194 deterministic reference on one seed. Goal4205 broadens that evidence
across multiple seeds and fixture shapes before any route-promotion wording is
changed.

## Method

The pod reran `scripts/goal4202_rt_dbscan_single_pass_reference_parity.py` on an
RTX 4000 Ada pod for four seeds:

- `20260519`
- `20260609`
- `7`
- `42`

Each seed covered the same four CPU-reference-capable fixtures:

- `tiny`, 9 points
- `clustered3d`, 512 points
- `road3d`, 1,024 points
- `ngsim_dense`, 1,024 points

The runner compares both native policies against
`predicate_aware_boundary_union_reference(...)`:

- `lowest_candidate_then_root`, native pass count `1`
- `lowest_component_root_two_pass`, native pass count `2`

## Results

All 16 seed/fixture cases passed:

- default one-pass labels matched the Goal4194 reference;
- two-pass labels matched the Goal4194 reference;
- default one-pass labels matched two-pass labels;
- all mismatch counts were zero;
- all claim-boundary flags remained false.

| Seed | Tiny | Clustered3D | Road3D | NgSim Dense |
| --- | --- | --- | --- | --- |
| `20260519` | pass | pass | pass | pass |
| `20260609` | pass | pass | pass | pass |
| `7` | pass | pass | pass | pass |
| `42` | pass | pass | pass | pass |

The candidate-pair counts varied as expected for stochastic fixtures:

| Seed | Clustered3D pairs | Road3D pairs | NgSim Dense pairs |
| --- | ---: | ---: | ---: |
| `20260519` | 6,138 | 8,778 | 1,869 |
| `20260609` | 6,385 | 8,716 | 1,837 |
| `7` | 6,180 | 8,612 | 1,888 |
| `42` | 6,263 | 8,705 | 1,820 |

Artifacts are stored under:

`docs/reports/goal4205_rt_dbscan_single_pass_multi_seed_parity_rtx4000ada/`

## Decision

The evidence now supports this engineering position:

- keep `lowest_component_root_two_pass` as an explicit reference/debug policy;
- keep the one-pass route as the performance route;
- do not spend performance budget on two traversals when one-pass is matching
  the deterministic reference on all current parity fixtures.

This does not yet promote the route to release-facing default status. Promotion
still needs larger policy-bound component-size signature evidence and external
review of the exact wording.

## Boundary

Goal4205 does not authorize release, route promotion, public speedup claims,
whole-app speedup claims, true-zero-copy claims, automatic partner selection, or
app-specific native engine logic.

## Next Work

The next major performance/design step is to make the current one-pass policy
name and metadata less misleading. The runtime behavior is now closer to
"single-pass candidate-root observed and final-root resolved" than the older
`lowest_candidate_then_root` wording suggests. That should be handled as a
compatibility-safe metadata/API cleanup after external review.
