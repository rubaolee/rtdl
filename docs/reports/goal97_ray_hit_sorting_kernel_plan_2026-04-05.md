# Goal 97 Plan: Ray-Hit Sorting Kernel

Date: 2026-04-05
Status: implemented locally

## Core formulation

Accepted implemented construction:

- build segment: `(x_i, 0) -> (x_i, x_i + 1)`
- probe segment: `(0, x_i + 0.5) -> (F, x_i + 0.5)` with `F > max(x_i)`

Expected hit-count law:

- `hit_count(x_i) = |{ x_j : x_j >= x_i }|`

## Preferred output contract

Emit:

- `value`
- `hit_count`
- `original_index`

Then define:

- ascending stable order by `(-hit_count, original_index)`
- descending stable order by `(hit_count, original_index)`

## First implementation priorities

1. Python/oracle implementation
2. RTDL kernel mapping
3. backend parity on available small and medium vectors
4. larger input smoke up to `10k`

## Explicit non-goals for the first round

- negative integer support without an explicit offset construction
- release-level performance claims
- using this goal to replace the existing RayJoin-style trust anchor
