# V3 Completion Roadmap — From Blocked to Done

Date: 2026-06-24
Author: Claude (independent reviewer) — master map, **not a release/POD authorization**
For: Main AI / next primary agent / release owner
Companions:
- `v3_engineering_targets_fused_barnes_hut_trunk_2026-06-24.md` (Phase A detail)
- `phoenix_v3_revised_m72_plan_target_the_blocker_2026-06-24.md`
- `phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md`
- `STOP_THE_CHURN_PHOENIX_V3_HIT_THE_BLOCKER_2026-06-24.md`

This is the whole remaining path from the current `redo_required` state to a
truly finished V3. Phases are dependency-ordered. "Done" has two legitimate
shapes (Phase H); both are real completions.

## Cross-cutting rules (apply to every phase)

1. **Correctness parity is a gate equal to performance.** A routed family whose
   results do not match the reference does not count, no matter how fast.
2. **One definition of progress:** a named scorecard blocker moving on
   same-contract, same-hardware measurement, with `host_materialization_in_hot_path:
   false` and a recorded `win_source`. Green tests, milestone numbers, audit
   surfaces, promotion ledgers, blocked external reviews are not progress.
3. **No process churn.** No audit/review/protocol milestones between engineering
   targets. External review only where this map says so (Phase D).
4. **"Done" is not "faster."** V3 is finished when the runtime is unified, the
   claims are honest and gated, and a user can learn it — not when a geomean
   hits a number.

---

## Phase A — Prove the performance source (the trunk)
**Purpose:** answer "does V3 have a real performance source at all."
**Tasks:** T1–T6 from the engineering-targets doc — instrument barnes_hut, route
it through the fused device-resident prepared-session trunk, measure vs 0.844x;
route a second blocker (librts); flip the execution graph live; promote the two
continuations; focused scorecard re-read of routed rows only.
**Exit gate:** ≥2 named blockers moved by the runner, `runtime_executed: true`,
hot-path host materialization measured false, parity verified, `win_source`
recorded.
**Forbidden:** all-app runs, external-review packets (T1–T5 need none), per-route
bypass, optimizing a family that is not a blocker.
**DECISION FORK 1:** blockers move → Phase B. Blockers do not move and the cost
is the kernel itself → jump to Phase H capability branch (do not fake it).

## Phase B — Generalize to all Set-A and clear every regression
**Purpose:** turn one proof into a release-controlling result.
**Tasks:**
- route every Set-A family (RT-DBSCAN, RTNN, Triangle, Hausdorff, Spatial/RayJoin,
  Barnes-Hut) through the same runner, each bound to the scorecard row it must move;
- resolve every Set-A severe regression (<0.90x) and every Set-B row (<0.95x);
  give RTNN an explicit verdict (trunk-fixable / parity / negative control);
- correctness parity verified per family.
**Exit gate:** the frozen Set-A/Set-B scorecard clears the redefined two-number
bar on focused measurement; every family has parity + `win_source`.
**Forbidden:** app-specific knobs, reclassifying A/B after results, counting a
non-blocker win.

## Phase C — Make residency/continuation the default runtime
**Purpose:** stop being N route-shaped pipelines; become one runtime.
**Tasks:** execution graph executes for all routed families; continuation
planner/executor is the general mechanism (not per-route copies); prepared-session
reuse is the documented default; phase telemetry mandatory and fail-closed.
**Exit gate:** a third+ family reuses the same continuation nodes with no new code
path; "the runtime" is one coherent path.
**Forbidden:** a special bypass that makes one family look fast.

## Phase D — Serious all-app run + external review + authorization
**Purpose:** convert focused evidence into a release decision.
**Tasks:** same-hardware all-app paired run; read on the two-number scorecard;
every surprising row explained in user language; external verdict per
`phoenix_v3_bounded_external_review_protocol_2026-06-22.md`.
**Exit gate:** `release_ready` external verdict against the redefined bar, or an
honest move to Phase H.
**Forbidden:** running all-app before B/C exit; promoting release wording from a
missing verdict.
**DECISION FORK 2:** bar cleared → high-performance release (Phase E→H). Bar not
cleared → capability reframe (Phase H branch).

## Phase E — Productize the user-facing surface (only after performance is real)
**Purpose:** make V3 learnable and honestly claimed. This is the work v3.0 did
prematurely and had to retract; it is legitimate only now.
**Tasks:**
- rewrite the app-author strategy from the proven runtime (the old one is
  quarantined);
- clean current docs; examples use the runner path, not the legacy materializing
  path;
- route-choice / partner-selection policy;
- claim boundaries aligned exactly to the proven evidence; backend maturity honest.
**Exit gate:** an app author can go README → docs → examples → validation with no
stale and no over-claimed material.
**Forbidden:** any claim not backed by a named, measured artifact.

## Phase F — Validation gates and anti-drift
**Purpose:** keep V3 from silently regressing or re-over-claiming.
**Tasks:** machine gates for `win_source` required, residency fail-closed,
scorecard gate, claim-boundary gate; **extend history fencing to the build and
test layers** (the exact v3.0 leak); forbid per-route bypass.
**Exit gate:** a regression or an over-claim trips a gate, not a reviewer.

## Phase G — Repo hygiene and version truth (do this early too)
**Purpose:** make the committed repo match the V3-only reality.
**Tasks:** commit the consolidated rebuild work; retire the HEAD
"V4.0.0 promoted" state per the 06-20 decision; fence V4 preparatory material to
history; make VERSION and all markers consistent.
**Exit gate:** the committed repo truth equals the V3-only mandate (today they
conflict — HEAD still promotes V4.0.0 while all work disavows it).
**Note:** safe to start now; do not turn it into a milestone series.

## Phase H — Release, or honest reframe (both are completion)
**Purpose:** finish V3 honestly, in whichever shape the evidence earned.
- **Performance is real:** release V3 as a residency-aware high-performance
  execution runtime — material, explained wins on the workloads it targets,
  parity elsewhere. Public wording scoped to proven rows.
- **Performance did not materialize:** release V3 as a capability/quality release
  — a productized, residency-aware execution runtime — and drop every
  "broadly faster than V2" claim. This is a real, finished V3, not a failure.
**Exit gate:** a release whose claims exactly match the evidence, authorized by
the release owner with an accepted external verdict.

---

## Dependency summary

```text
A ──> B ──> C ──> D ──> E ──> F ──> H
                   │
G (do early, anytime)        Fork 1 after A, Fork 2 after D
```

- A→B→C must precede D.
- E and F must come after performance is real (A/B), or it is premature
  productization again.
- G should be done early; the committed repo is currently wrong.
- H is reached either way; the only dishonest path is faking a number to avoid
  the capability reframe.

## Non-authorization

This map authorizes nothing: no release, no POD spend, no all-app run, no
public/broad V3-over-V2 wording, no V4/embedding/C-ABI. Gate stays
`redo_required` until Phase D produces an accepted verdict against the redefined
bar.
