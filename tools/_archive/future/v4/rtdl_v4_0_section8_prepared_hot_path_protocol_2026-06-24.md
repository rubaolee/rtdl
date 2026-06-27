# RTDL V4.0 Section 8 Revised Protocol: Prepared Hot Path

Date: 2026-06-24
Status: revised protocol after Claude backfill review; not a release claim

## Purpose

The original Section 8 whole-call route gate failed because the compact summary route paid prepared-scene setup inside every measured app call. A phase profile showed the prepared-session hot path may be materially faster than row materialization. This protocol tests that narrower question without changing the numeric bar:

> Once the fixed-radius count-threshold scene is prepared, does the compact summary hot path beat the separated row emit+reduce path by at least 1.5x on serious sizes?

## Timing Boundary

Excluded from timed windows:

- case construction
- oracle construction and comparison
- prepared scene creation

Included in timed windows:

- rows baseline: OptiX neighbor-row emit plus Python `reduce_rows(count)` conversion into density rows
- summary candidate: prepared native fixed-radius count-threshold query plus Python conversion from compact count rows into density rows

## Sizes And Repeats

- copies: 8192, 32768, 131072
- warmup: 1 hot-path call per route
- repeats: 7 measured hot-path calls per route
- statistic: median wall time

## Correctness Gate

For every serious size:

- rows result must match the exact tiled oracle
- summary result must match the exact tiled oracle
- point count and outlier count must match

Any correctness failure kills the experiment.

## Performance Gate

The revised summary hot-path gate passes only if:

- summary hot path speedup over rows emit+reduce is at least 1.5x on at least two serious sizes; and
- the candidate uses the generic fixed-radius count-threshold continuation, not an app-identity kernel.

The gate level is unchanged from the original Section 8 protocol. Only the timing boundary changes.

## Claim Boundary

Passing this protocol may authorize only:

```text
For a prepared fixed-radius count-threshold scene, the compact summary hot path
beats the separated neighbor-row emit+reduce path on the measured fixture and
hardware.
```

It does not authorize:

- V4 release
- broad V4 speedup wording
- broad V3-over-V2 wording
- near hand-written OptiX wording without an independent Route D
- Tier-3 callback claims
- app-specific native engine claims

## Harness

Use:

```bash
PYTHONPATH=src:. python scripts/v4_section8_prepared_hot_path_validation.py --dry-run
```

For the pod run:

```bash
PYTHONPATH=src:. python scripts/v4_section8_prepared_hot_path_validation.py \
  --copies 8192 --copies 32768 --copies 131072 \
  --repeat 7 --warmup 1 \
  --progress \
  --json-out docs_or_tmp_v4_section8_prepared_hot_path_result.json
```

The result and this protocol require external review before any summary route credit or Tier-2 primitive promotion.

