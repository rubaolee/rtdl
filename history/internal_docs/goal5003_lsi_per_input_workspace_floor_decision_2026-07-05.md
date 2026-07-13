# Goal5003 Result: LSI Per-Input Workspace Floor Decision

Date: 2026-07-05

## Verdict

```text
accept_current_fresh_lsi_workspace_floor_for_v2_14_3__future_generic_domain_workspace_needed
```

Goal5003 shows that the remaining LSI cost after Goal5002 is not another
global compile cost. It is tied to the prepared base/query workspace and,
more specifically, to the planar-map LSI scale domain.

For v2.14.3, this means the fresh one-shot top4 route must keep the LSI
workspace cost in its headline. A future version can attack it with a generic
domain/workspace API, but v2.14.3 should not hide it behind prewarm language.

## Why This Goal Exists

Goal5002 removed the global compile / pipeline cost from the top4 LSI phase
with a tiny generic LSI prewarm:

```text
exact_pipeline_ensure + split_kernel_ensure:
  ~0.989s -> ~0.000001s
```

The remaining target was:

```text
grouped_range_ensure + scaled_cache_ensure ~= 1.7s
```

Goal5003 asks whether that remaining cost is reducible in v2.14.3 by another
generic prewarm/reuse mechanism, or whether it is a true fresh-input workspace
floor.

## Source Audit

The relevant native code is in:

```text
src/native/optix/rtdl_optix_workloads.cpp
```

`ensure_rayjoin_lsi_scaled_segment_caches(...)`:

- computes a scale from the combined right/base and left/query coordinate
  domain;
- scales right and left segments into the exact planar-map LSI representation;
- uploads scaled segment caches;
- resets grouped-range acceleration when the right scaled cache changes.

`ensure_segment_pair_grouped_ranges(...)`:

- groups right-side scaled segments into ranges;
- uploads group ranges;
- builds an OptiX acceleration structure over those grouped AABBs.

The public Python API already exposes an explicit generic prepared-query
workspace hook:

```text
src/rtdsl/optix_runtime.py
PreparedOptixPlanarMapLsi2DQuery.prepare_workspace()
```

That method already states the correct contract:

```text
workspace_depends_on_base_and_query: true
workspace_reuse_contract: subsequent run_pair_id_rows/count calls on this prepared query may reuse native caches
```

So the missing piece is not a hidden RayJoin helper. The key question is what
can be reused across which product regime.

## POD Probe

Internal probe:

```text
history/internal_docs/goal5003_lsi_workspace_floor_probe.py
```

Artifact:

```text
history/internal_docs/goal5003_lsi_workspace_floor_artifacts_2026-07-05/lsi_workspace_floor_probe_top4.json
```

POD:

```text
root@157.157.221.29 -p 25248
repo: /root/rtdl_goal4988
```

Input:

```text
top4 County x Zipcode
left_lsi_segments: 1705027
right_lsi_segments: 9982960
capacity: 1000000
```

The probe first runs the tiny generic LSI prewarm from Goal5002, so the global
compile / pipeline costs are already removed. It then measures workspace reuse
under one prepared right/base handle.

## Measurement Matrix

| Case | Meaning | Rows | Elapsed sec | scaled cache ensure | grouped range ensure | OptiX launch |
|---|---|---:|---:|---:|---:|---:|
| `full_first_run_build_workspace` | first full query after generic compile prewarm | 428322 | 1.711297 | 0.706036 | 1.001106 | 0.002196 |
| `full_same_prepared_query_replay` | same prepared query handle, same input | 428322 | 0.003114 | 0.000001 | 0.000000 | 0.002149 |
| `full_new_query_same_input_same_base` | new query handle, same left input, same prepared right/base | 428322 | 0.141655 | 0.138032 | 0.000001 | 0.002162 |
| `far_query_changed_scale_same_base` | new query with changed scale domain, same prepared right/base | 0 | 1.473499 | 0.613669 | 0.857943 | 0.000073 |
| `full_query_after_far_scale_change` | return to full query after scale changed | 428322 | 1.572960 | 0.706045 | 0.862789 | 0.002145 |

## Interpretation

The matrix separates three regimes.

### 1. Same Prepared Query Replay

```text
full_same_prepared_query_replay ~= 0.003s
```

This is genuine reuse, but it is the same prepared query and same input. It is
not a fresh overlay and not true query-many with distinct queries.

### 2. Same Base, New Query, Same Scale Domain

```text
full_new_query_same_input_same_base ~= 0.142s
```

The right-side grouped range acceleration structure is reused, but the new
left/query handle still pays a smaller scaled-cache cost. This is useful
evidence for a future prepared-base service mode, but it does not remove the
fresh one-shot cost.

### 3. Same Base, Changed Scale Domain

```text
far_query_changed_scale_same_base ~= 1.473s
full_query_after_far_scale_change ~= 1.573s
```

Changing the query scale domain forces the right scaled cache and grouped-range
acceleration to be rebuilt. This is the decisive result: the major workspace
cost is not merely "right base already prepared." It is tied to the current
base/query scale domain.

## Decision

For v2.14.3:

```text
accept current fresh LSI workspace floor
```

The fresh one-shot top4 route must keep this cost in the headline. A benchmark
may separately report same prepared-query replay diagnostics, but must not
use them as fresh overlay evidence.

## Why Not Optimize It Now?

The current workspace floor can be attacked, but not by another simple
prewarm. A real reduction requires a generic product design such as:

```text
prepare_planar_map_lsi_domain(bounds)
prepare_planar_map_lsi_workspace(base, query, domain)
reuse right scaled cache and grouped ranges across compatible queries
```

That design would have to answer:

1. How does a user specify or infer a stable planar-map LSI scale domain?
2. Does the fixed domain preserve the exact Author/RTDLContractPatch LSI
   semantics?
3. How are incompatible queries rejected rather than silently reusing a wrong
   workspace?
4. How is this exposed as a generic planar-map LSI API, not a RayJoin overlay
   shortcut?

Those are product/API questions, not a small v2.14.3 patch.

## What This Proves

1. The global compile / pipeline cost from Goal5002 is removable by generic
   prewarm.
2. The remaining `~1.5-1.7s` cost is workspace/domain dependent.
3. Same prepared-query replay is legitimately fast but only for the same input.
4. Same base plus same scale domain can reuse most right-side workspace.
5. Changing scale domain rebuilds the expensive right scaled cache and grouped
   acceleration.

## What This Does Not Prove

This does not prove:

- author-performance parity;
- a fresh top4 author ratio;
- true query-many;
- that v2.14.3 can exclude LSI workspace from fresh one-shot timing;
- that a fixed-domain workspace API is already correct or implemented;
- that RayJoin-specific core state should be added.

## Next Step

The correct next step is not more LSI workspace micro-optimization in v2.14.3.

Recommended next goal:

```text
Goal5004: v2.14.3 Updated Fresh Matrix After Goal5002/5003
```

That matrix should report:

- fresh one-shot route with LSI workspace included;
- generic-compile-prewarmed diagnostic route;
- same prepared-query replay diagnostic route;
- no true query-many headline;
- no top4 author ratio unless top4 AuthorOfficial is measured.

Future post-v2.14.3 work can open a separate design goal for:

```text
generic fixed-domain / resident planar-map LSI workspace API
```

## Exit Label

```text
accept_current_fresh_lsi_workspace_floor_for_v2_14_3__future_generic_domain_workspace_needed
```
