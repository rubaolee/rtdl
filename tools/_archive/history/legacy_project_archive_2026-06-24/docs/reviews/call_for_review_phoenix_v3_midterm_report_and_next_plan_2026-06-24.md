# Call For Review: Phoenix V3 Midterm Report And Next Work Plan

Date: 2026-06-24
Author: Codex
Audience: external reviewers, release owner, next primary AI
Status: `phoenix_v3_midterm_report_for_external_review_not_release`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
focused_pod_spend_authorized: false
runbook_execution_authorized: false
v4_work_authorized: false
embedding_authorized: false
c_abi_authorized: false
true_zero_copy_claim_authorized: false
```

## 1. Purpose Of This Packet

This packet is written because the Phoenix V3 recovery drifted away from the
agreed trunk-first strategy. It asks external reviewers to judge whether the
current diagnosis and next work plan are correct before more engineering time
or POD time is spent.

The report deliberately separates four categories that were previously mixed:

1. real runtime technical work;
2. local focused evidence;
3. review/gate/process work;
4. mistakes and wasted direction.

The intended reviewer outcome is not release approval. The intended outcome is
a hard decision on the next engineering path.

## 2. Current Bottom Line

Phoenix V3 remains `redo_required`.

The serious same-RT-hardware V2.14 vs current Phoenix V3 paired run remains the
controlling release fact:

```text
same_metric_comparison_count: 52
V3 faster by >5%: 12
within +/-5%: 35
V3 slower by >5%: 5
geomean V3 speedup vs V2.14: 1.012x
actual_app_geomean_wins_gt_1_05x: 1
actual_app_geomean_regressions_lt_0_95x: 2
release_consideration_eligible: false
```

The later frozen Set-A / Set-B scorecard also blocks release:

```text
Set A geomean: 1.013x
Set B geomean: 1.007x
Set A apps over 1.05x: 1 / 5 required
Set A severe regressions below 0.90x: 1
Set B rows below 0.95x: 1
release candidate under two-number bar: false
```

The visible blockers include:

- `barnes_hut`: Set-A app geomean around `0.844x`;
- `librts_spatial_index`: Set-B app geomean around `0.937x`;
- Set-A app-win shortfall;
- RTNN not performance-cleared, with Claude recording 13/14 rows below `1.05x`
  and a `0.988781x` hot-query boundary.

Therefore current Phoenix V3 is not a user-facing performance success.

## 3. The Agreed Strategy

The accepted redesign says:

```text
Step 0  Stop & freeze
Step 1  Build the trunk: make execution graph / prepared runner execute on one
        residency-rich family end to end
