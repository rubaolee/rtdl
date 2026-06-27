# Phoenix V3 Current Status, Next Goals, And Pod Resource Plan

Date: 2026-06-22
Status: `phoenix_v3_redesign_in_progress_not_release`
Scope: Phoenix V3 only

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_claim_authorized: false
external_embedding_or_zero_copy_claim_authorized: false
all_app_pod_spend_authorized: false
```

## Current State

Step 0 is complete. The cache/prepared-query hygiene thread is closed as a
strategy, the Set-A/Set-B release read is frozen, and the all-app runner is
guarded so it cannot be run accidentally as release evidence.

Step 1 has one real structural credential, but not a performance win:

| Fact | Result |
| --- | ---: |
| RTDBSCAN runner vs legacy OptiX grouped-stream | `0.994858x` |
| RTDBSCAN legacy vs Embree control | `2.942860x` |
| RTDBSCAN runner vs Embree control | `2.927729x` |
| Runtime trunk executes all runner samples | `true` |
| Internal V3 residency across RTDL phases | `true` |
| Hot-path host materialization in runner samples | `false` |
| Material Set-A candidate | `false` |
| Claude external verdict | `approve_blocked_not_release` |

Interpretation: RTDBSCAN proves that the productized runner can execute and
record internal residency, but it does not prove V3 performance. The legacy
OptiX grouped-stream route already had the OptiX-over-Embree advantage and
already avoided hot-path host materialization, so the runner mostly makes the
route auditable rather than faster.

## What Is Still Missing

Phoenix V3 is still missing a runtime-sourced material performance source. The
current gap is not "more benchmark apps"; it is proving that the runtime trunk
can eliminate a real cross-phase cost in a reusable way.

All-app pod runs remain blocked until focused probes show material
runtime-sourced wins on honest Set-A families. Running all-app now would mostly
repeat the old blended `1.012x` result.

## Next Controlled Goals

| Goal | Work | Wall Time | Pod Time | Exit |
| --- | --- | ---: | ---: | --- |
| G1 | RayJoin legacy materialization audit | `0.5-1.5h` | `0-0.25h` | Prove whether LSI-to-PIP/overlay crosses host |
| G2 | RayJoin runner trunk path + local tests | `2-4h` | `0h` | Same runner path, no app ABI, metadata/tests pass |
| G3 | RayJoin focused same-pod A/B | `0.5-1.5h` | `0.5-1.5h` | Runner vs legacy result, external review |
| G4 | Second family or Barnes-Hut fallback | `3-6h` | `0.5-2h` | Generalization beyond one family |
| G5 | Full all-app paired run | `2-5h` | `2-5h` | Only after focused gates justify it |

At the user's pod price estimate of about `$1 / 4h`, the first meaningful
RayJoin go/no-go window should cost roughly `$0.13-$0.44` of pod time if G1
finds a real source. A responsible release-candidate path, if the engineering
works, is more like `8-18h` wall time and `3-8h` pod time (`$0.75-$2.00`).

## Next Decision

Proceed with RayJoin only if a cheap legacy-path audit finds an actual
inter-phase host boundary that V3 can remove. If RayJoin is already
device-resident across phases, stop it as the next material probe and audit
Barnes-Hut frontier/vector accumulation instead.

Do not continue RTDBSCAN micro-tuning as the main path. It can remain a
structural runner credential, but not a material performance candidate.

## Goal-Level Decision Audit

1. Was I foolish?
   No for stopping RTDBSCAN as a material probe; yes would be continuing to
   sell or tune it after the `0.994858x` incumbent result.
2. If yes, what actions would make the decision foolish?
   Counting runner-vs-Embree as V3 speedup, ignoring legacy-vs-Embree, or
   spending all-app pod time before identifying a real inter-phase cost.
3. Was there another path?
   Yes: keep doing cache hygiene and blended all-app geomean. That path already
   produced `1.012x` and does not solve V3.
4. Can I now try a different path that solves the problem?
   Yes: audit RayJoin for a real cross-phase host boundary, build only through
   the productized runner, and run focused pod A/B only if the source exists.

## Non-Authorization

This plan authorizes no release, no public speedup wording, no broad
V3-over-V2.x wording, no true-zero-copy wording, no external embedding wording,
and no full all-app pod spend. Release remains `redo_required`.
