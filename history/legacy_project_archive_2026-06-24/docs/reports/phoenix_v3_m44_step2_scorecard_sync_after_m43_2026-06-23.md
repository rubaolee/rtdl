# Phoenix V3 M44 Step-2 Scorecard Sync After M43

Date: 2026-06-23

Status: `m44_scorecard_synced_pending_external_review_not_release`

This report synchronizes the Phoenix V3 Step-2 evidence state after M43. It is
not a release authorization, not an all-app authorization, not paid-POD
authorization, not public speedup wording, not a broad V3-over-V2 claim, not V4,
not embedding, not C ABI, and not true-zero-copy evidence.

## Bottom Line

M43 changes the current engineering state: grouped reduction is no longer merely
contract-positive/performance-blocked. The original blocked `262144 x 1024`
shape now has accepted bounded Step-2 technical closure through a productized
CuPy prepared-session runner and user-provided Antigravity external review.

However, this still does not authorize a full all-app run. The controlling
release scorecard remains the frozen Set-A/Set-B all-app gate, and that gate
still blocks release and broad POD spend until the runtime-trunk evidence is
connected to the all-app blockers.

## Frozen All-App Scorecard Still Controls Release

The current frozen all-app gate remains:

```text
docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md
```

Key frozen values:

| Metric | Value |
| --- | ---: |
| Set A geomean | `1.013x` |
| Set B geomean | `1.007x` |
| Set A apps over `1.05x` | `1 / 5 required` |
| Set A severe regressions below `0.90x` | `1` |
| Set B rows below `0.95x` | `1` |
| Release candidate under two-number bar | `false` |
| All-app POD spend authorized | `false` |

The main visible all-app blockers remain:

- `barnes_hut`: Set-A app geomean `0.844x`
- `librts_spatial_index`: Set-B app geomean `0.937x`
- `librts_spatial_index` Embree AABB row below `0.95x`
- Set-A app-win shortfall: only `1` Set-A app over `1.05x`

## Current Step-2 Runtime-Trunk Ledger

| Family | Evidence class | External status | Runtime-trunk facts | Performance read | M44 classification |
| --- | --- | --- | --- | --- | --- |
| Component union / fixed-radius component labels | Focused paid POD, same generated point set, RT hardware gate | Codex+Claude consensus accepted M40 with caveats | `runtime_trunk_executes_end_to_end=true`, internal residency `true`, hot-path host materialization `false`, component-label output contract preserved | runner vs Embree hot `1.221027x`; runner vs Embree wall `2.421405x`; runner vs legacy wall `1.254316x`; runner vs legacy hot about `0.994x` | Positive Step-1/Step-2 family evidence, but not hot-kernel superiority over legacy |
| Grouped reduction / grouped vector sum | Free local lx1 CUDA evidence, original blocked shape fixed | Codex+Antigravity consensus accepted M43; Claude review debt remains open | `runtime_trunk_executes_end_to_end=true`, internal residency `true`, hot-path host materialization `false`, explicit partner `cupy`, `warp_per_group_tiled` | original shape runner vs CPU hot `3.454249x`, runner vs legacy hot `6.670790x`; trusted offsets runner vs CPU hot `3.634393x`, runner vs legacy hot `3.316330x`, runner vs legacy wall `15.409128x` | Second current Step-2 family closed for bounded technical purposes; not all-app, not paid-POD, not release evidence |
| M42 grouped-reduction shape diagnostic | Free local lx1 shape experiment | Codex+Claude accepted root cause and required tiled kernel | Proved old Numba path parallelized over `group_count`; `262144 x 1024` launched only `4` blocks | `262144 x 65536` runner vs CPU hot `6.443936x` | Supporting diagnostic, not an independent family |

## What M43 Changes

Before M43, grouped reduction was:

```text
contract-positive, performance-blocked, paid POD blocked
```

After M43, grouped reduction is:

```text
bounded Step-2 technical closure accepted by external review, local/free evidence only
```

This matters because it proves the trunk can carry a second generic continuation
family through the same prepared-session discipline. It does not prove full V3
release performance.

## What M43 Does Not Change

M43 does not change:

- the frozen all-app Set-A/Set-B scorecard
- the all-app `1.012x`/`1.013x` near-parity failure pattern
- the Barnes-Hut severe regression blocker
- the Set-B LibRTS parity blocker
- the requirement for an explicit all-app authorization packet before any broad
  POD run
- the open Claude review debt for M43

## Codex Recommendation For Next Work

M44 recommendation, pending external review:

```text
Do not run all-app yet.
Do not spend paid POD yet.
Move next to M45: Barnes-Hut severe-regression root-cause audit, but only as
generic runtime-trunk work around prepared graph / aggregate-tree / fused
continuation behavior.
```

Reason:

- The all-app gate is still blocked chiefly by a Set-A severe regression:
  `barnes_hut = 0.844x`.
- Adding more small positive probes without addressing the controlling all-app
  blocker risks repeating the old mistake: attractive local wins that do not
  move V3 as a language/runtime.
- Barnes-Hut should not be treated as app development. It is a stress test for
  generic V3 mechanisms: prepared graph/chunk execution, aggregate-tree
  reuse, fused vector-sum continuation, phase accounting, and internal
  residency.

M45 should start locally by answering:

1. Which Barnes-Hut row(s) make the frozen Set-A app geomean `0.844x`?
2. Is the regression from runtime overhead, prepared graph construction,
   frontier/chunk scheduling, continuation/reduction, backend dispatch, or
   baseline mismatch?
3. Which reusable runtime primitive would fix the root cause for more than
   Barnes-Hut?
4. Is there already focused evidence claiming Barnes-Hut is covered, and if so,
   why did the frozen all-app scorecard still show a severe regression?

M45 must not start with a POD run. It should start with file/evidence audit,
source inspection, and local tests.

## Review Debt

Claude review debt remains open:

```text
docs/reviews/phoenix_v3_claude_review_debt_register_2026-06-23.md
```

Claude must later confirm, amend, or reject the Antigravity M43 verdict before
any goal-completion audit or larger authorization.

## Non-Authorization

This report does not authorize:

- V3 release
- all-app benchmark run
- paid POD spend
- public speedup wording
- broad V3-over-V2 claim
- V4 work
- embedding
- C ABI
- true zero-copy claim

## Goal-Level Decision Audit

Decision: treat M43 as a bounded Step-2 grouped-reduction technical closure, but
keep all-app/POD/release blocked and recommend M45 Barnes-Hut severe-regression
root-cause audit as the next local runtime-trunk task.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? The foolish action would be
   to treat the strong M43 local result as automatic permission to run all-app,
   or to keep collecting unrelated positive probes while ignoring the frozen
   Barnes-Hut severe regression.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Immediately run all-app or pick another easy family. Both are rejected
   here because they spend time before addressing the controlling release
   blocker.
4. Can I now try a different path that actually solves the problem? Yes. M45
   should audit Barnes-Hut as a generic prepared-graph / fused-continuation
   runtime problem, not as app-specific tuning, and only then decide whether a
   focused POD run is justified.
