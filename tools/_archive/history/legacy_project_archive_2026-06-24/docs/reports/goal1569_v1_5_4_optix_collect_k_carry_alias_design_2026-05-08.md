# Goal 1569: collect-k carry-copy elimination design

## Verdict

Carry-copy elimination is the next plausible optimization target for odd tile
counts, but it is not a safe one-line pointer alias in the current fastest
OptiX path.

The accepted path uses derived level descriptors:

```text
current_base = current_rows.front()
segment N address = current_base + N * segment_capacity * row_width
```

This requires all segments for the next merge level to be physically
contiguous in the active staging buffer. A carry segment from the previous
level may live in the other staging buffer or at a smaller segment stride. If
we simply push the old carry pointer into `next_rows`, the next derived
descriptor level can compute the wrong address.

## Measured Motivation

Goal 1568 shows that `65537` candidates still spend about `0.035588 ms` in five
carry copies, or `12.6%` of total time. The `131072` case has no carry copies,
so this is specifically an odd-tile optimization.

## Current Code Shape

The carry copy currently does two things:

- copies the carried row segment into the next level's contiguous output stage;
- when device-level counts are active, copies the carry count from
  `current_counts_level_device` into `next_counts_level_device`.

This maintains the derived-descriptor invariant for the next merge level.

## Unsafe Shortcut

Do not replace:

```text
cuMemcpyDtoD(carry_output, current_rows.back(), ...)
next_rows.push_back(carry_output)
```

with:

```text
next_rows.push_back(current_rows.back())
```

while leaving the derived-descriptor kernels unchanged. That would preserve the
host vector but break the device-side address calculation in later merge
levels.

## Viable Designs

### Design A: Pointer Descriptor Mode For Odd Levels

Use the existing non-derived descriptor arrays, or a new persistent device
segment-pointer array, for levels that contain aliased carry segments. This
allows `current_rows[i]` to point anywhere.

Pros:

- avoids copying carry row data;
- preserves exact row contents and ordering;
- localized to odd levels.

Cons:

- the current non-derived path uploads pointer/count descriptors and may give
  back the metadata savings that the derived-descriptor path achieved;
- a new persistent device descriptor array would need careful update and
  profiling.

### Design B: Carry Alias Flag Plus Mixed Addressing Kernel

Extend the derived level kernels to accept one optional carry pointer/count for
the last segment when `current_segments` is odd. Even-indexed merge pairs still
use `current_base`; the unpaired carry segment is carried forward as metadata
without row copy.

Pros:

- keeps most derived descriptor benefits;
- targets only the odd carry segment.

Cons:

- the next level may merge the carried segment with a normal contiguous segment,
  so mixed addressing can propagate beyond one level;
- complexity grows unless the whole level representation becomes descriptor
  based.

### Design C: Ping-Pong Layout Reservation

Reserve the carry segment's next-level physical slot in the output stage before
the level runs, so no post-merge copy is needed.

Pros:

- preserves derived descriptors after the level;
- avoids the explicit carry copy.

Cons:

- still requires writing the carry segment into the destination slot at some
  point unless the previous stage had pre-positioned it;
- likely shifts copy work earlier rather than removing it.

## Recommended Next Diagnostic

Start with Design A as a diagnostic-only experiment:

- use pointer descriptors only for odd levels with a carry segment;
- keep even levels on the derived-descriptor path;
- keep the carry count copy, even if the row-data copy is removed;
- measure pointer-array upload cost separately from saved row-copy cost;
- switch both materialize and compact kernels to pointer-descriptor variants
  for the odd level;
- measure whether removing `carry_copy_ms` beats the extra descriptor handling;
- test `65537` first because it has five carries;
- include `131072` as a regression guard because it should not use the carry
  alias path.

Do not promote any carry-alias path unless it preserves parity and improves the
accepted `65537` long case without regressing the no-carry `131072` case.

This design is diagnostic only and does not authorize public speedup wording.

## External Review

Claude reviewed this design on 2026-05-08 and agreed that the derived-descriptor
contiguity invariant is real. The review also identified implementation
caveats that must be preserved:

- Design A removes row-data carry copies, not carry count copies.
- Pointer-array upload cost must be measured explicitly.
- Pointer-descriptor materialize and compact variants must be switched
  together for odd levels.
- Odd-level pointer output still writes into the normal output stage, so the
  following level can return to derived descriptors after the carry is no
  longer aliased.

Review artifact:
`docs/reports/goal1569_claude_carry_alias_design_review_2026-05-08.md`.
