# Proposal: Set-A / Set-B Two-Number Release Bar for Phoenix V3

Date: 2026-06-22
Author: Claude (independent reviewer) — **proposal only, not an authorization**
Companion to: `claude_phoenix_v3_external_review_2026-06-22.md`
Status: recommendation for the release owner to accept, amend, or reject. It does not change the mandate by itself.

## Why replace the single 1.20x geomean gate

The current bar is:

```text
overall_geomean_v3_speedup_vs_v2 >= 1.20x
at least 8 of 10 app geomeans > 1.05x
no app geomean < 0.95x without accepted explanation
```

Two problems (argued in the review):

1. **Unreachable by construction for part of the suite.** V3 and V2.14 share the OptiX/Embree backends. Single-primitive apps are already at their backend ceiling, so they cannot clear 1.05x by any generic runtime work — only multi-phase, residency-rich workloads can. Requiring 8/10 over 1.05x can demand speedups that do not exist.
2. **A blended geomean hides the real signal.** Averaging residency-rich probes (where the execution layer compounds) with single-shot/materializing controls (where the target is parity) produces a meaningless ~1.0x that conceals a genuine V3 win on the workloads that matter.

The fix is to measure two populations separately and define the major-version claim on the population the architecture can actually move.

## The two sets

**Set A — Architecture-bearing probes (residency / multi-phase / continuation-rich).**
Workloads with multiple RTDL phases where prepared execution + device residency + continuation can compound. The V3 performance claim is earned here.

Proposed set-A members (release owner finalizes):

- RT-DBSCAN (neighbor query → component-union continuation)
- Barnes-Hut (frontier / fused vector accumulation, multi-phase)
- RTNN (neighbor → ranked summary, chunked)
- Spatial / RayJoin (LSI → PIP → overlay, multi-phase)
- Triangle counting (segment planner → batched count)
- Hausdorff (pairwise threshold summary over streams)

**Set B — Ceiling / control rows (single-shot or contract-materializing).**
Workloads that are one primitive, or whose contract requires host materialization. The V3 target here is **parity**, not speedup. They are negative controls, not failures.

Proposed set-B members (release owner finalizes):

- Lone fixed-radius count / lone any-hit primitive rows
- Robot collision flag stream (single any-hit)
- RayDB bounded grouped count where it is a single fused reduction
- Outlier / ANN single-pass rows
- Any row that must materialize host rows by contract (e.g., RT-DBSCAN Embree neighbor rows)

**Freeze rule:** the A/B classification is committed *before* the paired run, with a one-line rationale per row. No row may be reclassified after results are seen. Reclassification-after-results is itself a measurement-integrity violation and voids the run.

## The bar

```text
# Set A — where the major-version claim is earned
set_a_geomean_v3_vs_v2          >= 1.20x
set_a_apps_over_1_05x           >= ceil(0.75 * |set_a|)     # ~3 of 4, 5 of 6, etc.
set_a_wins_sourced_from         productized execution path (runtime_executed: True),
                                not ad-hoc per-route caches

# Set B — where the target is parity, not speedup
set_b_geomean_v3_vs_v2          >= 0.98x
set_b_any_row_below_0_95x       requires accepted user-language explanation
set_b_rows_must_not             regress because the execution path added overhead

# Both sets
every_surprising_row_explained_in_user_language   = true
classification_frozen_before_run                  = true
serious_same_hardware_all_app_paired_run          = true
```

### Why these thresholds
- **Set-A 1.20x** keeps the maintainer's "material superiority" intent, but applies it only where the architecture can deliver it, so clearing it actually means something.
- **Set-A "sourced from the productized path"** is the anti-hygiene guard: a set-A win produced by another symbol cache does not count, because it proves nothing about V3 as a runtime. This directly enforces Gap 1.
- **Set-B parity (≥0.98x)** makes "do no harm on ceiling workloads" an explicit, passable target instead of an impossible 1.05x demand. It also catches the real risk that the new execution layer *adds* overhead to single-shot rows — a set-B regression below parity is a genuine V3 defect and should block.

## Precondition to spend all-app pod time

Do not run the full paired suite to test this bar until:

```text
execution_path_executes (runtime_executed: True) on >= 2 set_A probes
focused_evidence shows material per-probe gain on those probes
```

Running all-app before the execution layer is live will only re-confirm the blended ~1.01x and waste the pod.

## What clears each verdict

| Outcome | Verdict |
| --- | --- |
| Set A ≥1.20x (from the productized path) AND set B ≥0.98x, all rows explained | candidate for `release_ready` (still requires external re-review) |
| Set A material but set B has unexplained sub-0.95x rows | `block_p1` — fix the execution-path overhead on controls |
| Set A below 1.20x or wins sourced from caches not the path | `approve_blocked_not_release` — Gap 1 not yet delivered |
| Set A regresses or no path executes | `block_p0` — redesign the execution layer |

## Relationship to the mandate

This proposal keeps the spirit of "V3 must be the highest-performance independent-language release line": it still demands material, same-hardware, broad-within-its-class superiority, and still forbids release on a blended 1.01x. It changes only *which population the claim is measured on* and *that the win must come from the runtime, not from per-route caches*. If the release owner prefers to keep the single blended gate, that is their call; this document records the recommendation and the reasoning, and does not alter the gate on its own.
