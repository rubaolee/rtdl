# Call For Review: Goal4997-Goal5004 v2.14.3 RayJoin Binary Route Workstream

Date: 2026-07-05

Please review the full v2.14.3 RayJoin writer-free binary-route workstream from
Goal4997 through Goal5004.

## Requested Verdict Label

```text
approve_goal4997_to_goal5004_v2_14_3_binary_route_status__fresh_headline_5s__diagnostics_separated
```

or:

```text
revise_goal4997_to_goal5004_before_goal5005_docs_boundary
```

## Documents Under Review

Primary goal reports:

```text
history/internal_docs/goal4997_v2_14_3_final_closeout_after_goal4996_2026-07-04.md
history/internal_docs/goal4998_full_stage_device_resident_pipeline_result_2026-07-04.md
history/internal_docs/goal4999_device_midpoint_query_points_handoff_result_2026-07-04.md
history/internal_docs/goal5001_regime_and_lsi_producer_decision_gate_2026-07-05.md
history/internal_docs/goal5002_fresh_lsi_compile_prewarm_result_2026-07-05.md
history/internal_docs/goal5003_lsi_per_input_workspace_floor_decision_2026-07-05.md
history/internal_docs/goal5004_updated_v2_14_3_performance_matrix_2026-07-05.md
```

Interim review / response documents:

```text
history/internal_docs/interim_check_goal4999_and_goals5000_5006_device_resident_pipeline_2026-07-04.md
history/internal_docs/call_for_review_interim_check_goal4999_and_goals5000_5006_2026-07-04.md
history/internal_docs/claude_review_interim_goal4999_and_goals5000_5006_2026-07-05.md
history/internal_docs/response_to_claude_interim_goal4999_goals5000_5006_review_2026-07-05.md
history/internal_docs/call_for_review_response_to_claude_interim_goal4999_goals5000_5007_2026-07-05.md
history/internal_docs/claude_review_response_goals5000_5007_regime_honest_2026-07-05.md
```

Key artifacts:

```text
history/internal_docs/goal4998_full_stage_device_resident_pipeline_artifacts_2026-07-04/
history/internal_docs/goal4999_device_midpoint_query_points_artifacts_2026-07-04/
history/internal_docs/goal5001_regime_lsi_decision_artifacts_2026-07-05/fresh_one_shot_device_resident_carrier_top4.json
history/internal_docs/goal5002_lsi_compile_prewarm_artifacts_2026-07-05/
history/internal_docs/goal5003_lsi_workspace_floor_artifacts_2026-07-05/lsi_workspace_floor_probe_top4.json
history/internal_docs/goal5004_updated_performance_matrix_artifacts_2026-07-05/fresh_after_accounting_fix_top4.json
```

Relevant code/test changes:

```text
Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
tests/goal4999_device_query_point_location_handoff_test.py
history/internal_docs/goal5002_lsi_compile_prewarm_probe.py
history/internal_docs/goal5003_lsi_workspace_floor_probe.py
```

## Executive Summary To Review

The workstream corrected the earlier tendency to optimize and report the
`~0.33s` prepared replay body as if it were product performance. It now reports
three regimes separately:

| Regime | Current Status | Accounting-complete time |
|---|---|---:|
| Fresh one-shot top4 writer-free binary route | product-relevant v2.14.3 evidence | `5.003915s` |
| Generic compile-prewarmed top4 route | diagnostic / future service-start prewarm evidence | `4.584897s` |
| Same prepared-query replay | diagnostic only; same input replay, not true query-many | `0.332861s` |

The fresh top4 route is therefore **not** `0.33s`. It is approximately `5.00s`
in the current v2.14.3 binary route.

The corrected fresh top4 split is:

```text
writer_free_hot_sec = 5.003915s
LSI producer        = 2.628660s
downstream          = 2.375255s
LSI rows            = 428322
descriptor pairs    = 15014
```

## Goal-by-Goal Summary

### Goal4997

Closed the previous v2.14.3 state after Goal4996. This was the staging point
before the owner forced continued work toward a fuller device-resident binary
route.

Review focus:

