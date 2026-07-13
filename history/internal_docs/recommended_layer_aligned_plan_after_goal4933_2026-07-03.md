# Recommended Layer-Aligned Plan After Goal4933

Date: 2026-07-03

Status: recommendation for owner review. This document does not authorize implementation by itself.

## Executive Summary

My recommendation is to **revise the post-Goal4933 plan before implementing Goal4934**.

Goal4933 taught an important lesson:

- A generic grouping API can preserve correctness.
- But if the output backend still consumes Python lists, Python strings, and app-side chain loops, it will not solve the performance problem.

Therefore the next plan must not jump directly from "generic grouping works" to "compiled writer." It must first establish a **generic row-buffer/data-shape contract** that can carry grouped output data without Python object materialization.

The correct sequence is:

1. **Layer 0 confirmation**: already mostly done, but summarize the current measured bottleneck.
2. **Layer 3 feasibility gate**: decide whether the writer problem is generic or RayJoin-specific.
3. **Layer 1 row-buffer/data-shape gate**: define the generic columnar/native shape that Layer 3 will consume.
4. **Layer 3 prototype**: only then build a generic compiled/vectorized output materializer.
5. **RayJoin public-sample validation**: byte-equal and faster, or stop.
6. **Non-RayJoin proof**: prove the output layer is a real RTDL feature, not a RayJoin disguise.
7. **Repeated POD scorecard and release decision**.

In one sentence:

> Do not build a faster RayJoin writer. Build a generic output-materialization layer that RayJoin can use; if that is impossible, stop and classify the remaining gap as app-output-specific.

## Why The Previous Goal Chain Needs Adjustment

The previous document, `next_goals_after_goal4933_generic_output_assembly_2026-07-03.md`, correctly identified the immediate bottleneck: the writer is still slow and Goal4933 is correct but not faster.

But it underweighted one architectural fact:

> A compiled output backend cannot be clean or fast if its input is still Python object/list/string state.

Goal4933 currently works like this:

```text
RTDL primitives
  -> Python app state
  -> Python point_lines list
  -> Python chain_headers dict
  -> generic grouped assembly over integer line indexes
  -> Python loop reconstructs author-compatible text
```

That is useful as a correctness bridge, but it is not the target architecture.

The target architecture needs:

```text
RTDL primitives
  -> generic columnar row buffer
  -> generic grouped/materialized output records
  -> app-owned thin final formatting
```

This is why **Layer 1 must appear before any serious Layer 3 implementation**.

## Mapping To The Existing Layer Plan

### Layer 0: Measurement

Original role:

Measure writer composition and confirm warm/hot phase boundaries.

Current evidence:

- Goal4930 showed writer work is structure-dominant enough to justify a generic output assembly investigation.
- Goal4933 showed the first generic grouping attempt preserved correctness but regressed writer time:
  - plain writer: `2.069s`
  - generic-wired writer: `2.982s`
  - generic grouping itself: `0.331s`
  - remaining Python chain loops: `1.266s + 1.046s`

Interpretation:

Layer 0 has enough evidence to continue, but it changes the target:

- not "more grouping";
- not "Python micro-tuning";
- but "remove Python object/list/text chain loops from the hot writer path."

### Layer 1: Row-Buffer / Data-Shape Foundation

Original role:

Keep intermediate rows in a generic columnar/native shape so later layers do not consume Python objects.

Status:

Not done.

Why it matters now:

Layer 3 cannot be meaningfully compiled if it receives:

- Python dictionaries;
- Python lists of strings;
- Python tuple points;
- Python object graphs;
- RayJoin-specific output-chain objects.

Layer 1 for this line does not have to be full device-resident GPU memory yet. The immediate required form is:

- generic columnar arrays;
- stable schemas;
- no RayJoin naming;
- no author output-chain semantics;
- usable by more than one app.

Minimum acceptable v2.14.2 Layer 1 for output assembly:

```text
group_id: int64[N]
item_order: int64[N]
payload columns: primitive arrays
optional validity mask
optional descriptor columns
```

This can start host-columnar and later become device-resident. But it must be designed so Layer 3 is not forced to read Python strings.

### Layer 2: Numeric Continuation

Original role:

Move numeric work such as reprojection, sort, dedupe, and group into compiled/device kernels.

Status:

Partly probed, not the immediate top bottleneck.

Recommendation:

Do not prioritize Layer 2 before the writer problem. Revisit after Layer 3 changes the phase breakdown.

Reason:

The current writer is still a larger, clearer target. Reprojection/sort matters, but it is not the next highest-confidence payoff.

