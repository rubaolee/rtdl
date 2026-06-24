# Scorecard Classification Update — Barnes-Hut (handled under the freeze rule)

Date: 2026-06-24
Author: Claude (independent reviewer)
Context: Goal 0 verdict `claude_goal0_verdict_barnes_hut_2026-06-24.md`
Frozen source (DO NOT retro-edit): `phoenix_v3_set_a_set_b_classification_2026-06-22.json`

## The integrity problem first

The revised-goals rule says: **classification is frozen before the run; no
reclassification after results.** Moving Barnes-Hut out of Set-A *after seeing it
fail* could be the exact metric-gaming that rule forbids ("it regressed, move it
so it stops dragging the Set-A geomean"). So this update is deliberately
constrained:

1. **The frozen 2026-06-22 classification is NOT edited.** Barnes-Hut stays Set-A
   in that artifact. The serious paired run and the Set-A scorecard that already
   failed still count Barnes-Hut in Set-A. Nothing retroactively "passes."
2. The reclassification below takes effect **only for a future, newly-frozen
   scorecard**, and only as a **structural** correction, not a result-driven one.
3. It must not be used to claim the current Set-A now clears the bar.

## The structural justification (not "it regressed")

Barnes-Hut is reclassified because of a *structural* property discovered by the
phase telemetry, independent of the size of the regression:

```text
Barnes-Hut end-to-end is dominated by RT traversal / force-kernel work that V3
and V2.14 SHARE. The V3 trunk levers (residency, no host materialization) are
already fully applied (hot_path_host_materialization=false). Therefore no
runtime-sourced speedup over V2.14 is physically available: the family is
backend-bound.
```

A backend-bound family belongs in the **control / parity** population (target:
parity-with-explanation), not the **performance-probe** population (target:
≥1.20x runtime-sourced). This would be true regardless of whether Barnes-Hut
landed at 0.84x, 0.95x, or 1.00x — it is about *where the time goes*, not *what
the number was*.

## Precondition before this update is final

Backend-boundedness must be **confirmed from `phase_seconds`**, not asserted:

```text
REQUIRED: phase_seconds shows the dominant fraction of wall time is in the
shared RT traversal / force kernel, and the trunk-removable phases
(prepare/pack/host-materialization) are already negligible.
```

If, instead, telemetry shows a fat trunk-removable phase still remaining, then
Barnes-Hut is **not** backend-bound, this reclassification is void, and
Barnes-Hut stays a Set-A probe with unfinished trunk work.

## Recorded status for Barnes-Hut (future scorecards)

```text
app: barnes_hut_force_app
trunk_status: trunk_proven (runtime_executed, residency, parity, no host mat)
performance_class: backend_bound_parity_control   # pending phase_seconds confirm
geomean_observed: ~0.9526x (regression recovery, not a gain)
win_source: residency_wall
target_on_future_scorecard: parity-with-explanation (Set-B-style)
further_tuning: forbidden
public_wording: internal only — "trunk executes, near parity, backend-bound,
                no host materialization"
```

## What this does NOT do

- Does not move Barnes-Hut to improve any existing Set-A number.
- Does not reduce the count of Set-A *performance* families that must still clear
  ≥1.20x on a future frozen run. Reclassifying Barnes-Hut as a control means the
  Set-A win bar must be met by *other, winnable* families — it does not lower the
  bar, it raises the burden on the reselected families.
- Does not authorize release, all-app, or any speedup wording.

## Net

Barnes-Hut: trunk proven, backend-bound, near-parity control (pending phase
confirmation). The V3 performance premise is still open and must be proven on a
family with a stated, winnable hypothesis — per the Goal 0 verdict's
anti-avoidance lock — or V3 reframes to a capability release.
