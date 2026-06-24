# Phoenix V3 Remaining Work And Resource Plan

Date: 2026-06-22
Status: planning document for user review; not release authorization.

## Current State

Phoenix V3 remains `redo_required`.

The controlling facts are:

- serious same-RT-hardware V2.14 vs Phoenix V3 all-app result: `1.012x`
  geomean, release ineligible;
- Claude verdict: `approve_blocked_not_release`;
- one material Set-A runner-backed focused result exists: AABB M2.1, pending
  external review, not release authorization;
- RTDBSCAN component-signature route is wired through the productized runner
  and has pod evidence. M3.1 failed as the second material Set-A candidate:
  `0.503809x` geomean versus the incumbent legacy OptiX grouped-stream route.
  M3.2 fixed generic runner fingerprint overhead and recovered to `0.992998x`
  geomean versus the incumbent, but this is parity recovery, not material
  speedup;
- full all-app rerun is not authorized until at least two Set-A probes have
  runner-backed focused evidence and Set A / Set B classification is frozen.

Cost assumption from the user:

```text
pod cost: about $1 / 4 hours = about $0.25 / hour
```

## Resource Summary

Best-case path:

```text
active engineering/review time: 12-22 hours
pod time: 6-12 hours
estimated pod cost: $1.50-$3.00
calendar: 1-3 focused days, depending on external review latency
```

Expected controlled path:

```text
active engineering/review time: 20-40 hours
pod time: 12-24 hours
estimated pod cost: $3.00-$6.00
calendar: 3-6 focused days
```

Rescue path with one failed Set-A route or one optimization loop:

```text
active engineering/review time: 40-80 hours
pod time: 24-48 hours
estimated pod cost: $6.00-$12.00
calendar: 5-10 focused days
```

Hard stop recommendation:

```text
Do not keep spending pod time past 48 additional pod hours without a new user
decision. If two runner-backed Set-A route attempts fail to produce material
focused evidence, pause Phoenix V3 and write a handoff instead of continuing.
```

## Goal 1 — RTDBSCAN Runner-Backed Focused Pod A/B

Status update:

```text
completed: true
result: valid_negative_evidence
material_set_a_candidate: false
report: docs/reports/phoenix_v3_rtdbscan_component_signature_runner_route_m3_1_pod_ab_2026-06-22.md
summary: docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_m3_1_pod_ab_20260622_191459/summary.json
```

Purpose:

Prove or reject the current second Set-A candidate:
`optix_rt_core_grouped_stream_numba_column_signature_3d` routed through
`run_radius_graph_component_signature_3d_prepared_session`.

Entry condition:

- local route contract passes;
- metadata exposes `productized_execution_path: prepared_execution_session_runner`;
- no app-specific native DBSCAN ABI has been added.

Work:

- sync current route code to the RTX 4000 Ada pod;
- run a small sanity case to confirm route metadata;
- run focused same-hardware A/B with repeat/warmup separation;
- verify signatures unchanged;
- write a pod evidence report.

Done when:

- metadata proves the route used the productized runner;
- `runtime_executed_count` and `cache_hit_count` are reported;
- wall/query timing is compared on the same hardware;
- result is classified as material win, neutral, or fail.

Original estimate:

```text
local time: 1-2 hours
pod time: 1-3 hours
pod cost: $0.25-$0.75
risk buffer if Numba/OptiX environment breaks: +2-4 local hours, +1-2 pod hours
```

Stop condition:

If route metadata does not prove productized-runner execution, do not count the
run and do not proceed to all-app.

Actual outcome:

Route metadata proved productized-runner execution, signatures were stable, and
claim flags stayed false. The route still does not count because it lost badly
to the incumbent legacy OptiX grouped-stream path. The next work is a bounded
generic runner-overhead diagnosis or a switch to the next Set-A route.

## Goal 2 — External Review For RTDBSCAN M3.1 Evidence

Purpose:

Get second-AI review on whether the RTDBSCAN focused result can count as Set-A
runner-backed evidence.

Work:

- prepare one bounded review packet;
- call Claude once using the established protocol;
- record verdict and Codex consensus;
- keep release false unless review explicitly supports the evidence.

Done when:

- verdict is recorded;
- non-authorization is explicit;
- if positive, the evidence becomes second focused Set-A candidate evidence;
- if negative, the next route is chosen before more pod spend.

Estimate:

```text
local time: 0.5-1.5 hours
pod time: 0 hours
external review wall time: 0.5-2 hours typical, but quota/auth can delay
```

## Goal 3 — Freeze Set A / Set B Scorecard

Purpose:

Prevent dishonest post-result reclassification.

Work:

- classify benchmark rows before the next all-app run;
- Set A: residency/multi-phase/continuation-rich probes;
- Set B: single-shot/materializing/ceiling controls;
- write one-line rationale per row;
- add a gate that fails if classification is missing.

Done when:

- frozen JSON and Markdown exist;
- tests enforce `classification_frozen_before_run: true`;
- all-app preregistration references this exact classification.

Estimate:

```text
local time: 2-4 hours
pod time: 0 hours
pod cost: $0
```

## Goal 4 — Full Same-Hardware V2.14 vs Phoenix V3 Rerun

