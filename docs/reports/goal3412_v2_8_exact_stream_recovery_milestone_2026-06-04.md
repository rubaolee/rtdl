# Goal3412 - v2.8 Exact Stream Recovery Milestone

Date: 2026-06-04

Verdict: accept-with-boundary.

## Summary

Goals3401-3411 turn the OptiX exact pair-column bridge from a brittle one-shot
stream into a better-instrumented, caller-controlled recovery path:

- successful streams now report allocated exact-row capacity,
- overflowed streams fail closed and expose required capacity,
- callers can explicitly retry with that capacity,
- recovered exact streams feed generic grouped-count continuation,
- full `br_county.cdb` evidence exists for single-retry and windowed recovery.

This is a meaningful v2.8 runtime usability improvement, but it is still not a
native paged stream ABI or a device-only exact predicate.

## Goal Chain

| Goal | Result | Evidence |
| --- | --- | --- |
| 3401 | Fixed successful capacity metadata | 4096/full exact streams report exact rows, not point-by-shape capacity |
| 3402 | Claude review of 3401 | `accept-with-boundary` |
| 3403 | Added `PairColumnStreamCapacityStatus` | success/overflow status plus retry hint |
| 3404 | Proved explicit retry | overflow at 100, retry at 11316, exact pairs match |
| 3405 | Claude review of 3403 | `accept-with-boundary` |
| 3406 | Proved recovered stream grouped count | 4096 slice grouped counts match host |
| 3407 | Claude review of 3404 | `accept-with-boundary` |
| 3408 | Proved full-CDB recovered grouped count | full `br_county` grouped counts match host |
| 3410 | Documented chunked recovery gap | chunked streaming remains future work |
| 3411 | Proved windowed Python orchestration bridge | 9 windows, all recovered, full grouped counts match |

Goal3409 review of Goals3406/3408 was attempted, but Claude hit a session limit
before producing a review.

## Current Capability

For exact pair-column streams, a caller can now:

1. set a bounded capacity,
2. observe fail-closed overflow,
3. read `required_capacity` / `retry_capacity_hint`,
4. explicitly retry,
5. pass the recovered stream into a generic grouped-count continuation,
6. optionally use caller-visible point windows and merge grouped summaries by
   key addition.

## Full-CDB Evidence

| Path | Rows | Groups | Match |
| --- | ---: | ---: | --- |
| Single recovered stream | 47262 | 16476 | true |
| Windowed recovered stream | 47262 | 16476 | true |

Windowed evidence:

- window size: 2048
- windows: 9
- overflowed windows: 9
- retried windows: 9
- per-window grouped row sum: 16541
- final merged group keys: 16476
- missing/extra/mismatched groups: 0/0/0

The per-window grouped row sum is larger than the final group count because
group keys can appear in more than one window. The correct merge rule is
key-based addition, not concatenation under a disjoint-key assumption.

## Remaining Gap

The next native/runtime target is a real paged pair-column stream contract:

```text
prepare -> page_plan -> produce_page(page_index) -> consume_page -> release_page
```

Required properties:

- app-agnostic pair-column pages,
- stable original left/right ids,
- page-local capacity status,
- page ownership/lifetime rules,
- grouped continuations that consume or merge page summaries,
- fail-closed overflow at page and stream level,
- no hidden dispatch or automatic retry.

## Boundary

This milestone does not implement native paged streams, device-only exact
predicates, automatic retry, hidden dispatch, true zero-copy, public speedup
claims, RT-core speedup claims, RayJoin reproduction claims, or release
authorization.
