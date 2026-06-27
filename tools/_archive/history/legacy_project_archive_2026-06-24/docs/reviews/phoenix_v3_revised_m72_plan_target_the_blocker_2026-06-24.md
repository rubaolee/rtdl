# Revised Phoenix V3 Next-Work Plan — Target The Blocker, Not The Win

Date: 2026-06-24
Author: Claude (independent reviewer) — **proposed replacement for §7 of the midterm packet; not a release or POD authorization**
Companion to: `claude_phoenix_v3_midterm_external_review_2026-06-24.md`
Status: for the release owner / next primary AI to adopt, amend, or reject.

## Why this replaces the original §7

The original plan proves the trunk on families V3 already wins (component union, grouped reduction). The scorecard is blocked by **regressions in other families** (barnes_hut Set-A 0.844x, librts Set-B 0.937x, RTNN uncleared). Proving more wins where you already win does not clear a bar held down by regressions. This revision aims the trunk at the rows that actually gate release, and it reuses evidence you already have.

## The governing change in one line

> Point the working runner at the **scorecard blocker**, using the **M43 grouped-reduction win** that already exists, and require every trunk family to name the controlling row it must move **before** implementation.

## Goal sequence (revised)

### Goal A — M72: drive the Barnes-Hut / aggregate-tree blocker through the runner

Objective:

```text
Route the Barnes-Hut / aggregate-tree-fused-vector-sum front-door path (the M28
frozen Set-A trunk family, current geomean ~0.844x) through the productized
prepared-session runner, reusing the M43 CuPy grouped-reduction continuation,
and measure same-contract vs the current incumbent that produced 0.844x.
```

Why this family (not fixed-radius self-query):

- It is the **#1 Set-A blocker** (0.844x), so moving it actually changes the bar.
- M28 already froze it as the Set-A trunk family; M43 already cleared the grouped-vector-sum inversion it consumes — the pieces exist.
- Its regression is attributed to generic runtime overhead / repeated prepare-pack / row materialization — exactly what internal residency removes — so the trunk is the plausible fix, not app tuning.

Exit criteria:

- the Barnes-Hut/aggregate-tree front-door probe runs through the runner, not a bypass;
- `runtime_executed: true` emitted from the path under test;
- internal residency and no-hot-path-host-materialization are **measured**, not asserted;
- same-contract, same-hardware comparison against the 0.844x incumbent;
- **`win_source` recorded** as one of `{residency_wall, partner_continuation, kernel}`;
- result classified material / parity / negative **without changing the bar after the fact**;
- explicit read: did it move 0.844x toward/above parity, or not.

Estimated effort: 6–10 focused local hours; 2–4 POD hours **only after external approval**; budget one retry for residency/contract mismatch.

### Goal B — M73 (now the gate, not an afterthought): blocker-map binding

Objective:

```text
Before any further family work, bind each candidate trunk family to the exact
scorecard-controlling row it must move, and drop families that move none.
```

Rules:

- name the controlling all-app row(s) for each family **before** running;
- a family that cannot move a Set-A/Set-B blocker is recorded as bounded evidence and **dropped from the release path** (kept only as capability evidence);
- no app-specific knobs; the fix must be a reusable runtime capability.

Exit criteria: every active trunk family has a named blocker target; non-moving families demoted. No POD beyond what M72 already justifies.

### Goal C — Own the regression blockers explicitly

Objective:

```text
Decide, per blocker, whether it is trunk-fixable or needs severe-regression repair.
```

- barnes_hut 0.844x: handled by Goal A (trunk route). If the runner does not move it, it becomes a **severe-regression repair** item (permitted by the rules as an exception, since <0.90x).
- librts_spatial_index 0.937x (Set-B): diagnose source; Set-B target is parity (≥0.98x). If the new runner *added* the overhead, fix or fast-path the trivial case.
- RTNN: classify whether any productized continuation can move it, or accept it as parity/negative-control.

Exit criteria: each named blocker has an owner and a route (trunk-fix or repair), with `win_source`/regression cause recorded.

### Goal D — M74: generalize to a second/third blocker-bound family

Objective:

```text
Route at least two more Set-A families through the same runner discipline, each
bound to a controlling row, each with win_source classified.
```

Exit criteria:

- ≥3 Set-A families total use the same runner;
- each is bound to a scorecard row (Goal B);
- **at least two show a material runtime-sourced gain that moves a blocker** — or the V3 performance premise is reconsidered (capability/quality release, not a speed release);
- no family uses a bypass to look fast.

Estimated effort: 10–18 local hours; 4–8 POD hours after review.

### Goal E — M75: residency + phase accounting first-class (unchanged)

Per the original §7 Goal D: per-phase timing, measured device-resident intermediate status, measured no-hot-path-host-materialization, telemetry fails closed if missing.

### Goal F — M76: only then request all-app authorization (unchanged, preconditions tightened)

Preconditions to request the all-app run:

- ≥3 Set-A families run through the runner with `runtime_executed: true`;
- ≥2 show material runtime-sourced wins **that move named blockers** (not just local wins);
- barnes_hut and librts regressions resolved or owned with accepted explanation;
- Set-B overhead risk mitigated;
- reviewers agree the run answers a release question rather than repeating the 1.012x failure.

## What must be rejected (unchanged, plus one)

All §8 rejections stand. Add: **reject any trunk family that is not bound to a named scorecard-controlling row** — proving the trunk on a non-blocker family is the new version of the old leaf-work failure.

## The decision this plan forces

After Goal A (M72) and Goal D (M74), one of two things is true:

1. The runner moves real blockers (barnes_hut and ≥1 more) with honest `win_source` → V3 has a genuine performance source; proceed toward M76.
2. The runner executes cleanly but moves no blocker → V3's broad-speedup premise is wrong; **reframe V3 as a capability/quality release and stop chasing a speed number it has no source for.** Do not fake it; change the claim.

Either outcome is a real result. The current plan risks a third, useless outcome — more clean wins on non-blocker families and a still-blocked bar — which this revision is designed to prevent.