Purpose:

Only after two Set-A focused probes exist, run the serious all-app comparison
again using the frozen Set A / Set B scorecard.

Entry condition:

- AABB M2.1 remains accepted as first material Set-A focused evidence;
- RTDBSCAN M3.1 or another route is accepted as second material Set-A focused
  evidence;
- Set A / Set B classification is frozen;
- claim-boundary gates pass.

Work:

- sync code and preregistration to the pod;
- run V2.14 and current Phoenix V3 on same hardware/data;
- analyze both old blended bar and new Set A / Set B scorecard;
- explain every surprising row in user language.

Done when:

- all benchmark apps complete;
- Set A and Set B results are separately reported;
- result maps to one verdict: release candidate, block P1, approve blocked, or
  block P0.

Estimate:

```text
local prep/analyze time: 2-4 hours
pod time: 4-8 hours
pod cost: $1.00-$2.00
```

Stop condition:

If Set A does not show material superiority from the productized path, V3 is
not release-ready. Do not rewrite the result into a marketing claim.

## Goal 5 — One Generic Optimization Loop If Full Rerun Misses

Purpose:

Allow exactly one bounded performance rescue loop if the all-app result is
close but blocked by a generic runtime overhead.

Allowed work:

- runner overhead reduction;
- phase accounting correction;
- prepared-session reuse or cache policy fix;
- generic grouped continuation improvement;
- generic device-residency/materialization reduction.

Rejected work:

- app-specific native engine shortcut;
- special-case route knob that only benefits one benchmark app;
- public wording change without performance evidence.

Done when:

- one generic fix is implemented;
- focused pod evidence shows material improvement on at least one affected
  Set-A route;
- a second all-app rerun is justified or rejected.

Estimate:

```text
local time: 6-16 hours
pod time: 4-12 hours
pod cost: $1.00-$3.00
```

Hard limit:

One optimization loop before asking the user. A second loop requires explicit
approval and a clear hypothesis.

## Goal 6 — Public Docs And Tutorials Final Polish

Purpose:

Make V3 usable and honest for users after the final performance decision.

Work:

- update README, docs map, tutorials, support matrix, performance model;
- keep old V3/V4 material in history/quarantine;
- make current docs the only user path;
- explain V3 vs V2.x in concrete terms;
- document negative or surprising benchmark rows.

Done when:

- public wording gate passes;
- tutorial surface test passes;
- no broad V3-over-V2 claim exists unless the all-app evidence supports it;
- no V4/C ABI/embedding/zero-copy wording leaks into V3.

Estimate:

```text
local time: 4-8 hours
pod time: 0 hours
pod cost: $0
```

## Goal 7 — Final 2-AI Release Or Blocked Consensus

Purpose:

End the Phoenix V3 cycle cleanly: release candidate if evidence earns it, or
blocked handoff if it does not.

Work:

- assemble final packet;
- call Claude with one bounded attempt;
- record Codex consensus;
- update handoff and release gate.

Done when:

- verdict is one of the protocol labels;
- release authorization is explicit if granted;
- non-authorization is explicit if blocked;
- no future AI can accidentally revive old misleading V3/V4 claims.

Estimate:

```text
local time: 1-3 hours
pod time: 0 hours
external review wall time: 0.5-2 hours typical
```

## Decision Tree

```text
Start
  |
  |-- Goal 1 RTDBSCAN focused pod A/B
        |
        |-- material runner-backed win
        |      -> Goal 2 review
        |      -> Goal 3 freeze Set A/B
        |      -> Goal 4 full all-app rerun
        |
        |-- neutral/fail
               -> choose one alternate generic Set-A route
               -> one focused pod A/B
               -> if still fail, stop and handoff
```

After full all-app:

```text
Set A clears bar and Set B parity holds
  -> final docs
  -> 2-AI release review

Set A material but Set B has unexplained regressions
  -> one bounded P1 fix loop

Set A below material bar or wins not from productized path
  -> V3 remains redo_required
  -> write blocked handoff
```

## Pod Budget Recommendation

Minimum budget to keep available:

```text
12 pod hours = about $3
```

Practical budget for controlled Phoenix completion attempt:

```text
24 pod hours = about $6
```

Hard review point:

```text
48 additional pod hours = about $12
```

At 48 additional pod hours, if V3 still lacks two material Set-A
runner-backed probes plus a credible all-app result, stop paying for open-ended
pod time and switch to handoff/replan.

## Goal-Level Decision Audit

Decision: pause further pod execution long enough to produce this resource
plan.

1. Was I foolish?
   No for this decision. It converts the remaining work into bounded goals
   before spending more paid pod time.
2. What actions would have made this foolish?
   Continuing directly into pod runs without stop conditions, or hiding
   uncertainty behind optimistic estimates, would be foolish.
3. Was there another path?
   Yes. I could have kept running the RTDBSCAN pod test immediately, but that
   would leave the user without a resource ceiling.
4. Can I now try a different path that truly solves the problem?
   Yes. Use this plan as the spending and work-control contract: focused pod
   only, explicit review gates, and hard stop if the productized runtime path
   cannot produce material Set-A evidence.
