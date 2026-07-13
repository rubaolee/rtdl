# Goal4909 — Compiled Output-Chain Descriptor Plan

Date: 2026-07-03

## Verdict Requested

`approve_goal4909_compiled_descriptor_implementation_gate`

## Why This Goal Exists

Goal4907 produced a real writer win:

```text
writer: 2.674s -> 1.946s
hot body: 4.765s -> 4.013s
byte_equal: true
```

Goal4908 then tested a tempting Python fast path and rejected it:

```text
writer: 1.946s -> 2.222s
hot body: 4.013s -> 4.527s
byte_equal: true
verdict: negative; keep Goal4907
```

So the next writer work must not be another Python micro-fast-path. It must
either:

1. move real descriptor construction into a compiled partner path, or
2. stop the writer line and switch to cold/setup optimization.

This goal chooses (1), but only behind an explicit bar and kill condition.

## One-Line Goal

Build a compiled output-chain descriptor path that reduces Python chain-loop
bookkeeping while preserving the exact AuthorOfficial output contract.

## What "Compiled Descriptor" Means Here

It does **not** mean:

- moving RayJoin overlay semantics into RTDL core;
- adding an RTDL-native RayJoin writer kernel;
- changing LSI/PIP primitive behavior;
- changing output format;
- caching the final output.

It means:

```text
Python/RDTL primitives produce LSI/PIP rows as before
Numba receives app-layer arrays and computes compact chain descriptors
Python uses descriptors to perform final exact point-id assignment and text emit
```

The compiled partner path may compute:

- which output-chain fragments exist;
- fragment start/end point ranges for no-intersection runs;
- where intersection split fragments occur;
- left/right/other face ids for emitted fragments;
- counts needed for preallocation or low-branch emission.

The first implementation should not attempt to make Numba emit final text. Text
formatting and final byte-for-byte output remain in Python until the descriptor
is proven.

## Inputs Available To The Descriptor

From existing public primitive/app-layer route:

- dataset chain offsets and point counts;
- chain left/right face ids;
- point x/y arrays;
- point-location faces;
- sorted intersection rows, converted to compact arrays:
  - edge id on this map;
  - display x/y;
  - midpoint face for this map;
  - paired edge id for debug/reference if needed;
- existing Numba skip plan:
  - has_xsects;
  - terminal_keep;
  - skip_chain.

The descriptor must not import `rtdsl.rayjoin_overlay`.

## Proposed Implementation Shape

### Step 1 — Descriptor Arrays

Add Numba functions to:

```text
history/internal_docs/goal4886_rayjoin_numba_overlay_kernels.py
```

Initial descriptor schema:

```text
fragment_chain_index[int64]
fragment_map_index[int8]
fragment_kind[int8]          # normal, before_mid, mid_segment, after_last
point_start[int64]           # inclusive original point index if range-backed
point_stop[int64]            # exclusive original point index if range-backed
left_face[int64]
right_face[int64]
other_face[int64]
xsect_start[int64]           # index into sorted xsect arrays, or -1
xsect_stop[int64]
```

The descriptor is allowed to be conservative. It may initially only handle
no-intersection kept chains and simple single-intersection chains if it records
fallback counts honestly. But the success bar below only counts emitted output
that preserves byte equality.

### Step 2 — Python Emit From Descriptor

Modify only:

```text
history/internal_docs/goal4886_section57_public_primitives_overlay_numba_harness.py
```

Python still:

- assigns face ids in first-seen order;
- assigns point ids in first-seen order;
- formats exact output lines;
- verifies byte equality.

But Python should loop over compact descriptors, not re-run the full per-point
overlay state machine where descriptors cover the same logic.

### Step 3 — Measured Gate

Run the same Goal4904 prepared LSI+PIP replay probe:

```text
Australia representative
AuthorOfficial comparator
repeat=2
prepared-hot repeat1 is the comparison row
```

## Acceptance Bar

The implementation is a success only if all are true:

| Item | Required |
|---|---|
| byte equality | `true`, SHA `a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e` |
| writer time | `< 1.50s` on prepared-hot repeat1 |
| hot body | `< 3.60s` on prepared-hot repeat1 |
| RTDL core/native changes | none |
| claim boundary | app-layer / partner descriptor only |

If the writer improves but misses `<1.50s`, classify:

```text
partial_descriptor_win
```

If byte equality fails:

```text
fail_correctness_redo_or_revert
```

If writer is not faster than Goal4907:

```text
negative_descriptor_result_stop_writer_microline
```

## Why This Is The Right Next Step

Goal4905 proved file I/O is not the bottleneck.

Goal4907 proved duplicate point/display lists and repeated formatting were real
but only partially removable.

Goal4908 proved Python-side no-xsect fast paths are not enough and can make the
route slower.

Therefore the only remaining writer path worth testing is a real compiled
descriptor path. If this also underdelivers, the writer line should stop and the
project should move to cold/setup or longer-term data-flow fusion work.

## What This Must Not Become

This must not become a hidden RayJoin kernel in RTDL. It is a paper-reproduction
application continuation using Numba as a partner.

The acceptable boundary is:

```text
RTDL core: generic LSI + generic planar-map point-location
App layer: RayJoin Section 5.7 output-chain contract
Partner: Numba helps compute app-layer descriptors
```

## Review Questions To Resolve Before Implementation

1. Is this a real compiled descriptor plan rather than another Python
   micro-fast-path?
2. Is the `<1.50s` writer bar appropriate after Goal4907's `1.946s` and Goal4908
   negative result?
3. Is it acceptable that this remains app-layer paper-reproduction engineering,
   not RTDL primitive acceleration?
4. Is the boundary against RTDL core/native RayJoin-specific code clear enough?
5. Should the first implementation be conservative, or must it attempt full
   descriptor coverage immediately?

## Non-Authorization

This plan does not authorize:

- RTDL core/native RayJoin-specific kernels;
- public performance claims;
- full Section 5.7 performance claims;
- changing comparator/correctness rules;
- hiding a negative result;
- V3/V4 release resurrection.