Step 2  Generalize: route a second and third Set-A family through the same runner
Step 3  Make residency default and measured
Step 4  Promote continuation into runner-callable core nodes
Step 5  Run all-app only after the trunk is live and materially useful
Step 6  External review and release decision
```

The governing rule is:

```text
Every optimization must land as a reusable runtime capability that flows through
the single execution path. If a change cannot be expressed that way, it is not
V3 core work.
```

## 4. What Work Actually Happened

### 4.1 Work that was useful but not performance progress

Several items improved discipline and prevented further false claims:

- release wording and claim-boundary gates;
- Set-A / Set-B scorecard and all-app freeze;
- Claude / Antigravity / Codex review records;
- fail-closed intake validation for external reviews;
- M70/M71 final 3AI closure for bounded no-execution RTNN protocol and dry-run
  gate;
- final local rebuild after M70/M71:
  `module_count=148`, `Ran 752 tests`, `OK`.

This work is useful as guardrail work. It is not V3 performance progress.

### 4.2 Work that was hygiene or regression repair

The following work helped repair regressions or reduce overhead but mostly
asymptotes to parity:

- symbol/query cache work;
- fixed-radius symbol-cache repair;
- RTNN neighbor symbol-cache hygiene;
- LibRTS AABB count cache repair;
- self-query refresh metadata and device-column cleanup.

Important examples:

- RTNN focused cache work produced about `1.001x` geomean and no material
  release-performance gain.
- Fixed-radius self-query refresh showed about `0.998x` on the relevant CuPy
  A/B and no material speedup.
- Barnes-Hut cache repair recovered some losses toward parity, but did not
  solve the Set-A app blocker.

These changes may stay if correct, but continuing this strategy is the old
failure mode: it pays back Phoenix V3 overhead rather than creating a V3
performance source.

### 4.3 Real runtime / trunk-related work

Some real runtime pieces do exist:

- `prepared_execution_session_runner` exists and focused routes can report
  `runtime_executed: true`.
- M36 added a generic grouped vector-sum / grouped-reduction prepared-session
  helper:
  `run_grouped_vector_sum_2d_prepared_session`.
- M37 added a generic fixed-radius component-union prepared-session helper:
  `run_radius_graph_component_union_3d_prepared_session`.
- The prepared-session surface ledger and export gates were added so helper
  drift can be detected.
- M31/M32 style audit gates made phase/residency/continuation metadata more
  explicit across prepared-session families.

These are genuine runtime-surface improvements. They are not enough by
themselves because a user does not experience a helper existing as performance.
The helper must drive a benchmark front-door path and produce material,
same-contract evidence.

### 4.4 Focused evidence with real technical signal

Two focused families have meaningful, bounded evidence:

1. Component union / fixed-radius component labels

   From the M44 Step-2 sync:

   ```text
   runtime_trunk_executes_end_to_end: true
   internal residency: true
   hot-path host materialization: false
   runner vs Embree hot: 1.221027x
   runner vs Embree wall: 2.421405x
   runner vs legacy wall: 1.254316x
   runner vs legacy hot: about 0.994x
   ```

   Read: positive Step-1/Step-2 family evidence, but not hot-kernel superiority
   over the legacy OptiX route, and not a broad RTDBSCAN app win.

2. Grouped reduction / grouped vector sum

   From M43:

   ```text
   runtime_trunk_executes_end_to_end: true
   internal residency: true
   hot-path host materialization: false
   explicit partner: cupy
   strategy: warp_per_group_tiled
   original shape runner vs CPU hot: 3.454249x
   original shape runner vs legacy hot: 6.670790x
   trusted-offset runner vs CPU hot: 3.634393x
   trusted-offset runner vs legacy hot: 3.316330x
   trusted-offset runner vs legacy wall: 15.409128x
   ```

   Read: this clears a real grouped-reduction CPU-hot inversion for the original
   blocked `262144 x 1024` shape through a productized CuPy prepared-session
   route. It is bounded technical evidence, not all-app or release evidence.

These two families matter. The mistake was not recognizing them as useless. The
mistake was not connecting them rapidly and cleanly to the release-control
front-door scorecard and the next trunk milestone.

## 5. What Went Wrong

### Error 1: The work did not stay hard enough on Step 1

The redesign said the critical path was to make the execution graph / residency
runner execute and source material gains. Instead, too much effort went into
protocol closure, review debt, dry-run harnesses, and gate hardening after they
were already sufficient to prevent false claims.

Those things were not irrelevant, but they displaced the trunk.

### Error 2: Green local tests were allowed to feel like progress

Examples such as `Ran 752 tests OK` certify that local contracts did not break.
They do not certify that Phoenix V3 solves the user problem. The only release
progress is same-contract, same-hardware performance sourced from the runtime
path.

### Error 3: The project kept drifting toward leaf/blocker work

Barnes-Hut, RTNN, LibRTS, and grouped-reduction were often discussed as rows or
apps. The correct framing is different:

- benchmark apps are probes;
- fixes must become runtime capabilities;
- a row win that bypasses the productized runner does not count as V3 core.

### Error 4: M70/M71 became process-complete but not technology-complete

M70/M71 closed a bounded RTNN focused protocol and local dry-run gate with 3AI
review. This was not wrong, but it was not the V3 trunk. It should not have
consumed the center of the work after the core performance failure was already
known.

### Error 5: The current state became hard to read

There are focused packets where `runtime_executed: true` exists, and there are
handoff records saying the current next action is no-execution planning. Both
can be true, but the combined picture is confusing. External review should
decide whether M40/M43 already count as partial Step-1/Step-2 evidence, or
whether the next goal should reset Step 1 against a stricter front-door path.

## 6. Status Against The Claude Steps

| Step | Current status | Honest read |
| --- | --- | --- |
| Step 0: stop and freeze | Mostly complete | Scorecard and no-all-app rules exist. Cache work should stay closed except for correctness regressions. |
| Step 1: build trunk | Partial, not release-controlling | Runner and focused `runtime_executed: true` evidence exist, especially M40 and M43. But there is not yet a current, clean, user-facing benchmark-front-door trunk path that clears the performance bar. |
| Step 2: generalize | Partial, unstable | Component union and grouped reduction are two candidate families. A third family and scorecard connection are not solid. |
| Step 3: residency default | Partial | Metadata/audit exists, but residency is not yet a default measured property across Set-A probes. |
| Step 4: continuation core | Partial | M36/M37 promoted grouped reduction and component union into runner-callable helpers. Ranked summary, topology stream, frontier accumulation, and other continuations remain incomplete or not performance-cleared. |
| Step 5: all-app | Blocked | Do not rerun all-app until Step 1/2/3 have front-door, material evidence. |
| Step 6: release review | Not reached | Existing external reviews are bounded. None authorize release. |

## 7. Recommended Next Work Plan

This section has been revised after Claude's external review
`accept_with_required_amendments` and the companion plan
`docs/reviews/phoenix_v3_revised_m72_plan_target_the_blocker_2026-06-24.md`.

The governing change is:

```text
Point the working runner at the scorecard blocker, using the M43
grouped-reduction win that already exists, and require every trunk family to
name the controlling row it must move before implementation.
```

The original plan overcorrected toward clean runtime families and was
blocker-blind. M40 component union and M43 grouped reduction are meaningful
focused wins, but the current scorecard is held down by different families:
`barnes_hut` around `0.844x`, `librts_spatial_index` around `0.937x`, RTNN not
cleared, and a Set-A app-win shortfall. More wins on already-winning families
will not clear those blockers.

### Goal A: M72, drive the Barnes-Hut / aggregate-tree blocker through the runner

Objective:

```text
Route the Barnes-Hut / aggregate-tree-fused-vector-sum front-door path, the M28
frozen Set-A trunk family with current geomean around 0.844x, through the
productized prepared-session runner, reusing the M43 CuPy grouped-reduction
continuation, and measure same-contract vs the current incumbent that produced
the 0.844x blocker.
```

Why this family:

- it is the leading Set-A blocker, so moving it changes the release bar;
- M28 already froze aggregate-tree fused vector sum as the Barnes-Hut trunk
  family;
- M43 already cleared the grouped-vector-sum inversion that this family
  consumes;
- the observed regression is plausibly tied to generic runtime overhead,
  repeated prepare/pack, and row materialization, which the residency trunk is
  designed to remove.

Exit criteria:

- the Barnes-Hut / aggregate-tree front-door probe runs through the runner, not
  a bypass;
- `runtime_executed: true` is emitted from the path under test;
- internal residency and no-hot-path-host-materialization are measured, not
  asserted;
- the comparison is same-contract and same-hardware against the `0.844x`
  incumbent;
- every evidence packet records `win_source` as one of
  `{residency_wall, partner_continuation, kernel}`;
- the result is classified as material, parity, or negative without changing
  the bar after the fact;
- the report explicitly states whether M72 moved `0.844x` toward or above
  parity.

Estimated effort:

- local implementation and audit: 6 to 10 focused hours;
- focused POD only after external approval: 2 to 4 POD hours;
- budget one retry for residency or contract mismatch.

### Goal B: M73, blocker-map binding gate

Objective:

```text
Before any further family work, bind each candidate trunk family to the exact
scorecard-controlling row it must move, and drop families that move none.
```

Rules:

- name the controlling all-app row or rows for each family before running;
- a family that cannot move a Set-A or Set-B blocker is recorded as bounded
  capability evidence and removed from the release path;
- no app-specific knobs are allowed; the fix must be a reusable runtime
  capability.

Exit criteria:

- every active trunk family has a named blocker target;
- non-moving families are demoted;
- no POD beyond what M72 separately justifies.

### Goal C: own the regression blockers explicitly

Objective:

```text
Decide, per blocker, whether it is trunk-fixable or needs severe-regression
repair.
```

Required ownership:

- `barnes_hut` around `0.844x`: handled first by M72 as a trunk route; if the
  runner does not move it, it becomes a severe-regression repair item;
- `librts_spatial_index` around `0.937x`: diagnose whether the runner added
  overhead or a trivial/control path needs parity repair;
- RTNN: decide whether a productized continuation can move it, or keep it as
  parity/negative-control evidence with no performance clearance.

Exit criteria:

- each named blocker has an owner and a route;
- the route is labeled `trunk_fix` or `severe_regression_repair`;
- `win_source` or regression cause is recorded.

### Goal D: M74, generalize to second and third blocker-bound families

Objective:

```text
Route at least two more Set-A families through the same runner discipline, each
bound to a controlling row, each with win_source classified.
```

Exit criteria:

- at least three Set-A families total use the same runner discipline;
- each family is bound to a scorecard row by Goal B;
- at least two families show material runtime-sourced gain that moves a named
  blocker, or the V3 performance premise must be reconsidered;
- no family uses a bypass to look fast.

Estimated effort:

- local implementation: 10 to 18 focused hours;
- focused POD after review: 4 to 8 POD hours.

### Goal E: M75, make residency and phase accounting first-class

Objective:

```text
Turn residency and phase accounting from packet metadata into required runtime
outputs for Set-A probes.
```

Exit criteria:

- per-phase timing is emitted consistently;
- device-resident intermediate status is measured consistently;
- hot-path host materialization is measured consistently;
- missing telemetry fails closed.

Estimated effort:

- local implementation and tests: 6 to 10 hours;
- no POD required unless telemetry changes affect measured runtime.

### Goal F: M76, only then request all-app authorization

Objective:

```text
Prepare a small external-review packet asking whether all-app POD spend is now
justified.
```

Preconditions:

- at least three Set-A families run through the runner with
  `runtime_executed: true`;
- at least two show material runtime-sourced wins that move named blockers, not
  only local wins;
- `barnes_hut` and `librts_spatial_index` regressions are resolved or owned
  with accepted explanation;
- Set-B overhead risk is mitigated;
- reviewers agree the run answers a release question rather than repeating the
  `1.012x` failure.

Estimated effort:

- review packet: 2 to 4 hours;
- all-app POD only if authorized: 4 to 8 POD hours plus analysis time.

## 8. What Must Be Rejected Now

Reject:

- more symbol-cache or query-cache performance work unless it fixes a correctness
  or severe regression blocker already tied to the trunk;
- any claim that M70/M71 means V3 performance is improving;
- another all-app run before M72/M74/M75 satisfy their preconditions;
- any trunk family that is not bound to a named scorecard-controlling row;
- route-specific RTNN, Barnes-Hut, RayJoin, or LibRTS tuning that cannot be
  expressed as reusable runtime capability;
- public V3-over-V2 wording;
- V4, embedding, C ABI, or true-zero-copy work.

## 9. Questions For External Review

Please answer with one of the verdict labels below and explicit reasoning.

Allowed verdict labels:

```text
accept_plan_continue_m72_target_blocker
accept_with_required_amendments
revise_before_engineering
block_plan_wrong_route
```

Review questions:

1. Is the midterm report honest about the current state, especially the
   difference between guardrail progress and runtime performance progress?
2. Does the report correctly classify M40 component-union and M43 grouped
   reduction as meaningful but bounded focused evidence?
3. Should M40/M43 count as partial Step-1/Step-2 evidence, or should M72 reset
   Step 1 against a stricter benchmark front-door path?
4. Is the revised M72 target, Barnes-Hut / aggregate-tree using the M43
   grouped-reduction runner, the correct next critical path?
5. Is the plan now properly runtime-driven while still being blocker-aware, or
   does it risk falling back into app-specific tuning?
6. Are the resource estimates reasonable?
7. What must be removed, tightened, or added before engineering resumes?

## 10. Explicit Non-Authorization

This packet does not authorize:

- V3 release;
- all-app benchmark run;
- paid POD spend;
- focused POD spend;
- runbook execution;
- public speedup wording;
- broad V3-over-V2 wording;
- RT-core speedup wording;
- paper reproduction wording;
- V4 work;
- embedding;
- C ABI;
- true-zero-copy claim;
- automatic partner selection;
- route-specific app tuning.

## 11. Goal-Level Decision Audit

Decision: write a midterm external-review packet instead of continuing directly
with more Phoenix V3 engineering.

1. Was I foolish?

   Yes, partially. The recent work stayed inside non-release boundaries, but it
   spent too much attention on process closure after the trunk-first strategy
   was already agreed.

2. If yes, what actions made the decision foolish?

   I let M70/M71 review debt, protocol hardening, and dry-run gates become the
   center of work. They were useful guardrails, but they were not the Step-1
   trunk implementation that V3 needs.

3. Was there another path?

   Yes. After minimum guardrails were in place, I should have immediately
   re-entered Step 1 and made one front-door residency-rich family execute
   through the productized runner with measured evidence.

4. Can I now try a different path?

   Yes. The next path is M72: a narrow, reviewed execution-trunk implementation
   target. If external review rejects this plan, revise before more engineering.
   If it accepts the plan, stop expanding process work and implement the trunk.
