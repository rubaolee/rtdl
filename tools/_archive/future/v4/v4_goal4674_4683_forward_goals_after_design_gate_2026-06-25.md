# V4 Forward Goals After Goal4673 Target Design Gate

Date: 2026-06-25

Status: proposed forward goal list after Goal4673.

Current decision state:

```text
goal4673_target_design_gate_complete_pod_not_authorized
```

The selected conditional target is:

```text
AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D
```

This list continues the existing project goal numbering. It is not a release
authorization, not a POD authorization, and not a public performance claim.

## Controlling Rule

The next V4 work must prove a new generic runtime lever against the V2.14
denominator. Partner migration, front-door cleanup, and old primitive
repackaging do not count as V4 performance wins.

Progress means:

```text
a named generic V4 route beats the frozen V2.14 denominator at app-relevant
scale, with correctness parity, phase evidence, and no app-identity kernel.
```

## Goal4674 - Aggregate Frontier Device Columns Static/Protocol Gate

Purpose:

- Prove that `AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D` is a valid V4 target before
  any POD run.

Required work:

- Verify the public surface is app-name-free.
- Verify it does not wrap the old host-row aggregate-frontier collector.
- Verify host frontier row materialization before partner continuation is
  forbidden by the route contract.
- Freeze V2.14, V3.0.2, and V4 denominators.
- Freeze correctness parity for aggregate-frontier rows and downstream weighted
  vector summaries.
- Freeze numeric bars before hardware measurement.
- Record review request or review debt.

Exit gate:

- Static/protocol checks pass.
- Machine-readable evidence is written.
- POD remains unauthorized unless this goal explicitly recommends Goal4676.

Kill condition:

- If the target is equivalent to an existing V2.14 device-column route, reclassify
  it as same-primitive improvement. It cannot be a clean new V4 win.

## Goal4675 - Productize the Generic Prepared Runner

Purpose:

- Implement or complete the productized generic runner:

```text
v4_aggregate_frontier_device_columns_2d_prepared_runner
```

Required work:

- Route through generic V4 prepared execution, not an app-mode bypass.
- Keep app probe names out of native/public symbols.
- Add local correctness tests and dry-run fixtures.
- Emit phase/residency telemetry fields required by Goal4674.
- Preserve the hard boundary: do not promote the old aggregate-tree fused
  weighted-vector route as-is.

Exit gate:

- Local tests pass.
- The runner can produce correctness evidence without a hardware performance
  claim.
- Review request or review debt is recorded.

Kill condition:

- If the only implementation path is the old app-domain aggregate-tree fused
  weighted-vector route, stop and redesign. Do not rename an app-specific route
  into a generic operator.

## Goal4676 - Focused POD Benchmark Gate

Purpose:

- Measure whether the new generic route creates a real V4 performance source.

Prerequisite:

- Goal4674 and Goal4675 complete.

Frozen bars:

| Metric | Bar |
| --- | ---: |
| V4 aggregate-frontier hot over V2.14 | >= 1.20x |
| V4 aggregate-frontier wall over V2.14 | >= 1.10x |
| V4 app-probe hot over V2.14 | >= 1.20x |
| Correctness parity | required |
| Host frontier materialization in hot path | forbidden |
| Partner migration counts as speed | false |

Required work:

- Run V2.14, V3.0.2, and V4 on the same POD/hardware.
- Use serious app-relevant scales, not toy fixtures.
- Record phase timings, residency, correctness parity, and denominator labels.
- Preserve raw outputs under `future/v4/evidence`.

Exit gate:

- Pass: route qualifies as a second independent true V4 performance candidate.
- Fail: record no-go/reframe; do not continue toward app-level high-performance
  release on this target.

## Goal4677 - Candidate Promotion or No-Go Decision

Purpose:

- Decide what Goal4676 means.

Required work:

