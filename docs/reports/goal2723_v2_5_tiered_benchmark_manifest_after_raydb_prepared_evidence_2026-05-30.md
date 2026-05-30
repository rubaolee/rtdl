# Goal2723: v2.5 Tiered Benchmark Manifest After RayDB Prepared Evidence

Date: 2026-05-30
Status: accepted as planning/harness hardening

## Purpose

The recent v2.5 reviews warned that the 10 benchmark apps should not be treated as one uniform Triton parity target. Some apps are grouped scalar reductions that fit the current Triton continuation surface, some need new generic continuation shapes, and some are RT-core baselines with no meaningful partner-continuation phase.

Goal2723 turns that guidance into a machine-checkable manifest:

`rt.v2_5_tiered_benchmark_manifest()`

The manifest is not a release gate and not public performance wording. It is a clean internal map for the next v2.5 pushes.

## Manifest Shape

The manifest partitions the 10 benchmark apps:

| Tier | Count | Meaning |
| --- | ---: | --- |
| A | 4 | Same-contract parity is realistic with current grouped/scalar or count/parity continuation support. |
| B | 4 | Per-app parity bets that require new generic continuation shapes or accepted fallback paths. |
| C | 2 | RT-core / bounded-collection / any-hit baselines; target no-regression, not partner parity. |

Each row records:

- app id;
- benchmark track;
- parity target;
- canonical harness status;
- same-contract opponent;
- required partner operations;
- pod evidence status;
- next action.

## Current Rows

| App | Tier | Track | Immediate status |
| --- | --- | --- | --- |
| `raydb_style` | A | partner continuation | ready with Goal2720/Goal2722 prepared pod evidence |
| `triangle_counting` | A | partner continuation | needs Triton wiring and streaming/OOM closure |
| `spatial_rayjoin` | A | RT-core count/parity | add Triton only if count/parity enters v2.5 timing |
| `librts_spatial_index` | A | RT-core count/parity | needs warm/median harness |
| `rt_dbscan` | B | high-risk partner continuation | needs grouped components or fallback-backed path |
| `rtnn` | B | partner continuation | needs live harness and top-k/ranked-summary mapping |
| `barnes_hut` | B | partner continuation | needs vector-valued reduction or accepted fallback |
| `hausdorff_xhd` | B | partner continuation | needs witness-preserving grouped max/argmax path |
| `contact_manifold` | C | RT-core collection | no-regression target, not partner parity |
| `robot_collision` | C | RT-core any-hit | no-regression target, not partner parity |

## Why This Matters

The old broad question, "Do all 10 apps have v2.5 Triton parity?", is too blunt. The useful question is:

- Which apps can use the current grouped scalar continuation surface?
- Which apps need a new generic continuation primitive?
- Which apps should remain RT-core baselines where partner parity is a category error?

The manifest answers those questions in code so tests can reject accidental overclaiming.

## Boundary

This goal authorizes no public speedup, no true-zero-copy wording, no release claim, and no blanket "all 10 apps have Triton parity" statement.

The manifest only scopes future work. Every performance claim still needs a same-contract command, phase-separated timing, `sm_70+` pod evidence, and review.
