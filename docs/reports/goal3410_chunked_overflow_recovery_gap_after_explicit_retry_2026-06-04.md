# Goal3410 - Chunked Overflow Recovery Gap After Explicit Retry

Date: 2026-06-04

Verdict: needs-more-evidence for chunked streaming recovery.

## Context

Goals 3403, 3404, 3406, and 3408 close the explicit retry path:

1. A bounded pair-column stream fails closed.
2. The runtime exposes `required_capacity` and `retry_capacity_hint`.
3. The caller explicitly retries with that capacity.
4. The recovered exact stream can feed generic grouped-count continuation.

This is useful, but it is not chunked streaming recovery. If
`required_capacity` itself is too large for one device allocation, explicit retry
still cannot complete.

## Current Delivered Contract

Delivered:

- `PairColumnStreamCapacityStatus`
- fail-closed overflow
- no partial rows on overflow
- explicit retry hint
- recovered stream grouped-count continuation
- slice and full `br_county.cdb` evidence

Not delivered:

- paged exact relation streams
- chunked exact row emission
- multi-page grouped-count continuation
- device-only exact predicate
- page-token or cursor ABI
- automatic retry

## Why Existing Chunked Candidate Append Is Not Enough

Goal3187 chunked the segment-pair candidate launcher by appending multiple native
launches into the same bounded output columns. That works when each launch can
append into a pre-sized buffer and the producer can preserve a global row
counter.

The exact closed-shape bridge is different:

- It currently computes exact rows through the host-refined path.
- It only uploads exact rows after the exact count is known.
- Overflow means the caller's output capacity was too small for exact rows.
- Retrying with `required_capacity` still requires one allocation large enough
  for every exact row in the requested point window.

So Goal3187's append shape is relevant, but it does not solve exact-stream
overflow by itself.

## Required Future Contract

A real chunked recovery contract should be generic and explicit:

| Piece | Required behavior |
| --- | --- |
| Page plan | caller-visible page/window metadata before or during execution |
| Page producer | produces bounded pair-column pages without exposing partial rows as complete |
| Stable keys | preserves original left/right ids across pages |
| Continuation | grouped reductions can consume one page at a time or merge page summaries |
| Overflow policy | fail closed per page and for the whole stream |
| Claim boundary | no hidden dispatch, no automatic retry, no true-zero-copy claim |

## Practical First Slice

The safest next engineering slice is a Python-level explicit windowed recovery
probe for grouped count:

1. Partition the left input into caller-visible point windows.
2. For each window, call `exact_device_columns(window_points, max_rows=window_bound)`.
3. If a window overflows, use that window's `retry_capacity_hint` explicitly.
4. Run grouped count on each recovered page.
5. Merge group summaries only because the left-id windows are disjoint.

This would prove the orchestration policy, not a native streaming ABI. It should
be labelled as a bounded Python orchestration bridge.

## Native Graduation Target

The native graduation target is a generic paged pair-column stream:

```text
prepare -> page_plan -> produce_page(page_index) -> consume_page -> release_page
```

The page producer must remain app-agnostic and expose only generic pair-column
fields, capacity status, page index, total pages if known, and stable id columns.

## Boundary

This report does not implement chunked overflow recovery. It records the gap and
the next safe implementation path. It does not authorize release, public speedup,
RayJoin reproduction, RT-core speedup, true zero-copy, hidden dispatch, automatic
retry, or app-specific native-engine behavior.