### Layer 3: Generic Compiled Output Assembly

Original role:

Convert grouped rows into compact output records/columns/lines without Python chain loops.

Status:

Started but not solved.

Goal4932/4933 provided:

- generic grouping API;
- correctness proof;
- RayJoin app wiring;
- proof that grouping alone is insufficient.

The next Layer 3 work must target the expensive part:

```text
chain_loop_map0_sec = 1.266s
chain_loop_map1_sec = 1.046s
```

But it must only proceed if this work can be expressed generically.

Allowed generic concepts:

- group descriptors;
- item rows;
- stable group ordering;
- stable item ordering;
- columnar payload extraction;
- record buffers;
- generic CSV/Arrow/binary-like output records;
- generic line-fragment materialization if format-neutral.

Forbidden core concepts:

- RayJoin overlay chain writer;
- author output-chain text format;
- map0/map1 overlay-specific semantics in the output core;
- polygon/face id rules hidden inside RTDL output assembly;
- any function whose only honest consumer is RayJoin.

## Recommended Revised Goal Chain

This replaces the previous rough Goal4934-4940 sequence if the owner approves it.

### Goal4934: Layer 3 Feasibility And Writer Semantics Audit

Purpose:

Decide whether the remaining writer work is generic output materialization or RayJoin-specific author-format logic.

Work:

- Audit the current Section 5.7 writer line by line.
- Classify each operation:
  - generic grouping;
  - generic ordering;
  - generic descriptor construction;
  - generic item materialization;
  - app-specific id policy;
  - app-specific author text formatting;
  - file IO.
- Produce a proposed generic output IR if honest.

Verification:

- Every writer subphase is classified.
- No ambiguous "generic-ish" category.
- The report explicitly says whether Layer 3 is feasible.
- External review checks for hidden RayJoin semantics.

Exit labels:

- `layer3_generic_feasible`
- `writer_is_app_specific_stop`
- `needs_layer1_shape_before_decision`

### Goal4935: Layer 1 Output Row-Buffer/Data-Shape Contract

Entry condition:

Goal4934 exits `layer3_generic_feasible` or `needs_layer1_shape_before_decision`.

Purpose:

Define the generic columnar/native data shape that a future output materializer consumes.

Work:

- Specify generic schemas for:
  - group keys;
  - order keys;
  - descriptor columns;
  - payload/item columns;
  - validity masks;
  - optional dedupe keys.
- Implement only the minimum host-columnar contract if needed for tests.
- Avoid device-resident implementation unless separately authorized.

Verification:

- No RayJoin/app identity in schema names.
- A RayJoin adapter can map into this shape.
- At least one non-RayJoin fixture can map into this shape.
- Tests prove deterministic grouping/order.

Exit labels:

- `layer1_shape_contract_ready`
- `shape_contract_rejected_as_app_specific`

### Goal4936: Generic Output Materializer Prototype

Entry condition:

Goal4935 exits `layer1_shape_contract_ready`.

Purpose:

Prototype a generic materializer that consumes the Layer 1 shape and reduces Python chain-loop cost.

Work:

- Prototype materialization from generic columnar input.
- Prefer vectorized/Numba/native implementation only where it stays generic.
- Do not implement author/RayJoin final formatting in core.

Verification:

- Synthetic Section 5.7-scale data.
- Non-RayJoin synthetic grouped-output data.
- Materializer faster than equivalent Python loop on synthetic scale.
- No app identity strings in core.

Exit labels:

- `generic_materializer_beats_python_loop`
- `correct_but_not_faster_stop`
- `rejected_as_app_specific`

### Goal4937: RayJoin Public-Sample Wiring

Entry condition:

Goal4936 exits `generic_materializer_beats_python_loop`.

Purpose:

Test whether the materializer helps the real RayJoin Section 5.7 public sample.

Work:

- Wire the materializer into `Paper-reproduction-apps/rayjoin-paper/section57_overlay_numba.py`.
- Keep final author-compatible formatting app-owned.
- Run on POD with warmed cache.

Verification:

- Byte-equal to public answer.
- Compare against Goal4933:
  - plain writer: `2.069s`;
  - generic-wired writer: `2.982s`.
- Minimum performance gate:
  - must beat `2.069s` repeatedly.
- Target:
  - `output_chain_write_sec <= 1.65s`.

Exit labels:

- `rayjoin_writer_speedup_generic_and_byte_equal`
- `byte_equal_but_not_faster_stop`
- `correctness_failed_redo_or_revert`