- Classify the result as one of:
  - true V4 generic-runtime win;
  - same-primitive material improvement;
  - partner migration;
  - algorithmic-complexity baseline win;
  - parity/regression.
- Update route-binding tables only if the classification supports it.
- Preserve non-authorization if the result is not a true V4 app-level win.

Exit gate:

- A written decision exists with machine evidence and review request/debt.

Kill condition:

- If the result is parity/regression, stop chasing this target and pivot. Do not
  lower the bar after seeing the result.

## Goal4678 - Select the Next Independent Generic Lever

Purpose:

- Avoid depending on one app row. Choose a third independent V4 lever only if
  Goal4676/4677 produces a real candidate.

Required work:

- Use the V2.14 primitive audit as the denominator.
- Reject targets that are only front-door cleanup or partner certification.
- Prefer a relation/topology or contact/witness primitive if it has a real
  V2.14-absent lever.
- Freeze bars before any hardware run.

Exit gate:

- A selected target or an explicit no-clean-target finding.

Kill condition:

- If no clean independent target exists, move to release reframe instead of
  manufacturing a weak target.

## Goal4679 - Implement and Measure Third Lever, If Selected

Purpose:

- Prove whether V4 has more than one/two isolated wins.

Prerequisite:

- Goal4678 selects a clean target.

Required work:

- Repeat the Goal4674-4677 discipline for the selected lever.
- No app-identity native kernels.
- No partner migration counted as speed.

Exit gate:

- Third independent candidate win, or explicit no-go.

## Goal4680 - Full App-Level V2.14/V3/V4 Benchmark Rerun

Purpose:

- Produce the serious all-benchmark answer users need.

Prerequisite:

- At least two independent true V4 candidate app rows exist, or the goal is
  explicitly framed as a reframe/negative evidence run.

Required work:

- Run all promoted benchmark apps on the same hardware.
- Use frozen datasets, repeats, warmups, correctness checks, and denominator
  labels.
- Keep V2.14, V3.0.2, and current V4 side by side.
- Store raw outputs and summary JSON/Markdown.

Exit gate:

- Complete app-level scorecard with clear row classification.

## Goal4681 - V4 Release Classification

Purpose:

- Decide whether the evidence supports formal high-performance V4, bounded
  operator V4, or no release.

Required work:

- Separate true V4 wins from partner migration, same-primitive improvements,
  algorithmic-complexity wins, parity, and regressions.
- Explain why V4 exists relative to V2.14 using evidence, not slogans.
- Keep public wording bounded to the evidence.

Exit gate:

- One of:
  - `formal_high_performance_v4_supported`;
  - `bounded_operator_v4_only`;
  - `v4_release_not_supported_reframe_required`.

## Goal4682 - Public Docs and User Surface Cleanup

Purpose:

- Make the user-facing V4 surface honest and usable.

Prerequisite:

- Goal4681 classification complete.

Required work:

- Update front page, docs, examples, tutorials, and benchmark pages to match the
  classification.
- Hide or move stale historical V3/V4 work out of the user path.
- Ensure all visible examples run.
- Remove broad speed wording if not authorized.

Exit gate:

- Clean user surface and reproducible examples.

## Goal4683 - Final External Review and Release/No-Release Decision

Purpose:

- Get final independent authorization or rejection.

Required work:

- Send Goal4680-4682 evidence to external reviewers.
- Claude review may be recorded as debt while weekly-limited, but final public
  release must not pretend blocked debt is authorization.
- Antigravity may be used as an available external reviewer.
- Record the final decision and non-authorization boundaries.

Exit gate:

- Release tag if authorized, or explicit no-release/reframe record if not.

## Non-Authorization

This file does not authorize V4 release, public speedup wording, whole-app
high-performance wording, POD spend, RT-core speedup wording, true-zero-copy
wording, a Barnes-Hut/DBSCAN/RayJoin app kernel, C ABI, embedding, non-Python
hosts, or arbitrary callback claims.
