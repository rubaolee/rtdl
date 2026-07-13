# Goal4912 — Persistent Planar-Map Workspace Design Gate

Date: 2026-07-03

## Requested Verdict

`approve_goal4912_productize_in_process_workspace_api__do_not_pursue_cross_process_gas_cache_now`

## Why This Goal Exists

Goal4911 closed the simple knob-tuning path. The current default point-location
range construction is already the best measured tradeoff among tested modes.
The remaining setup cost is not an obvious bad default; it is the cost of
building reusable native locator state.

The next step must therefore be a product/API decision, not another timing
knob:

```text
Should RTDL expose a generic persistent planar-map workspace/session API
that lets users pay CDB load/pack, LSI prepare, and point-location prepare
once, then run repeated Section-5.7-style query bodies cheaply?
```

My decision for this goal is:

```text
Yes: productize an in-process PlanarMapWorkspace/session API.
No: do not pursue cross-process OptiX GAS serialization/cache now.
```

## Evidence From Prior Goals

### Current Best Prepared-Hot Result

Goal4910 best prepared-hot repeat:

| Metric | Value |
|---|---:|
| hot body | `3.918s` |
| writer | `1.840s` |
| LSI replay | `0.006s` |
| vertex PIP map0 in map1 | `1.080s` |
| byte equal to AuthorOfficial | `true` |

This is the best current RTDL+Numba+Python app-layer route for the Australia
representative Section 5.7 workload.

### Existing Session Reuse Already Works

Goal4902 proved that prepared point-location base sessions can be reused:

```text
prepare planar-map point-location base sessions once
→ run repeated point-location queries / overlay bodies
→ destroy sessions when the application is done
```

Measured effect:

| Route | Hot body |
|---|---:|
| Prepare point-location inside each run | `11.320s` |
| Reuse prepared point-location sessions | `6.915s` |

This is a real generic RTDL pattern. It is not a single-run speedup claim.

### Prepared LSI Replay Also Works

Goal4904 proved that prepared LSI query replay is valuable:

| Route | LSI phase |
|---|---:|
| public pair-id rows without prepared query replay | `1.814s` |
| prepared LSI query replay | `0.006s` |

This shows that the right abstraction is not a RayJoin shortcut. It is a
reusable prepared workspace around public planar-map primitives.

### Simple Point-Location Knob Tuning Is Exhausted

Goal4911 measured point-location prepare/run tradeoffs:

| Mode | map0 prepare/run | map1 prepare/run | Correct hash? |
|---|---:|---:|---|
| default repeat | `0.260s / 1.157s` | `4.043s / 0.038s` | yes |
| legacy fixed8 | `0.213s / 10.915s` | `3.374s / 1.587s` | yes |
| adaptive ms8 e1.5 | `0.252s / 1.142s` | `4.073s / 0.040s` | yes |
| block_merge64 i0 e1.5 | `0.261s / 1.137s` | `4.325s / 0.036s` | yes |

Conclusion: keep the current default. Do not run more mode sweeps unless new
evidence explains a new failure mode.

## Product Design: Public In-Process Workspace

The next product feature should be a generic public API shaped like this:

```python
with rtdsl.prepare_planar_map_workspace_2d_optix(
    left_cdb,
    right_cdb,
    cache_dir=packed_cache_dir,
    lsi=True,
    point_location=True,
) as workspace:
    result = workspace.overlay_query(
        continuation=app_continuation,
        output_writer=app_writer,
    )
```

or lower-level:

```python
with rtdsl.prepare_planar_map_workspace_2d_optix(left_cdb, right_cdb, cache_dir=cache) as ws:
    with ws.prepare_lsi_query() as lsi_query:
        pair_rows = lsi_query.run_pair_id_rows()

    faces0 = ws.point_location_right.run(left_points)
    faces1 = ws.point_location_left.run(right_points)
```

The user-visible contract:

- load/pack CDB inputs once;
- prepare public planar-map LSI base/query handles once when reused;
- prepare public directed planar-map point-location handles once;
- expose explicit `close()` / context-manager lifetime;
- make hot/cold timing separation first-class;
- keep app logic outside RTDL core;
- allow Numba/CuPy/Python continuations to consume rows/faces;
- do not import or depend on `rtdsl.rayjoin_overlay`;
- do not expose raw OptiX callbacks.

