# Goal5001 Result: Regime And LSI Producer Decision Gate

Date: 2026-07-05

## Verdict

```text
target_fresh_lsi_producer_first
```

Goal5001 decides that v2.14.3 must not continue by optimizing the `0.33s`
prepared replay body as if it were a product `query-many` result.

The next implementation work should target the fresh LSI producer first,
especially the reusable compile / pipeline-ensure portion of the LSI cost.

## Why This Goal Exists

Claude approved Goal4999 but blocked the old Goals5000-5006 implementation plan.
The reason was regime confusion:

- Goal4999 measured `~0.3295s` in a `--prepared-operator-session --repeat 5`
  route.
- That route replays the same top4 input inside one process.
- Its median LSI phase is only `~0.003s`.
- Therefore the `~2.7s` fresh exact LSI producer is cached out.

That `0.3295s` value is valid as a prepared replay diagnostic, but it is not a
fresh one-shot result and not a demonstrated true `query-many` workload.

## Evidence Used

Existing evidence:

```text
history/internal_docs/goal4982_lsi_and_carrier_fresh_warm_isolation_result_2026-07-04.md
history/internal_docs/goal4985_v2_14_3_final_performance_matrix_2026-07-04.md
history/internal_docs/goal4999_device_midpoint_query_points_handoff_result_2026-07-04.md
history/internal_docs/goal4999_device_midpoint_query_points_artifacts_2026-07-04/device_query_midpoint_top4_repeat5.json
```

New Goal5001 POD artifact:

```text
history/internal_docs/goal5001_regime_lsi_decision_artifacts_2026-07-05/fresh_one_shot_device_resident_carrier_top4.json
```

POD:

```text
root@157.157.221.29 -p 25248
repo: /root/rtdl_goal4988
```

Fresh one-shot command:

```text
python Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
  --left Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_county.cdb
  --right Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_zipcode.cdb
  --pair-name top4_county_zipcode
  --summary /root/rtdl_goal5001_fresh_one_shot_device_resident_carrier.json
  --device-columnar
  --bounded-exact-lsi-device-columns
  --bounded-exact-lsi-capacity 1000000
  --point-location-device-face-columns
  --fast-scaled-point-pack
  --device-resident-carrier
```

## Regime Table

| Regime | Evidence | Status |
|---|---:|---|
| Fresh one-shot top4, current device-resident carrier route | `4.816061s` | Product-relevant fresh evidence |
| Prepared replay top4, same input repeated | median `0.329542s` | Diagnostic only |
| True prepared/query-many with distinct query batches | not measured | Not authorized |
| Paper text writer route | separate reproduction route | Correctness / format route, not binary performance route |

## Fresh One-Shot Breakdown

From the Goal5001 fresh artifact:

| Component | Seconds |
|---|---:|
| Fresh writer-free route | `4.816061` |
| LSI producer | `2.587732` |
| Downstream floor | `2.366445` |
| LSI native OptiX launch | `0.002177` |
| LSI exact pipeline ensure | `0.512160` |
| LSI split kernel ensure | `0.400800` |
| LSI grouped range ensure | `0.986021` |
| LSI scaled cache ensure | `0.684211` |

LSI producer decomposition:

```text
compile / pipeline-like cost:
  exact_pipeline_ensure + split_kernel_ensure
  = 0.512160 + 0.400800
  = 0.912960s

per-input workspace-like cost:
  grouped_range_ensure + scaled_cache_ensure
  = 0.986021 + 0.684211
  = 1.670232s

actual native launch:
  ~0.002177s
```

This shows that "LSI is slow" does not mean traversal is slow. The launch is
tiny. The major costs are producer setup/ensure work.

## Prepared Replay Breakdown

From Goal4999:

| Component | Seconds |
|---|---:|
| Prepared replay median | `0.329542` |
| Median LSI phase | `0.003082` |
| Median downstream floor | `0.329779` |

The replay route is useful to isolate downstream floors, but it is not evidence
that fresh overlay can run in `0.33s`. It reuses same-input prepared state.

## True Query-Many Status

True prepared/query-many is not demonstrated.

The current CLI supports:

```text
--prepared-operator-session --repeat N
```

but the implementation repeats the same left/right CDB pair. That is same-input
prepared replay, not multiple distinct query batches.

The POD currently has only:

```text
top4_county.cdb
top4_zipcode.cdb
```

