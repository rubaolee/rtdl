# Goal3555 Collect-K Microprobe Contact Correction

Date: 2026-06-06

## Purpose

Goal3554 showed that the contact-manifold AABB broadphase was not a stable regression, but its single app-level `collect_k_bounded_rows_sec` value looked about 2x slower in v2.8 than v2.3. Goal3555 isolates the generic collector itself before changing code.

Artifact:

- `docs/reports/goal3555_collect_k_microprobe_a5000/summary.json`

## Probe

For each lane, the probe:

1. Builds the same contact grid fixture.
2. Uses OptiX AABB broadphase to produce 4096 candidate rows.
3. Measures `collect_k_bounded_rows` 200 times.
4. Measures `validate_collect_k_bounded_result` separately 200 times.

Both lanes used tuple row containers with tuple rows:

- row container type: `tuple`
- row element type: `tuple`
- row count: `4096`

## Result

| Phase | v2.3 median | v2.8 median | v2.8/v2.3 |
| --- | ---: | ---: | ---: |
| `collect_k_bounded_rows` | `0.005402350` | `0.004573330` | `1.181x` |
| validation | `0.005468729` | `0.004538195` | `1.205x` |
| combined collect+validate | `0.010978700` | `0.009080293` | `1.209x` |

## Interpretation

The generic Python collector is not the stable contact-manifold regression. In an isolated repeated microprobe, v2.8 is faster than v2.3 for both collection and validation.

That means the single-call `collect_k_bounded_rows_sec` value in Goal3554 should be treated as diagnostic noise or context-sensitive timing, not enough evidence for a source change. The correct engineering decision is to avoid touching the app-agnostic collector until a repeatable regression is found.

## Boundary

This is diagnostic evidence only. It does not authorize public speedup claims, whole-app claims, release, broad RT-core claims, zero-copy claims, paper-reproduction claims, or package-install claims.

## Next Target

After Goal3553-3555, v2.9 has an all-target 11-row parity baseline and no confirmed contact collector regression. The next useful performance target is RTNN (`0.956x` in Goal3553), because it is the clearest remaining stable negative row after contact is de-risked.
