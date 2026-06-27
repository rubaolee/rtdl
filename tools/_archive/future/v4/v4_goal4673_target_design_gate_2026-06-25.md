# V4 Goal4673 Target Design Gate

Date: 2026-06-25

Status: `goal4673_target_design_gate_complete_pod_not_authorized`

Decision label:

```text
select_aggregate_frontier_device_columns_as_conditional_goal4674_target__pod_not_authorized
```

Machine evidence:

```text
future/v4/evidence/v4_goal4673_target_design_gate_2026-06-25.json
```

## Decision

Goal4673 selects `AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D` as the conditional
Goal4674 target.

This is not a POD authorization and not a V4 release claim. It is the next
target-design gate after the V2.14 primitive audit proved that every promoted
benchmark app already had some primitive or explicit partner route.

## Why This Target

The V2.14 audit changed the target-selection rules. V4 cannot count these as
new performance wins:

- exposing an old V2.14 primitive through a cleaner V4 front door;
- certifying a partner route V2.14 already used;
- comparing against a weak route while ignoring the stronger V2.14 primitive;
- naming an app and hiding an app-specific kernel behind a generic label.

`AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D` is different enough to be worth the next
gate:

- V2.14 had the generic aggregate-frontier collection family, but `git show
  v2.14` did not show the device-column primitive or its prepare/run/destroy
  symbols.
- Current source exposes `AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D` as an
  app-generic contract with device-resident handoff and forbidden host frontier
  rows before partner continuation.
- The target attacks the real bottleneck class: hierarchical frontier rows
  materialized between RTDL traversal and continuation work.
- Barnes-Hut can stress this path as a probe, but the engine target remains the
  generic aggregate-frontier device-column operator.

## Hard Boundary

This does not promote the old aggregate-tree fused weighted-vector sum.

That implementation remains rejected as a V4 public target as-is because it has
force-law/domain risk and records CUDA-driver execution inside the OptiX backend
rather than RT-core traversal evidence. It may inform tests, but it cannot be
renamed into a generic V4 speed surface.

## V2.14 Denominator

V2.14 denominator:

```text
RTDL/OptiX aggregate-frontier membership plus explicit CuPy/Numba force-vector
continuation
```

V2.14 had:

```text
rtdl_optix_collect_aggregate_frontier_2d
```

V2.14 did not show:

```text
rtdl_optix_prepare_aggregate_frontier_device_columns_2d
rtdl_optix_run_aggregate_frontier_device_columns_2d
rtdl_optix_destroy_aggregate_frontier_device_columns_2d
AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D
```

If a later audit finds an equivalent V2.14 device-column route under another
name, this target must be reclassified as same-primitive improvement before any
POD run.

## Goal4674 Pre-POD Gate

Goal4674 must be local/static/protocol work first. It must prove:

- the surface is app-name-free;
- the surface does not wrap the old host-row collector;
- host frontier row materialization before partner continuation is forbidden;
- RT-core wording remains blocked unless the measured path proves OptiX trace;
- correctness parity is frozen for aggregate-frontier rows and downstream
  weighted-vector summaries;
- V2.14, V3.0.2, and V4 denominators are frozen;
- numeric material-speed bars are frozen before any hardware run;
- review request or review debt is recorded.

Only after that may a focused POD benchmark be considered.

Frozen later POD bars, if authorized:

| Metric | Bar |
| --- | ---: |
| V4 aggregate-frontier hot over V2.14 | `>= 1.20x` |
| V4 aggregate-frontier wall over V2.14 | `>= 1.10x` |
| V4 app-probe hot over V2.14 | `>= 1.20x` |
| Correctness parity | required |
| Host frontier materialization in hot path | forbidden |
| Partner migration counts as speed | false |

## Rejected Or Deferred Targets

| Target | Decision | Reason |
| --- | --- | --- |
| `spatial_rayjoin` segment-pair / point-location | Deferred | V2.14 already had segment-pair, directed point-location, and RayJoin CDB point-location symbols, including advanced prepared variants. Useful future work, but not a clean new V4 lever. |
| `contact_manifold` collect-k | Deferred | V2.14 already had bounded collect-k and contact witness routes. Possible same-primitive improvement, not first new lever. |
| `robot_collision` any-hit flags | Rejected as clean win | V2.14 already had prepared any-hit collision flags. |
| `rt_dbscan` grouped union | Rejected | Goal4670/4671 no-go; V2.14 already had the core route. |
| aggregate-tree fused weighted-vector as-is | Rejected | Force-law/app-domain risk plus no RT-core claim basis. |

## Goal-Level Decision Audit

1. Was I being stupid?
   - Yes.
2. If yes, what action made it stupid?
   - The risk was to jump from the V2.14 audit into another convenient app
     target without proving a V2.14-absent runtime lever.
3. Is there another path that avoids getting stuck on a bad premise?
   - Yes. Select a V2.14-absent generic runtime lever, freeze denominators and
     bars, and keep app names as probes only.
4. Can I now try the different path that actually solves the problem?
   - Yes. Goal4674 starts with local static/protocol feasibility for
     `v4_aggregate_frontier_device_columns_2d_prepared_runner`, not a POD run.

## Review State

This is a significant target decision. It needs external review before POD or
release claims.

- Claude: known weekly limit until 2026-06-28 19:00 America/New_York; record
  debt rather than probing repeatedly.
- Antigravity: review request should be sent or debt recorded.
- Codex: self-audit complete, not external consensus.

Implementation may continue only for local static/protocol work until review is
available. No POD performance claim is authorized by this file.

## Non-Authorization

This goal does not authorize V4 release, public speedup wording, whole-app
high-performance wording, a POD run, RT-core speedup wording, true-zero-copy
wording, a Barnes-Hut engine kernel, C ABI, embedding, or promotion of the old
aggregate-tree fused weighted-vector route.
