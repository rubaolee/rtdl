# Goal4954 Binary Overlay Operator Pre-Fusion Program

Date: 2026-07-04

Status: proposed_goal_pending_review

## Purpose

Goal4954 defines the next implementation program after the owner approved the
correct boundary:

> Do all practical Layer 1/2/3 binary overlay operator work before Layer 4
> traversal-side fusion.

This goal explicitly excludes Layer 4.

It is not a paper text-writer optimization goal. It is the program to make
RayJoin overlay behave like a real RTDL spatial dataflow operator:

```text
binary/columnar input
-> RTDL primitives
-> columnar/device-resident continuation where possible
-> binary/columnar overlay output
-> downstream operator
```

The paper text writer remains only as a correctness anchor.

## Non-Goal: Layer 4 Fusion

Goal4954 does **not** authorize:

- raw OptiX callbacks;
- any-hit / closest-hit user callback exposure;
- traversal-side code injection;
- Numba PTX injection into OptiX traversal;
- in-traversal fusion compiler;
- app-specific RayJoin kernels hidden in RTDL core.

If, after Goal4954's work, the remaining gap is traversal/fusion-bound, that
becomes a later Layer 4 R&D decision. It is outside this goal.

## System Invariant: RTDL Is Generic; RayJoin Is An App

Goal4954 is valid only if it preserves this invariant:

> RTDL is a general spatial dataflow system. RayJoin is one application and one
> stress test running on top of RTDL.

This invariant is not optional wording. It is a hard gate for every subgoal.

### What RTDL Core May Own

RTDL core/runtime may own only generic mechanisms:

- columnar/device-resident row buffers;
- generic numeric columns and grouped-row carriers;
- generic spatial operator outputs such as segment-pair ids, point-location
  labels, descriptors, offsets, lengths, and keep masks;
- generic continuation and partner handoff infrastructure;
- generic columnar transforms such as map, filter, sort, group, reduce, gather,
  scatter, and descriptor joins;
- generic binary output carriers that another non-RayJoin spatial pipeline can
  consume.

Any new core/runtime feature must be explainable without naming RayJoin,
Section 5.7, AuthorOfficial, CDB text output, output chains, or paper-specific
formatting.

### What RayJoin App May Own

The RayJoin paper-reproduction app may own application adaptation:

- CDB loading and paper dataset conventions;
- mapping RayJoin polygon-map fields into generic RTDL columns;
- AuthorOfficial comparison and public-sample correctness checks;
- paper text writer and byte-for-byte output formatting;
- app-level reconstruction from generic binary rows into the paper output sink;
- RayJoin-specific reporting and reproduction metadata.

These pieces must stay in the RayJoin app/reproduction layer. They must not be
promoted into RTDL core as hidden app semantics.

### Hard Promotion Gate

A feature may move from RayJoin app code into RTDL generic infrastructure only
after it passes all of the following:

1. It has a generic name and generic schema.
2. It can be described as a spatial/dataflow primitive without RayJoin identity.
3. It has a non-RayJoin consumer or test that uses the same mechanism.
4. It does not encode paper text output or AuthorOfficial comparison behavior.
5. It preserves correctness on the RayJoin paper line when adapted by the app.

If a feature fails this gate, it may still be useful, but it remains app-owned
and cannot be counted as RTDL language/runtime progress.

## What Problem This Solves

The previous paper-reproduction performance line measured a sink workload:

```text
overlay -> author-compatible giant text file
```

That benchmark is useful for correctness, but it is a poor measure of RTDL's
operator value. The text writer is mostly Python/C++ string and app-format work,
not RT/GPU work.

The correct product question is:

```text
Can RTDL run overlay as a binary intermediate operator efficiently?
```

That requires removing the writer from the performance question and making the
operator's intermediate data columnar, binary, and consumable by downstream
operators.

## Evidence We Must Preserve

Known facts:

- RTDL Section 5.7 paper route is byte-correct on the public sample.
- Current fastest paper-output route is still much slower than the author.
- Current paper writer is about `2.58s`.
- Final file write is tiny, around `0.04s`.
- Prepared-hot PIP traversal is tiny, around `0.02s`.
- After removing writer, remaining overlay compute is still large, roughly:
  - LSI rows: `~1.18s`;
  - reprojection: `~0.73s`;
  - sort: `~0.80s`;
  - plus preparation/session and app control costs.
- This remaining operator cost is still much larger than the author's overlay
  compute path.

Therefore:

> Removing the writer isolates the real compute gap; it does not close it.

## Required Framing

Goal4954 must maintain two separate lines:

### 1. Paper Reproduction Line

Purpose:

- byte-for-byte correctness;
- compatibility with AuthorOfficial/public answers;
- evidence trail for Section 5.2/5.3/5.7 reproduction.

The paper writer remains here.

### 2. Binary Operator Line

Purpose:

- performance/value benchmark for RTDL as a spatial dataflow language;
- binary/columnar intermediate output;
- no author text writer in the hot metric;
- downstream operator consumes the overlay output.

The binary line is where Layer 1/2/3 optimization belongs.

## Program Tasks

### Task 1: Binary Overlay Contract

Define the operator output schema.

Minimum required columns:

- group/chain id;
- item order;
- numeric `x`, `y`;
- source chain id;
- source edge or interval id;
- left/right face ids;
- other-map face id;
- validity / keep flag;
- grouping offsets or lengths.

The schema must be generic enough that another spatial pipeline could consume
it. It must not encode the paper text-output format.

The schema must also pass the System Invariant: if the schema requires RayJoin
identity to make sense, it is an app schema, not an RTDL operator contract.

