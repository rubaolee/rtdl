# Goal4953 RayJoin Binary Overlay Operator Contract

Date: 2026-07-04

Status: proposed_goal_pending_review

## Purpose

Goal4953 revises the immediate post-4952 direction.

The previous Goal4953 proposal was:

```text
Plain Writer Fine-Grained Phase Audit
```

That was useful for the paper-reproduction text-output path, but it is not the
right first goal for evaluating RTDL's real value as a spatial data language.

The corrected goal is:

> Define and measure RayJoin overlay as an intermediate RTDL operator:
> binary/columnar input, binary/columnar output, no author text writer.

This goal is a contract and measurement goal. It does not implement a new
high-performance operator yet.

## Why This Goal Exists

Recent evidence shows:

- RTDL's paper-reproduction Section 5.7 route is correct.
- The route is much slower than the author's C++/CUDA/OptiX implementation.
- The largest visible hot cost is the paper output-chain writer.
- The final file write is tiny, but writer structure/formatting is costly.
- PIP traversal is already tiny in prepared-hot mode.
- CPU/Numba path-split materialization was byte-equal but slower.

The key interpretation is:

> The paper-reproduction benchmark measures a sink workload: dumping a huge
> author-compatible text file. That is not the same as running overlay as a SQL
> intermediate operator.

In a database / query engine pipeline, overlay should normally produce binary
tuples or columnar batches that feed the next operator. It should not allocate
author text ids, format hundreds of thousands of lines, and write a paper answer
file unless the query actually ends at that sink.

Therefore, before building another writer optimization, RTDL must define the
binary intermediate operator it actually wants to be good at.

## Relationship To Previous Goals

- Goal4947-4948 proved generic row-buffer / Numba handoff capability.
- Goal4949 showed current Numba app helpers do not speed up RayJoin.
- Goal4950 closed Layer 1/2 as capability success but RayJoin performance no-go
  in the paper text-output workload.
- Goal4951 showed CPU/Numba generic path-split materialization is correct but
  slower for the text-output path.
- Goal4952 stopped the CPU/Numba materializer route and authorized only a
  measurement next step.

Goal4953 changes what should be measured first:

- not "how can we make the paper writer faster?";
- but "what is the cost of overlay before the paper writer, and what binary
  output contract should the next operator consume?"

This does not invalidate Goal4952. It sharpens it: the text writer can still be
audited later if the owner wants paper-output acceleration, but the RTDL product
question is the binary operator path.

## Scope

Allowed:

- define a binary/columnar overlay output contract for an intermediate operator;
- inspect the existing Section 5.7 route to identify the earliest correct
  pre-text output boundary;
- measure the public sample with the writer removed or bypassed where possible;
- classify which phases are currently Python/CPU versus RTDL primitive/native;
- identify which pieces can connect to existing Layer 1/2 row-buffer / Numba
  handoff;
- produce a go/no-go plan for a later device-resident reprojection/sort/binary
  overlay prototype.

Forbidden:

- no new native writer implementation;
- no device writer implementation;
- no public API exposure;
- no performance claim;
- no RayJoin paper text format in RTDL core;
- no hidden RayJoin-specific RTDL kernel;
- no claim that the binary operator is already optimized;
- no replacing the paper-reproduction correctness route.

## Binary Overlay Operator Contract To Define

Goal4953 must define a neutral intermediate representation for overlay output.

At minimum, the contract must answer:

1. **Granularity**
   - Is the output a row per overlay point?
   - A row per path segment?
   - A grouped row buffer: group/chain descriptors plus point items?

2. **Required columns**
   Candidate columns include:
   - `group_id` or `chain_id`;
   - `item_order`;
   - numeric `x`, `y`;
   - source chain id;
   - source edge id or interval id;
   - left/right face ids;
   - other-map face id;
   - validity / keep flag.

3. **Ownership**
   RTDL generic operator may own:
   - numeric columns;
   - grouping offsets/lengths;
   - primitive descriptor columns;
   - device/columnar row buffers.

   RayJoin app must own:
   - author text line format;
   - paper answer-file byte layout;
   - paper-specific id numbering if only needed for text output.

4. **Downstream consumption**
   The contract must show at least one plausible downstream operator shape:
   - count / aggregate;
   - filter by face id;
   - group by face pair;
   - spatial post-processing.

   This can be a design-level consumer; it does not need to be implemented in
   Goal4953.

## Measurement Required

Goal4953 must measure, on the public County x Soil sample:

1. current full paper-output route;
2. route with author text writer excluded or bypassed as much as possible;
3. pre-writer phases:
   - LSI rows;
   - reprojection;
   - sort;
   - vertex PIP;
   - midpoint generation;
   - midpoint PIP;
   - face assignment;
   - binary/grouped overlay row construction if currently present.

For each phase, classify:

- RTDL native / RT-core primitive;
- Python/CPU numeric processing;
- Python object/control-flow processing;
- output sink / text formatting;
- candidate for existing Layer 1/2 row-buffer handoff;
- candidate for future device-resident implementation.

## Required Answers

Goal4953 must answer:

1. If we remove the paper text writer, what is the current RTDL hot cost?
2. Which remaining phases are still Python/CPU?
3. Which of those phases are real operator work rather than final sink work?
4. Can current Layer 1/2 infrastructure directly help reprojection/sort/binary
   rows, or is additional infrastructure needed?
5. What is the smallest next implementation goal that would move the binary
   operator path?
6. Should the paper writer path be deprioritized as a reproduction-only sink?

## Exit Labels

Goal4953 must exit with exactly one of:

1. `binary_overlay_contract_ready__authorize_device_resident_reprojection_sort_goal`
   - The binary contract is clear.
   - Writer-bypassed measurement shows reprojection/sort/binary-row construction
     are meaningful operator costs.
   - Existing Layer 1/2 can plausibly be used as the next implementation base.

2. `binary_overlay_contract_ready__operator_cost_already_low__stop_rayjoin_perf_line`
   - Removing the writer leaves little operator cost to optimize, or the
     remaining costs are not RTDL-relevant.

3. `binary_overlay_contract_blocked__needs_correctness_boundary_work`
   - The app cannot produce a well-defined binary operator output without
     relying on paper text writer semantics.

4. `binary_overlay_contract_inconclusive_redo_measurement`
   - Measurement is too noisy or the writer boundary cannot be isolated.

## Review Gate Before Implementation

No implementation goal may start until Goal4953 is reviewed.

If Goal4953 exits through label 1, the likely next implementation goal is:

```text
Goal4954 Device-Resident Reprojection/Sort/Binary-Row Prototype
```

That future goal must:

- preserve byte-equivalent paper output when the binary rows are later passed to
  the existing app text sink;
- measure binary-operator speed separately from text writer speed;
- prove non-RayJoin genericity on at least one additional spatial pipeline shape.

## Decision Audit

This goal is not another looks-busy process document. It changes the benchmark
question.

Old question:

```text
Can RTDL dump the RayJoin paper answer file as fast as C++?
```

Correct RTDL product question:

```text
Can RTDL execute overlay as a binary intermediate spatial operator efficiently,
so downstream operators consume its output without a text writer?
```

The old question is dominated by Python-vs-C++ text/output mechanics. The new
question tests RTDL's actual architecture: RT primitives plus columnar,
device-resident, partner-capable data-flow.

## Requested Review Verdict

`approve_goal4953_binary_overlay_operator_contract`
