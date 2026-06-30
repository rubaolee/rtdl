# Goal 97 External Variant Task

Write a compact single-file RTDL program for Goal 97 in exactly one target file.

## Problem

Given a multiset of nonnegative integers `x_i`, build geometry:

- build segment:
  - `(x_i, 0)` to `(x_i, x_i + 1)`
- probe segment:
  - `(0, x_i + 0.5)` to `(F, x_i + 0.5)`

where `F > max(x_i)`.

For each input value `x_i`, the probe intersects exactly those build segments
whose values satisfy `x_j >= x_i`.

That means:

- `hit_count(x_i) = number of values x_j such that x_j >= x_i`

Use those hit counts to derive:

- ascending stable sort by `(-hit_count, original_index)`
- descending stable sort by `(hit_count, original_index)`

Duplicates are allowed. Stable ordering must preserve `original_index`.

## Required implementation shape

- single file only
- use RTDL directly
- compact style
- include:
  - RTDL kernel
  - case construction
  - hit-count derivation
  - ascending/descending reconstruction
  - verification against Python `sorted(...)`
  - small `__main__` demo

## Scope

- nonnegative integers only
- correctness/demo only
- no performance claims

## Output rules

- write code only to the exact target file path given in the prompt
- do not modify any other files
- do not write docs
- do not write tests
- do not publish or push

## Example accepted backend default

- `cpu_python_reference`

Other backends may be supported optionally, but the file must work at least with
`cpu_python_reference`.