### Task 2: Writer-Free Measurement

Measure the public sample with the paper writer excluded.

Required phase table:

- LSI rows;
- reprojection;
- sort;
- vertex PIP;
- midpoint generation;
- midpoint PIP;
- face assignment;
- binary/grouped overlay row construction;
- downstream consumer.

Required comparison:

- compare against author overlay compute, not author text dump;
- explicitly state the remaining compute gap.

### Task 3: Device/Columnar Reprojection And Sort Plan

Identify how to move reprojection and sort out of Python objects.

Allowed implementation paths:

- NumPy/CuPy/Numba columnar kernels;
- existing row-buffer/device-column handoff;
- native helper only if generic and reviewed.

Forbidden:

- RayJoin-specific kernel in RTDL core;
- paper text writer in core;
- traversal-side fusion.

### Task 4: Binary Row Construction

Build or plan construction of binary overlay rows without author text formatting.

The output should be columnar or grouped-row-buffer style, suitable for a
downstream operator.

This task may use app-owned mapping from RayJoin state to generic columns, but
RTDL generic infrastructure must remain app-agnostic.

If binary row construction needs RayJoin-specific fields, those fields must live
in an app adapter layered on top of generic RTDL columns. They cannot define the
core carrier schema.

### Task 5: Downstream Consumer

Define and, if authorized by subgoal review, implement a simple downstream
consumer.

Valid consumer examples:

- count rows by face pair;
- filter by face id;
- group by overlay face pair;
- compute a small aggregate over binary rows.

The consumer must consume binary/columnar rows. It must not parse paper text.

### Task 6: Performance Readout

Produce a final table with:

- paper-output route time;
- writer-free binary operator route time;
- downstream-consumed binary route time;
- author overlay compute reference;
- remaining gap;
- classification of remaining gap:
  - Layer 1/2/3 still actionable;
  - or likely Layer 4 fusion-bound.

## Subgoal Sequence

### Goal4954-A: Contract And Measurement Plan

Deliver:

- binary schema;
- exact phase measurement plan;
- author overlay-compute comparator definition;
- downstream consumer choice.
- explicit System Invariant check showing which pieces are RTDL-generic and
  which pieces are RayJoin-app-owned.

Exit:

- `binary_overlay_contract_measurement_plan_ready`
- or `binary_overlay_contract_blocked`

### Goal4954-B: Writer-Free Baseline Measurement

Deliver:

- public sample writer-free phase table;
- paper route vs binary route split;
- remaining compute gap against author overlay compute.

Exit:

- `writer_free_measurement_ready_for_device_columnar_work`
- or `writer_free_measurement_invalid_redo`

### Goal4954-C: Columnar Reprojection/Sort Prototype

Deliver:

- reprojection/sort moved from Python object lists toward columnar/partner path;
- correctness check by reconstructing paper output through existing sink;
- performance table for binary route.
- non-RayJoin proof, or a recorded reason why the prototype remains app-owned
  and must not be promoted.

Exit:

- `columnar_reprojection_sort_win_continue`
- `columnar_reprojection_sort_correct_but_not_faster_stop`
- `columnar_reprojection_sort_wrong_reject`

### Goal4954-D: Binary Row Construction And Consumer

Deliver:

- binary/grouped overlay rows;
- downstream consumer over binary rows;
- no paper text parse;
- correctness link back to paper route.
- proof that the consumer uses generic binary rows, not RayJoin paper text or
  RayJoin-only hidden fields.

Exit:

- `binary_overlay_consumer_pipeline_proven`
- or `binary_overlay_consumer_pipeline_blocked`

### Goal4954-E: Pre-Fusion Decision

Deliver:

- final pre-fusion performance summary;
- remaining gap classification;
- decision whether Layer 4 is necessary.

Exit:

- `pre_fusion_layers_deliver_product_value_continue_productization`
- `pre_fusion_layers_exhausted_defer_to_layer4_decision`
- `binary_operator_line_not_useful_stop`

## Review And Governance

Each subgoal requires review before the next opens.

Antigravity review is required for every subgoal.
Claude review is required for:

- Goal4954-A;
- Goal4954-E;
- any decision that opens native code or public API.

Review debt is allowed only when a reviewer is unavailable, but must be recorded.

## Success Criteria

Goal4954 succeeds if it produces:

1. a clear binary overlay operator contract;
2. writer-free measurements;
3. at least one real binary downstream consumer;
4. evidence that Layer 1/2/3 improvements either:
   - materially reduce the binary operator cost; or
   - are insufficient, leaving a clearly classified Layer 4 fusion gap.
5. proof that any RTDL-core contribution remains generic, with RayJoin-specific
   behavior confined to the RayJoin paper-reproduction app.

It does not need to match the author's sub-second performance. Matching that may
require Layer 4, which is explicitly outside this goal.

## Failure Criteria

Goal4954 fails or stops if:

- the binary output cannot be defined without paper text semantics;
- the binary route is not meaningfully different from the paper writer route;
- the downstream consumer still depends on parsing text output;
- improvements require app-specific RTDL core logic;
- all non-fusion work is exhausted and the remaining gap is clearly Layer 4.

## Owner-Facing Summary

This goal means:

> Build the RTDL value case before Layer 4: overlay as a binary intermediate
> operator, not as a text-dumping paper app.

If this succeeds, RTDL gains a credible spatial dataflow operator story.
If this fails, the remaining author-performance gap should be classified as
requiring Layer 4 fusion rather than more Python/Numba wrapper work.

## Requested Review Verdict

`approve_goal4954_binary_overlay_pre_fusion_program`
