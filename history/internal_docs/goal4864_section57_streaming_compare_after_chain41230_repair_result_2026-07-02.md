# Goal4864 Result: Section 5.7 Streaming Compare After Chain 41230 Repair

Date: 2026-07-02

## Purpose

Run exactly one Section 5.7 County x Zipcode streaming compare after the
Goal4863 chain `41230` midpoint-contract repair.

This was a correctness check only.  It was not a performance run.

## Result

Evidence file:

- `history/internal_docs/goal4864_after_chain41230_streaming_compare_summary.json`

Result:

```json
{
  "elapsed_sec": 476.471871137619,
  "stream_match": false,
  "first_diff": {
    "line": 499960,
    "author": "-144.125743 64.796193",
    "rtdl": "-144.125743 64.796192"
  }
}
```

## What Improved

The previous first difference was:

```text
line 123678
author: 41230 2 42104 42105 280 290
rtdl:   41230 2 42104 42105 294 295
```

After Goal4863, the compare passed beyond that location.

Therefore the chain `41230` midpoint face-selection repair worked.

## New First Difference

Author output context:

```text
-144.121999 64.800915
166684 2 172573 172574 1928 1929
-144.121999 64.800915
-144.127807 64.799108
166685 2 172574 172575 1928 1929
-144.127807 64.799108
-144.125743 64.796193
166686 2 172575 172576 1926 1927
-144.125743 64.796193
-144.123679 64.793277
166687 2 172576 172577 1926 1927
```

The new first difference is a coordinate line:

```text
author: -144.125743 64.796193
rtdl:   -144.125743 64.796192
```

This is a one-unit difference in the sixth decimal place for the Y coordinate.
The surrounding headers and point ids show that the differing coordinate is the
shared point `172575`, used by chains `166685` and `166686`.

## Classification

This is no longer the chain `41230` face-assignment bug.

Current best classification:

- output coordinate materialization / unscale / decimal formatting mismatch;
- likely scaled-internal-to-double-to-`%.6f` rounding boundary;
- not LSI row-count;
- not vertex PIP;
- not midpoint face-id assignment;
- not a performance issue.

## Inefficiency Note

This full streaming compare was justified once after the targeted chain fix. It
should not become the new debug loop.

The next goal should start with a small coordinate formatting / unscale
diagnostic for point `172575`, not another full Section 5.7 run.

## Recommended Next Goal

**Goal4865: output coordinate rounding / unscale diagnostic for point 172575**

The goal should:

1. identify the internal scaled coordinate that generates point `172575`;
2. compare AuthorPatch unscale and formatting against RTDL unscale and
   formatting;
3. create a small synthetic regression for sixth-decimal rounding boundaries;
4. repair generic author-compatible coordinate output formatting if needed;
5. only then run one additional streaming compare.

## Claim Boundary

Authorized:

- chain `41230` no longer blocks the streaming compare;
- the next blocker is coordinate output rounding at line `499960`.

Not authorized:

- Section 5.7 byte-equal correctness;
- Section 5.7 performance;
- broad RayJoin paper reproduction;
- broad RTDL correctness or performance.