## Why Not Cross-Process OptiX GAS Serialization Now

I am explicitly not choosing cross-process OptiX GAS/build-artifact caching for
this goal.

Reasons:

- The current measured win already comes from in-process reuse.
- Cross-process acceleration-structure persistence is backend-specific and may
depend on CUDA/OptiX version, driver, device, and allocator details.
- A failed or fragile GAS cache would become a large product-maintenance burden.
- It would not change the hot replay body; it only attacks cold setup.
- It is unnecessary before we productize the simpler, already-proven in-process
workspace route.

This can be revisited later as a separate backend-specific R&D goal, after the
public workspace lifecycle exists.

## Implementation Scope If Approved

The implementation goal following this design should add:

1. `PlanarMapWorkspace2DOptix`
   - public Python class;
   - context manager;
   - owns packed CDB inputs;
   - owns prepared LSI base/query handles when requested;
   - owns prepared point-location handles for both directions;
   - exposes phase timings and close semantics.

2. Public constructor:
   - `prepare_planar_map_workspace_2d_optix(...)`.

3. Tests:
   - workspace close/idempotence test;
   - repeated-query byte equality on a small synthetic CDB-like fixture;
   - no `rtdsl.rayjoin_overlay` import;
   - timing metadata includes setup vs hot replay;
   - workspace can run at least one LSI query and one point-location query.

4. RayJoin paper-reproduction harness update:
   - use the workspace instead of manually preparing individual handles;
   - preserve AuthorOfficial byte equality;
   - report cold setup and hot replay separately.

5. Documentation:
   - internal only until reviewed;
   - no public benchmark claim until correctness and a clean user-facing surface
     are separately approved.

## Acceptance Bar For The Implementation Goal

The follow-up implementation should pass:

| Gate | Required |
|---|---|
| correctness | byte-equal to AuthorOfficial on Australia representative |
| public boundary | no `rtdsl.rayjoin_overlay` import |
| generality | API names are planar-map/workspace names, not RayJoin names |
| lifecycle | repeated hot queries reuse the same prepared handles |
| timing | setup and hot replay reported separately |
| hot body regression | hot body no worse than Goal4910 by more than 5% |
| docs | no broad speedup claim |

This bar intentionally does not require a new speedup. The first purpose is
productizing the already-proven prepared-session route into a coherent user API.
Any speedup beyond Goal4910 is secondary.

## What This Does Not Authorize

This goal does not authorize:

- raw OptiX callback exposure;
- RayJoin-specific hidden kernels;
- cross-process OptiX GAS serialization;
- rewriting the overlay algorithm;
- broad RTDL/RayJoin performance claims;
- public release wording changes;
- resurrection of V3/V4 claims.

## Expected Outcome

If approved, Goal4913 should implement the in-process workspace API. The expected
result is not a magic new hot-path win. The expected result is:

```text
RTDL has a clean, generic, user-facing way to express the performance pattern
that the experiments already proved:

prepare public planar-map primitives once, replay hot query bodies many times,
and keep Python/Numba app continuation outside the RTDL core.
```

That is a real product improvement because it turns the current hand-built
experimental harness into a coherent RTDL programming model.

## Goal-Level Decision Audit

1. **Am I being stupid?**

   Not if I keep this as a design gate. It would be stupid to keep tweaking
   writer Python or group-mode knobs after Goal4908, Goal4910, and Goal4911.

2. **What action would make this stupid?**

   Implementing cross-process native cache machinery before productizing the
   simpler in-process workspace pattern that already has evidence.

3. **Was there another possible path?**

   Yes: stop optimization and consolidate. That is legitimate, but the user has
   asked us to continue improving the language/product. The workspace route is
   the lowest-risk product improvement left.

4. **Can I start a different path that truly solves the problem?**

   Yes. Goal4913 should implement the generic workspace API if this design is
   approved. If reviewers reject it as just packaging, then the honest next path
   is to stop this performance line and document the current best bounded result.
