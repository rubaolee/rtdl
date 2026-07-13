# Goal4888: Core Phase Decomposition Gate Before Prepared/Fused Work

Date: 2026-07-03

Status: `proposed_after_goal4887_block__measurement_only`

## Trigger

Goal4887 proposed a generic prepared-session + fused-continuation plan with a
target prepared hot query+output time of `3-8 s`.

Claude's review blocked that plan:

```text
verdict: block_as_rayjoin_specific_or_underdesigned
```

The core objection is accepted:

```text
RTDL+Numba v2 query+output:       20.920 s
RTDL+Numba v2 core query compute: 18.880 s

Goal4887 target query+output:      3-8 s
```

Because output writing is already about `2.040 s`, reaching `3-8 s` requires
cutting the `18.880 s` core compute down to roughly `1-6 s`.

Goal4887 did not prove that this `18.880 s` is dominated by Python/host
materialization rather than RT LSI/PIP kernel time. Without that proof, the
plan risks repeating the V3 failure: setting a performance goal before proving
the performance source.

## One-Line Goal

Measure and decompose the current RTDL+Numba RayJoin Section 5.7 hot path so we
know whether prepared/fused continuation has a real performance source before
any engine implementation begins.

## Scope

This goal is **measurement only**.

It may:

- add a temporary analysis harness under `history/internal_docs/` or
  `tools/tmp/`;
- rerun the Australia representative workload;
- collect detailed phase times;
- report exact denominators and materialization points;
- classify the bottleneck.

It must not:

- modify `src/rtdsl/**`;
- modify `src/native/**`;
- add prepared-session APIs;
- add row-buffer APIs;
- add continuation APIs;
- add RayJoin-specific fast paths;
- change correctness/comparator boundaries;
- claim any performance improvement.

## Required Decomposition

The `18.880 s` core compute bucket must be split into at least:

1. public RTDL LSI traversal / row production;
2. LSI row materialization or row download;
3. intersection reprojection;
4. sort/reordering;
5. vertex PIP map0-in-map1 traversal;
6. vertex PIP map0-in-map1 upload/download/materialization;
7. vertex PIP map1-in-map0 traversal;
8. vertex PIP map1-in-map0 upload/download/materialization;
9. midpoint generation;
10. midpoint PIP traversal;
11. Numba continuation time;
12. Python-only orchestration time not already attributed;
13. host/device transfer or host materialization time if measurable.

If the existing summaries already expose a field, use it. If they do not, the
goal may add instrumentation only in an external harness copy, not in RTDL
core.

## Inputs

Primary route:

```text
Australia representative Section 5.7
left:  lakes_Australia_current_osm_Point.cdb
right: parks_Australia_current_osm_Point.cdb
comparator: AuthorOfficial / Author+RTDLContractPatch output
```

Primary current artifact:

```text
history/internal_docs/goal4886_pod_numba_au_skip_v2_summary.json
```

Current known top-level phases:

```text
lsi_public_rows_sec:             5.666642814874649
intersection_reprojection_sec:   0.4334440380334854
sort_map0_sec:                   0.20129620283842087
sort_map1_sec:                   0.19340070337057114
vertex_pip_map0_in_map1_sec:    10.700430862605572
vertex_pip_map1_in_map0_sec:     1.5591728761792183
midpoint_pip_map0_sec:           0.06625231355428696
midpoint_pip_map1_sec:           0.059853315353393555
output_chain_write_sec:          2.039528727531433
```

Current native point-location subfields:

```text
vertex_pip_map0_in_map1:
  point_upload: 0.037994229
  traversal:    9.784154503
  row_download: 0.018498268

vertex_pip_map1_in_map0:
  point_upload: 0.00298305
  traversal:    1.52976916
  row_download: 0.001351374

midpoint_pip_map0:
  traversal:    0.065761965
  row_download: 0.000021441

midpoint_pip_map1:
  traversal:    0.059341061
  row_download: 0.000024897
```

## Early Read From Existing Evidence

The existing summary already suggests that the major hot-path cost is likely
native traversal, not Python writer overhead:

```text
vertex PIP traversal total:
9.784154503 + 1.52976916
= 11.313923663 s
```

LSI public rows:

```text
5.666642814874649 s
```

Together:

```text
17.0 s of the 18.880 s core bucket
```

This is why the original Goal4887 performance target is not currently
justified. If this early read holds, prepared/fused continuation alone cannot
reach `3-8 s`; it would need native primitive/kernel work or algorithmic
changes, which are outside the original generic continuation plan.

## Work Plan

### Step 1: Recompute The Existing Phase Ledger

Use existing Goal4886 JSON artifacts to produce a machine-readable ledger:

```text
history/internal_docs/goal4888_existing_phase_decomposition_2026-07-03.json
history/internal_docs/goal4888_existing_phase_decomposition_2026-07-03.md
```

The ledger must separate:

- cold load/pack;
- query/output;
- output write;
- core compute;
- native traversal;
- upload/download;
- Python or partner continuation.

### Step 2: Identify Missing Instrumentation

List what cannot be separated from current summaries.

Examples:

- LSI traversal vs LSI row materialization if not exposed separately;
- Python orchestration inside vertex PIP wrapper if not exposed;
- row conversion cost if folded into outer phase.

Output:

```text
history/internal_docs/goal4888_missing_instrumentation_list_2026-07-03.md
```

### Step 3: Optional Focused Rerun

Only if needed, run a focused Australia representative rerun with external
harness-level timers.

Rules:

- no RTDL core/native edits;
- no comparator changes;
- output must remain byte-equal;
- if rerun differs materially from existing summary, report both.

### Step 4: Bottleneck Classification

Classify the `18.880 s` core bucket into one of:

1. `native_rt_traversal_dominated`
2. `host_materialization_dominated`
3. `python_orchestration_dominated`
4. `mixed_but_fusion_plausible`
5. `insufficient_instrumentation`

## Decision Gate

After Goal4888:

### If `host_materialization_dominated` or `python_orchestration_dominated`

Then a revised prepared/fused continuation goal may be allowed, with targets
based on the measured removable cost.

### If `native_rt_traversal_dominated`

Then the Goal4887 `3-8 s` target is rejected. The next work must be reframed as
one of:

- generic native primitive/kernel improvement;
- algorithmic candidate pruning;
- a correctness/architecture hygiene goal with no performance promise;
- or an explicitly deeper native fusion project with separate approval.

### If `mixed_but_fusion_plausible`

Then rewrite Goal4887 with a target no lower than the measured non-native
removable cost.

### If `insufficient_instrumentation`

Then do not implement prepared/fused work yet. First add measurement support in
a bounded way.

## Acceptance Criteria

Goal4888 succeeds if it produces:

1. a phase ledger from existing artifacts or a byte-equal focused rerun;
2. a clear split of native traversal vs materialization vs Python/partner work;
3. a bottleneck classification;
4. an explicit decision on whether Goal4887's `3-8 s` target survives;
5. no RTDL core/native modifications.

## Expected Outcome

Based on existing summaries, the expected result is:

```text
native_rt_traversal_dominated
```

If that is confirmed, the correct conclusion is uncomfortable but useful:

```text
prepared session and formal Numba continuation are still good generic
engineering work, but they should not be sold as the path to 3-8 s RayJoin
prepared hot query+output unless native primitive/kernel time is also reduced.
```

## Goal-Level Decision Audit

1. **Am I being stupid?**

   The stupid path would be to continue implementing Goal4887 after Claude
   pointed out the arithmetic contradiction.

2. **What action would make this stupid?**

   Writing code for prepared/fused APIs before measuring the `18.880 s` core
   bucket would repeat the V3 failure mode.

3. **Is there another path that avoids being stuck?**

   Yes. Measure first. If the bottleneck is native traversal, stop pretending
   continuation work alone can close it.

4. **Can I start a different path that truly solves the problem?**

   Yes. The correct path is:

   ```text
   decompose core time -> classify bottleneck -> rewrite implementation goal
   around the measured bottleneck
   ```

## Non-Authorization

This goal does not authorize:

- Goal4887 implementation;
- prepared-session API changes;
- row-buffer ABI changes;
- Numba partner API changes;
- native kernel changes;
- RayJoin-specific shortcuts;
- broad performance claims;
- changing public release wording.