- Was Goal4997 correctly superseded by later Goals4998-5004?
- Does any Goal4997 wording now need revision because Goal5004 corrected the
  fresh headline to `5.003915s`?

### Goal4998

Implemented an experimental writer-free `--device-resident-carrier` route in
the RayJoin paper app.

Scope:

- app-layer implementation in `section57_overlay_columnar_binary.py`;
- no RayJoin-specific RTDL core primitive;
- device-side midpoint face scatter;
- prepared-session carrier arrays;
- device carrier construction kernels;
- device descriptor-pair consumer.

Effect:

- It connected the existing RTDL/Numba device-column assets to the real
  RayJoin reprojection/sort/midpoint/PIP/carrier/consumer path.
- It did not prove fresh author parity.
- It was originally measured mostly in prepared replay / repeat protocol, not
  fresh one-shot.

Review focus:

- Is this a legitimate app-layer writer-free binary route?
- Does it preserve the generic RTDL boundary?
- Are its measurements correctly treated as binary descriptor route evidence,
  not paper-text byte-equality evidence?

### Goal4999

Removed another host boundary: midpoint query points are now generated on
device and handed to native directed point-location / PIP through a generic
device-query-point API.

Effect:

- modest prepared-replay improvement only (`~1.026x`);
- important architectural cleanup;
- no fresh one-shot performance claim by itself.

Review focus:

- Is the native/public API generic directed point-location device-query input,
  not a hidden RayJoin overlay kernel?
- Is it correct to call the improvement architectural rather than a major
  speedup?

### Interim Review And Response

Claude found that the `~0.3295s` number was same-input prepared replay, not
fresh performance and not true query-many. The response accepted this and
restructured the plan around a regime decision gate.

Review focus:

- Did the team fully accept regime honesty?
- Is `query-many` now forbidden unless distinct query batches are actually
  measured?
- Is `0.3295s` correctly demoted to diagnostic replay evidence?

### Goal5001

Decision gate:

```text
target_fresh_lsi_producer_first
```

Fresh one-shot evidence at that stage:

```text
fresh top4 ~= 4.816061s
LSI producer ~= 2.587732s
downstream ~= 2.366445s
```

The exact fresh headline was later corrected by Goal5004 because the
`writer_free_hot_sec` accounting omitted device midpoint query-point phases.

Review focus:

- Was the decision to target fresh LSI producer correct?
- Is the old `4.816061s` now correctly treated as superseded by Goal5004's
  accounting-complete `5.003915s`?

### Goal5002

Tested whether LSI compile / pipeline ensure cost is globally prewarmable.

Result:

```text
top4 compile-like LSI cost before tiny generic prewarm:
  exact_pipeline_ensure + split_kernel_ensure = 0.988718s

top4 compile-like LSI cost after tiny generic prewarm:
  exact_pipeline_ensure + split_kernel_ensure = 0.000000591s
```

Interpretation:

- generic global LSI compile / pipeline initialization is prewarmable;
- tiny prewarm uses public generic `prepare_planar_map_lsi_2d_optix`;
- this is not a one-shot speedup if prewarm time is counted in the same command;
- remaining LSI floor is per-input workspace.

Review focus:

- Is the prewarm generic and non-RayJoin-specific?
- Is it correctly classified as diagnostic / future service-start precompile
  evidence rather than a fresh one-shot headline?

### Goal5003

Tested the remaining LSI workspace floor.

Key evidence:

```text
first full run after generic compile prewarm: 1.711297s
same prepared query replay:                  0.003114s
new query, same input, same base:            0.141655s
changed query scale domain:                  1.473499s
full query after scale changed back:         1.572960s
```

Decision:

```text
accept_current_fresh_lsi_workspace_floor_for_v2_14_3__future_generic_domain_workspace_needed
```

Interpretation:

- same prepared query replay is fast but diagnostic;
- same base / same scale domain can reuse most right-side workspace;
- changing the scale domain rebuilds expensive workspace;
- v2.14.3 must keep per-input LSI workspace in fresh timing.

Review focus:

- Is the conclusion correct that the remaining LSI floor is scale-domain /
  workspace dependent?
