# Phoenix V3 Next Goals After Goal0 / Claude Verdict

Date: 2026-06-24
Status: planning only; do not execute from this document alone
Scope: V3 runtime / language performance work only

## Current Locked Fact

Barnes-Hut Goal0 produced a real but limited result:

- `runtime_executed: true`
- `runtime_trunk_executes_end_to_end: true`
- `internal_device_residency_between_rtdl_phases: true`
- `hot_path_host_materialization: false`
- `correctness_parity: true` on focused evidence
- projected performance improved from the old `0.844x` row to about `0.9526x`
- it still fails parity `0.98x`, V2 parity `1.00x`, and Set-A `1.20x`

Claude's verdict is accepted as the controlling interpretation:

```text
goal0_trunk_proven__barnes_hut_backend_bound__reclassify_and_reselect
```

Meaning:

- Barnes-Hut proves the V3 trunk can execute with residency and parity.
- Barnes-Hut is not a performance proof.
- Barnes-Hut must not receive more tuning.
- Barnes-Hut can become a future control row only after `phase_seconds` confirms backend-boundedness.
- V3's performance premise remains open and must be tested on one explicitly chosen, winnable family.

## Non-Negotiable Rules

1. No V4, no embedding, no C ABI, no external zero-copy claims.
2. No all-app run until the focused gates below pass.
3. No public or broad "V3 beats V2" wording before release review.
4. No app-special optimization may count as V3 progress.
5. Every performance claim must include correctness parity.
6. Every runtime win must include `win_source`, `phase_seconds`, `runtime_executed`, and `hot_path_host_materialization`.
7. No third search for a winner: if the reselected best family misses its bar, V3 reframes to capability/quality release.

## Goal 1 -- Confirm Barnes-Hut Backend-Bound Status, Without Tuning

Purpose: close the integrity precondition for reclassifying Barnes-Hut as a control row.

Tasks:

- Read existing Barnes-Hut focused evidence.
- If needed, run only the minimum telemetry probe to expose `phase_seconds`; do not tune.
- Show that dominant wall time is in the shared RT traversal / force kernel, not in trunk-removable phases.
- Record Barnes-Hut as `trunk_proven`, `backend_bound_pending_or_confirmed`, and `further_tuning_forbidden`.

Exit gate:

- Pass: `phase_seconds` confirms backend-bound status; Barnes-Hut becomes a future control row.
- Fail: if a large trunk-removable phase remains, Barnes-Hut stays an unfinished Set-A probe and the next goal becomes fixing that missing trunk work, not selecting a new family.

## Goal 2 -- Select One Winnable Performance Family Under The Anti-Avoidance Lock

Purpose: choose the real V3 performance test before writing code.

For each candidate, record:

```text
(a) family name
(b) current scorecard ratio / blocker row
(c) dominant end-to-end phase by measured wall-time fraction
(d) concrete runtime hypothesis for >=1.20x
(e) why V2.14 lacks that mechanism
(f) expected win_source
(g) parity oracle
```

Selection rule:

- Pick exactly one candidate with a measured dominant phase and a credible `>=1.20x` runtime-sourced hypothesis.
- Do not pick a family just because it is easy to wire.
- Do not pick a family whose expected win is another Barnes-Hut-style regression recovery.

Exit gate:

- Pass: one candidate is selected and falsifiable.
- Fail: no candidate can satisfy the lock; V3 immediately reframes to capability/quality release.

## Goal 3 -- Freeze The Focused Experiment Protocol For The Selected Family

Purpose: prevent metric gaming before the run.

Freeze:

- exact app / scorecard row
- V2.14 baseline route
- V3 route
- dataset scale
- hardware
- correctness oracle and tolerance
- timing metric
- Set-A bar: `>=1.20x` runtime-sourced with parity
- fail condition: below bar, parity fail, host materialization in hot path, or missing telemetry

Exit gate:

- A written protocol exists before implementation and cannot be edited after the run except to record results.

## Goal 4 -- Implement The Selected Family Through The Generic V3 Trunk

Purpose: make the V3 runtime, not the app, do the work.

Allowed:

- prepared-session runner integration
- device-resident phase handoff
- generic continuation node
- shared runtime primitive usable by more than one benchmark family
- fail-closed telemetry and parity checks

Forbidden:

- app-only native route
- hidden host materialization
- one-off benchmark patch
- changing the benchmark to match the implementation

Exit gate:

- Local tests prove the route is wired through the trunk.
- Focused smoke proves correctness parity.
- Telemetry reports all required fields.

## Goal 5 -- Run The One Focused POD Experiment For The Selected Family

Purpose: decide whether V3 has a real performance source.

Output:

- JSON evidence
- summary report
- `phase_seconds`
- `win_source`
- `runtime_executed`
- `hot_path_host_materialization`
- `parity_pass`
- V3/V2 ratio against the frozen row

