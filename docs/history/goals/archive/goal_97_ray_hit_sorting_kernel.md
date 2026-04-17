# Goal 97: Ray-Hit Sorting Kernel

## Objective

Use RTDL to implement and validate a non-join test program that sorts integers
through geometric hit counts.

This goal is meant to test RTDL outside the main spatial-join storyline while
still exercising the same core runtime/backend machinery:

- authored kernel lowering
- backend portability
- stable result semantics
- correctness comparison across backends

## Problem statement

Given a multiset of integers `x_i`, construct geometry as follows:

- for each integer `x_i`, create one vertical segment from `(x_i, 0)` to
  `(x_i, x_i)`
- for each integer `x_i`, cast one horizontal ray from `(0, x_i)` to `(F, x_i)`
  where `F` is at least `max(x_i)` and preferably a fixed value greater than
  the maximum input

Accepted implemented construction for the first round:

- build segment:
  - `(x_i, 0)` to `(x_i, x_i + 1)`
- probe segment:
  - `(0, x_i + 0.5)` to `(F, x_i + 0.5)`

This removes the `x = 0` degenerate endpoint ambiguity while preserving the
intended integer ordering law.

For a nonnegative integer `x_i`, the accepted implemented probe at height
`y = x_i + 0.5` intersects exactly those build segments whose endpoint height
is at least `x_i + 0.5`.

That means the ray-hit count is:

- number of values `x_j` such that `x_j >= x_i`

Those hit counts can then be used to derive a sorted order.

## First accepted scope

The first accepted scope is:

- nonnegative integers only
- duplicates allowed
- integer-only inputs
- sorting by hit-count-derived rank

Negative integers are deferred unless the construction is shifted by an
explicit offset. They should not be silently mixed into the first accepted
claim surface.

## Expected sorting semantics

For input values `x_i`:

- larger numbers produce smaller hit counts
- smaller numbers produce larger hit counts
- sorting by:
  - increasing hit count gives descending numeric order
  - decreasing hit count gives ascending numeric order

Duplicates are expected to produce equal hit counts.

So the accepted output should be:

- a stable sorted multiset
- or a `(value, hit_count)` table plus a deterministic secondary tie rule

The preferred first contract is:

- output `(value, hit_count, original_index)`
- derive:
  - ascending stable sort by `(-hit_count, original_index)`
  - descending stable sort by `(hit_count, original_index)`

## Backend scope

Target backends:

- Python reference/oracle
- native C oracle where practical
- Embree
- OptiX
- Vulkan

PostGIS is not the natural primary oracle for this goal, because the target is
not a spatial-join benchmark claim. It may still be used as a supporting
checker if it helps, but the main trust path should be the RTDL oracles and
cross-backend parity.

## Test matrix

Required input sizes:

- empty input
- single-element input
- small hand-written vectors
- duplicate-heavy vectors
- already sorted vectors
- reverse-sorted vectors
- random vectors
- larger vectors up to at least `10k` integers

Required value families:

- all zeros
- strictly increasing
- strictly decreasing
- repeated plateaus
- mixed sparse nonnegative integers

## Acceptance

Goal 97 is done when:

- the problem is implemented as an RTDL program/kernel family
- the sorting semantics are explicit and deterministic
- the accepted backends produce parity-clean `(value, hit_count)` outputs on the
  accepted nonnegative test matrix
- the package clearly states whether it is:
  - a correctness/demo goal only
  - or also a backend-scaling/performance goal

The initial honest target should be:

- correctness and portability first
- performance only as a secondary observation