### Goal4938: Non-RayJoin Generality Proof

Entry condition:

Goal4937 exits `rayjoin_writer_speedup_generic_and_byte_equal`.

Purpose:

Prove the materializer is not a RayJoin-only subsystem.

Work:

- Use the same Layer 1 shape and materializer on a non-RayJoin workload.
- Good candidates:
  - grouped segment-pair output;
  - radius-neighbor grouped output;
  - kNN result grouping;
  - spatial join grouped pairs.

Verification:

- Non-RayJoin correctness test.
- Same materializer API.
- No RayJoin imports.
- At least not slower than old Python output loop.

Exit labels:

- `genericity_proven_on_second_workload`
- `rayjoin_only_reject_core_promotion`

### Goal4939: Layer 2 Revisit After Writer Improvement

Entry condition:

Goal4938 exits `genericity_proven_on_second_workload`, or owner explicitly decides to stop the writer line and inspect the next bottleneck.

Purpose:

Re-measure the hot path after writer changes and decide whether numeric continuation is now the bottleneck.

Work:

- Re-run phase decomposition.
- Inspect:
  - reprojection;
  - sort;
  - dedupe/group;
  - row conversion/marshal;
  - remaining writer.
- Decide whether Layer 2 is worth implementing.

Verification:

- New phase table.
- No implementation unless Layer 2 has a measured target.
- If reproj/sort is already NumPy/C-speed dominated, stop.

Exit labels:

- `layer2_numeric_continuation_now_worth_it`
- `writer_remains_dominant_stop_or_redesign`
- `no_more_hot_python_target_stop`

### Goal4940: Repeated POD Scorecard

Entry condition:

At least one implementation goal exits with a real performance win.

Purpose:

Produce a serious repeated-run scorecard.

Work:

- Repeated warmed-cache POD runs.
- Plain route vs new route.
- Public sample plus any representative pairs that are valid.

Verification:

- Correctness for every row.
- At least 5 runs per route.
- Median/min/max/raw artifacts.
- No broad claim from one noisy run.

Exit labels:

- `scorecard_supports_v2_14_2_performance_claim`
- `scorecard_supports_internal_only`
- `scorecard_rejects_performance_claim`

### Goal4941: Public/Private Boundary And Release Decision

Entry condition:

Goal4940 complete.

Purpose:

Decide whether v2.14.2 gets a public feature/performance claim.

Work:

- Classify the output materializer:
  - public API;
  - internal API;
  - paper-reproduction app-local;
  - removed.
- Draft public docs only if supported by evidence.

Verification:

- Public surface scan.
- External review.
- No unsupported performance wording.

Exit labels:

- `authorize_v2_14_2_output_materializer_release`
- `keep_internal_no_public_claim`
- `remove_or_archive_experimental_output_materializer`

## My Recommendation

Start with **Goal4934 only**.

Do not implement a compiled writer yet.

The first concrete decision should be:

> Is the writer problem generic enough to belong in RTDL core?

If yes, immediately follow with Goal4935, because a serious materializer requires a generic row-buffer/data-shape contract first.

If no, stop the performance line. Keep the current RayJoin app correct, keep the generic grouping API only if it remains broadly useful, and do not burn time building an app-specific writer under a generic name.

## Expected Performance If The Plan Works

The realistic target is:

- writer: from `2.069s` toward `1.3s-1.6s`;
- total public-sample hot path: likely improve by `0.4s-0.8s`;
- full RayJoin public sample: may move from roughly `~6s` warmed runs toward `~5s`, depending on cache/state and remaining phases.

This is not the path to beat the author's fused C++/CUDA/OptiX implementation.

This is the path to build a reusable RTDL output pipeline that benefits RayJoin and at least one other spatial workload.

## What Would Be A Bad Plan

The following would repeat earlier mistakes:

- building a RayJoin-specific writer in RTDL core;
- hiding author output-chain semantics behind generic names;
- optimizing Python strings/dicts by small edits;
- claiming total elapsed speedup when cache state differs;
- skipping non-RayJoin proof;
- starting device-resident work without a stable row-buffer shape;
- starting Layer 2 numeric continuation without a fresh phase table showing it matters.

## Bottom Line

The correct next move is not "optimize harder." It is:

1. decide whether the remaining writer work is generic;
2. define the generic row-buffer/data-shape contract;
3. only then prototype a compiled/vectorized materializer;
4. require RayJoin byte-equality and non-RayJoin generality before any core promotion.

That is the disciplined version of the Layer 0-3 plan.
