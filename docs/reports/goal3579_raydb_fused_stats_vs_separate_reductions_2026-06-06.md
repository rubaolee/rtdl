# Goal3579 RayDB Fused Stats vs Separate Reductions

Date: 2026-06-06

## Purpose

Goal3579 documents the practical user-facing lesson from Goals3575 and 3578:
when a columnar grouped aggregate needs `count`, `sum`, `min`, and `max`
together, the correct RTDL contract is the fused generic `stats` reduction,
not four separate grouped reductions.

This is a primitive-choice packet. It does not add a new native ABI and does
not authorize public speedup claims.

## Evidence Source

This packet uses the current-head A5000 isolated-mode artifacts from Goal3578:

`docs/reports/goal3578_raydb_grouped_i64_mode_reprobe_current_a5000/*.json`

Configuration:

| Field | Value |
| --- | --- |
| GPU | RTX A5000 |
| commit | `1bde04f7` |
| backend | `optix_partner_resident_experimental` |
| row count | `960000` |
| warmup | `3` |
| repeat | `5000` |

## Result

Separate medians:

| Mode | Median sec |
| --- | ---: |
| `count` | 0.000443520956 |
| `sum` | 0.000502159353 |
| `min` | 0.000458555296 |
| `max` | 0.000489640050 |

Total separate median time:

`0.001893875655` seconds

Fused median:

| Mode | Median sec |
| --- | ---: |
| `stats` | 0.000525371637 |

Ratio:

`separate_count_sum_min_max / fused_stats = 3.604830411x`

## Interpretation

The fused `stats` contract returns the same grouped summary family in one
native launch:

- `count`;
- `sum`;
- `min`;
- `max`.

For this RayDB-style columnar aggregate fixture, using the fused contract is
the right user-level recommendation when all four outputs are needed. The
separate modes remain useful for single-output queries and for diagnostic
isolation, but they are not the recommended implementation of a full grouped
summary.

## Boundary

This packet records an internal same-backend primitive-choice comparison. It
does not authorize:

- release or tag action;
- public speedup claims;
- whole-app acceleration claims;
- broad RT-core speedup claims;
- true zero-copy claims;
- paper reproduction claims;
- package-install claims.