- Is it correct to defer any fixed-domain workspace API to future product work?

### Goal5004

Updated the final matrix and fixed a measurement-accounting bug.

Bug:

`writer_free_hot_sec` used old midpoint keys:

```text
midpoint_points_map0_columnar_sec
midpoint_points_map1_columnar_sec
```

but the Goal4999 device route uses:

```text
midpoint_points_map0_device_query_points_sec
midpoint_points_map1_device_query_points_sec
```

Fix:

- device-resident carrier route now counts device query-point midpoint phases;
- regression test added.

Post-fix POD fresh top4:

```text
writer_free_hot_sec = 5.003915s
LSI = 2.628660s
downstream = 2.375255s
rows = 428322
descriptor pairs = 15014
```

Review focus:

- Is the accounting fix correct?
- Is `5.003915s` now the correct v2.14.3 fresh top4 headline?
- Are diagnostic `4.584897s` and `0.332861s` separated correctly?

## Specific Review Questions

1. Does the workstream preserve the principle:

   ```text
   RTDL is a generic system; RayJoin is an app on top of it.
   ```

2. Did any Goal4997-Goal5004 implementation add hidden RayJoin-specific RTDL
   core semantics?

3. Is Goal4998's `--device-resident-carrier` route a legitimate writer-free
   app/operator route rather than a paper-text reproduction route?

4. Is Goal4999's device-query-point API generic directed point-location input,
   even though legacy internal naming debt remains?

5. Did Goal5001 correctly reject the old downstream-first plan and target fresh
   LSI producer first?

6. Does Goal5002 prove that the LSI compile / pipeline ensure cost is globally
   prewarmable by generic LSI, while correctly refusing to use that as a fresh
   one-shot headline?

7. Does Goal5003 prove that the remaining LSI workspace cost is scale-domain /
   base-query dependent, and therefore must remain in v2.14.3 fresh timing?

8. Is Goal5004's measurement-accounting fix correct and sufficient?

9. Is the corrected fresh top4 headline:

   ```text
   5.003915s
   ```

   rather than the older undercounted `~4.8s` or the prepared replay
   `~0.33s`?

10. Should the workstream close this segment and proceed to Goal5005
    documentation / release-boundary update using the corrected matrix?

## Claims To Approve If Correct

The reviewer may approve these bounded claims:

```text
1. v2.14.3 has a writer-free binary RayJoin 5.7 app/operator route.
2. The route uses generic RTDL primitives plus app-layer Numba/CUDA continuation.
3. The corrected fresh top4 writer-free binary route is 5.003915s.
4. Generic compile prewarm can reduce the measured route window to 4.584897s
   only when prewarm is legitimately outside the route window.
5. Same prepared-query replay reaches about 0.332861s, but this is diagnostic
   only and not true query-many.
6. The remaining fresh cost is split roughly between LSI producer/workspace
   and downstream binary route.
```

## Claims Not To Approve

The reviewer should reject any wording that implies:

```text
1. v2.14.3 fresh top4 is 0.33s.
2. prepared replay is true query-many.
3. v2.14.3 reaches author-performance parity.
4. top4 author ratio is known.
5. the binary route proves paper text byte equality.
6. RTDL has full zero-copy overlay.
7. LSI per-input workspace is solved.
8. a RayJoin-specific core primitive is acceptable.
```

## Requested Next Step If Approved

If this review passes, authorize:

```text
Goal5005: v2.14.3 Documentation And Release Boundary Update After Corrected Matrix
```

Goal5005 must update documents to use:

```text
fresh top4 writer-free binary route: 5.003915s
compile-prewarm route: diagnostic
prepared replay route: diagnostic
top4 author ratio: not measured
true query-many: not demonstrated
```

## Non-Authorization Boundary

This review should not approve:

- additional performance implementation work;
- new runtime/native changes;
- public release of v2.14.3;
- author-performance parity claims;
- top4 author ratios without measured top4 AuthorOfficial timing;
- true query-many claims;
- hiding fresh LSI workspace cost;
- hidden RayJoin-specific RTDL core semantics.