Exit gate:

- Pass: `>=1.20x`, runtime-sourced, parity true, no hot-path host materialization.
- Fail: V3 reframes to capability/quality release; no third search for a more convenient winner.

## Goal 6 -- Prove Limited Generalization With One More Preselected Family

Purpose: show the first pass was not a single-family trick.

Precondition:

- Goal 5 passed.

Tasks:

- Select one additional family using the same anti-avoidance lock.
- Prefer a different dominant phase or different `win_source`.
- Reuse the same runner / continuation / residency mechanisms where possible.
- Do not create a new app-special route.

Exit gate:

- Pass: second family moves its scorecard row with parity and runtime-sourced evidence.
- Fail: V3 may still have a narrow capability, but not a broad high-performance release; move to capability/quality framing unless external review explicitly approves a narrower claim.

## Goal 7 -- Promote Residency, Phase Accounting, And Continuation Into Core Runtime Defaults

Purpose: make the trunk a product surface, not a demo path.

Tasks:

- Required telemetry for every prepared runner path.
- `runtime_executed` must fail closed if the runner is bypassed.
- `hot_path_host_materialization` must be measured, not asserted.
- continuation nodes such as grouped reduction / component union / ranked summary must be callable from the runner, not buried in app modes.

Exit gate:

- Any routed family missing required telemetry fails tests.
- At least two families use the same trunk-level mechanism.

## Goal 8 -- Route Remaining Set-A Families Only Through Proven Generic Mechanisms

Purpose: complete the V3 performance surface without becoming app developers.

Tasks:

- Apply only already-proven generic trunk mechanisms.
- For every remaining Set-A row, classify honestly:
  - runtime-sourced win
  - parity/control row
  - backend-bound
  - failed / capability-only
- No new route may be justified solely by one app.

Exit gate:

- All Set-A rows are either moved by runtime-sourced mechanisms or explicitly classified with evidence.
- All severe regressions have an explanation or a fix path.

## Goal 9 -- Focused Scorecard Re-Read, Not All-App

Purpose: decide whether all-app is justified.

Tasks:

- Re-read only rows touched by the V3 trunk work.
- Compute Set-A performance row result and Set-B/control parity result separately.
- Preserve Barnes-Hut as a control row only if Goal 1 confirmed backend-bound status.

Exit gate:

- Go: enough runtime-sourced rows clear the frozen bar and controls are explainable.
- No-Go: V3 becomes capability/quality release; no all-app spend.

## Goal 10 -- Serious All-App POD Run

Purpose: final evidence, not exploration.

Precondition:

- Goal 9 Go.

Tasks:

- Run all benchmark apps on the same RT hardware.
- Compare V2.14 vs Phoenix V3 under the frozen scorecard.
- Publish both the performance score and control/parity score.
- Explain every surprising row in user language.

Exit gate:

- Evidence package is complete enough for external audit.

## Goal 11 -- External 3-AI Release Review

Purpose: decide release truth.

Review packet must include:

- code diff summary
- POD evidence
- scorecard movement
- correctness parity results
- win_source distribution
- backend-bound/control classifications
- claim boundaries
- all-app results if authorized and run

Verdicts:

- high-performance V3 release
- capability/quality V3 release
- blocked / redo required
- reject

## Goal 12 -- User-Facing V3 Productization Only After Release Truth Is Known

Purpose: avoid repeating the old mistake of polishing a claim before it is true.

Tasks:

- docs and tutorials reflect the verified release truth
- examples teach the real V3 surface
- old/conflicting material goes to history
- no V4 wording leaks into V3
- installation and quickstart are tested

Exit gate:

- Users see one coherent V3, not a sea of old plans and failed claims.

## Parallel Hygiene Goal -- Repository Truth

This can run in parallel only when it does not delay Goals 1-5.

Tasks:

- collect uncommitted Phoenix V3 work into reviewable commits
- retire or fence the old committed `V4.0.0 promoted` front-door state
- ensure repository history reflects the 2026-06-20 decision: V3 first, V4 out of scope

This is necessary hygiene, but it does not count as performance progress.

## Goal-Level Decision Audit

Decision: accept Claude's Goal0 verdict and reselect one winnable family instead of continuing Barnes-Hut.

1. Was the prior direction foolish? Partly yes: continuing Barnes-Hut from `0.9526x` toward `0.98x` would be trivial tuning and would not prove V3.
2. What actions made it foolish? Treating a near-parity recovery as a possible performance route after the evidence showed Barnes-Hut was backend-bound.
3. Was there another path? Yes: stop Barnes-Hut, write the anti-avoidance lock, and choose a family whose dominant measured phase can actually be moved by the V3 trunk.
4. Can we try a different path that solves the problem? Yes: Goals 2-5 force exactly one decisive performance experiment; if it fails, V3 honestly becomes a capability/quality release instead of wasting more time.
