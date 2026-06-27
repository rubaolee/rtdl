# V4 Goal4734 RTDBSCAN Generic Continuation No-Go

Date: 2026-06-26

Status: `closed_no_go_pending_external_review_debt`

Decision:
`rt_dbscan_goal4734_closed_by_existing_grouped_union_no_go__pivot_to_goal4735`

## Purpose

Goal4731 listed Goal4734 as:

`rt_dbscan generic continuation improvement attempt`

The intended exit was either:

- a material generic continuation improvement that lifts RTDBSCAN to the formal
  app-level bar; or
- a no-go without app-identity kernels, partner-migration credit, or bar
  lowering.

## Controlling Evidence

Goal4734 is closed by existing focused evidence rather than by another POD run.
The reason is important: the same generic continuation lever was already tested
in Goal4670 and Goal4671.

Relevant records:

- `future/v4/v4_goal4670_rt_dbscan_second_win_diagnostics_2026-06-25.md`
- `future/v4/v4_goal4671_rtdbscan_native_grouped_union_feasibility_2026-06-25.md`
- `future/v4/evidence/v4_goal4671_rtdbscan_grouped_union_telemetry_20260625/summary.json`

Goal4670 found:

| RTDBSCAN variant | class | V4/V2.14 hot | V4/V3.0.2 hot | decision |
|---|---|---:|---:|---|
| default grouped-stream Numba signature | true V4 runtime candidate | about 1.08x | about 1.08x | below formal bar |
| direct side-effect probe | generic native toggle probe | about 1.12x | about 1.11x | below formal bar |
| direct side-effect plus no same-root culling | best generic grouped-union probe | about 1.166x | about 1.163x | still below 1.20x |

Goal4671 then inspected grouped-union telemetry and concluded that the remaining
gap was not a safe generic root-finding tweak:

- candidate hits remain enormous;
- root-link depth is already about one link per root find in the best variant;
- same-root culling is not a reliable win on this all-core fixture;
- repeating RTDBSCAN micro-probes would be churn.

## Decision

Do not spend another Goal4734 POD cycle on RTDBSCAN unless a new generic
grouped-union algorithm changes the candidate/root-find count structure.

Goal4734 is therefore closed as:

`no_second_true_v4_win_from_current_rt_dbscan_grouped_union_trunk`

This keeps RTDBSCAN as a bounded modest-gain route, not formal high-performance
V4 evidence.

## Why This Is Not Avoidance

This is not skipping a hard experiment. The hard experiment was already run:
Goal4670 measured the app-level variants and Goal4671 measured the native
grouped-union structure. The current action prevents the exact failure pattern
the user warned against: repeatedly probing a route already classified as no-go
just to look busy.

## Reopen Condition

RTDBSCAN may be reopened only if one of the following exists before the run:

1. a new generic grouped-union algorithm that plausibly reduces candidate/root
   work, not just Python-side signature materialization;
2. a new app-level contract that is generic and not an app-identity DBSCAN
   kernel;
3. a frozen V2.14/V3 denominator and a predeclared bar showing how the new
   generic lever could reach `>=1.20x`.

Direct-status routes remain external-proof/historical routes and must not be
counted as true V4 wins.

## Next Action

Proceed to Goal4735:

`choose one no-route/deferred app for fresh generic operator`

The correct target should have:

- a frozen denominator;
- correctness parity;
- a material-speed hypothesis before implementation;
- no app-identity native kernel;
- no hidden V2/V3 fallback;
- no release wording before measurement.

## Claim Boundary

Goal4734 supports this bounded statement:

RTDBSCAN remains a complete V4 app route with modest measured speedup, but the
current generic grouped-union trunk has already been tested and is not a
credible second true high-performance V4 app win.

Goal4734 does not authorize:

- final V4 tag;
- public all-benchmark speedup claim;
- RTDBSCAN high-performance claim;
- direct-status rows as V4 wins;
- app-specific DBSCAN native kernels;
- automatic partner selection;
- true-zero-copy wording.

## Goal-Level Decision Audit

1. Was I being foolish?
   No. Repeating Goal4670/4671 would be foolish; closing RTDBSCAN based on the
   existing no-go evidence is the disciplined path.

2. If yes, what action made the decision foolish?
   The foolish action would be spending another POD run on the same grouped-union
   lever without a new generic algorithm or frozen hypothesis.

3. Was there another path?
   Yes: ignore Goal4671 and try to polish RTDBSCAN toward 1.20x. That would be
   exactly the process-churn failure mode already diagnosed.

4. Can I now try a different path that actually solves the problem?
   Yes. Move to Goal4735 and select a fresh generic operator/app target where a
   real material-speed hypothesis exists before implementation.

## Non-Authorization

Goal4734 authorizes no final V4 tag, no public speed claim, no all-benchmark
speedup claim, no app-specific native kernel, no arbitrary callback support, and
no true-zero-copy wording.