under the top4 ArcGIS data directory. There is no measured workload of one
prepared base serving multiple distinct query CDB batches.

Therefore:

```text
true prepared/query-many claim: not authorized
```

The CLI/help wording that calls repeat mode "prepared/query-many" is a naming
debt and should be corrected before release/staging.

## Decision

Goal5001 chooses:

```text
target_fresh_lsi_producer_first
```

Reason:

1. Fresh one-shot is the product-relevant default.
2. Fresh top4 is dominated by LSI producer setup/ensure cost.
3. Prepared replay `0.3295s` is same-input diagnostic, not true query-many.
4. Downstream `0.33s` micro-optimizations cannot materially move the fresh
   `4.8s` result while the `~2.6-2.7s` LSI producer remains.
5. The most honest first target is the reusable compile / pipeline-ensure part
   of the LSI producer (`~0.91s`), followed by a decision on whether the
   per-input workspace cost (`~1.67s`) is reducible.

## Revised Next Goals

### Goal5002: Fresh LSI Producer Compile/Ensure Reduction Design

Purpose:

Attack the fresh LSI producer first, without relying on same-input replay.

Work:

- Identify whether `exact_pipeline_ensure` and `split_kernel_ensure` can be
  reused as a generic precompiled / prepare-once pipeline within a process.
- Keep this generic for planar-map/segment-pair LSI, not RayJoin overlay.
- Do not hide per-input workspace cost.

Verification:

- Fresh one-shot route measured before and after.
- Prepared replay diagnostic may be reported but cannot be the headline.
- LSI decomposition must show which sub-cost moved:
  - exact pipeline ensure;
  - split kernel ensure;
  - grouped range ensure;
  - scaled cache ensure;
  - native launch.

Exit labels:

```text
completed_fresh_lsi_compile_reuse_reduction
```

or

```text
blocked_lsi_compile_reuse_not_available_without_core_redesign
```

### Goal5003: LSI Per-Input Workspace Decision

Purpose:

Decide whether `grouped_range_ensure + scaled_cache_ensure ~= 1.67s` is a real
per-input cost or reducible through a generic workspace contract.

Work:

- Measure whether these costs are tied to the particular left/right input.
- If reducible, design a generic workspace reuse contract.
- If not reducible, document it as the fresh LSI floor for v2.14.3.

Verification:

- Fresh measurement required.
- Same-input replay cannot be used to claim improvement.
- No RayJoin-specific workspace hidden in RTDL core.

Exit labels:

```text
target_lsi_workspace_reuse_contract
```

or

```text
accept_per_input_lsi_workspace_floor_for_v2_14_3
```

### Goal5004: Downstream Device-Resident Polish Only After LSI Decision

Purpose:

Only after the LSI producer decision, return to run-bound/sort/carrier/consumer
work if still worthwhile.

Work:

- Device run-bound generation.
- Ordering primitive decision.
- Binary carrier output contract.
- Real downstream operator proof.

Verification:

- Fresh and prepared replay both reported.
- Any downstream improvement must be framed as architecture polish unless it
  materially moves fresh.

Exit label:

```text
completed_downstream_device_resident_polish_after_lsi_decision
```

### Goal5005: Regime-Separated Performance Matrix

Purpose:

Produce the matrix only after the LSI decision and any authorized implementation.

Required columns:

- fresh one-shot;
- prepared replay diagnostic;
- true query-many if demonstrated;
- paper text route;
- writer-free binary route;
- downstream operator route if implemented.

Exit label:

```text
completed_regime_separated_v2_14_3_matrix
```

### Goal5006: Release/Staging Boundary Report

Purpose:

Close v2.14.3 with honest regime labels and public-surface boundaries.

Exit label:

```text
approve_v2_14_3_regime_honest_release_staging
```

## Non-Authorization Boundary

Not authorized:

- no use of `0.3295s` as fresh performance;
- no use of `0.3295s` as true query-many;
- no downstream-only goal sequence before LSI producer decision;
- no hidden RayJoin-specific LSI producer optimization in RTDL core;
- no author-performance ratio for top4 unless measured on top4;
- no release wording that calls same-input replay "query-many."

## Immediate Next Step

Start Goal5002:

```text
Fresh LSI Producer Compile/Ensure Reduction Design
```

This should be a design + measurement goal first. It may become an implementation
goal only if the reusable compile/pipeline ensure path is generic and can be
validated on fresh one-shot measurements.
