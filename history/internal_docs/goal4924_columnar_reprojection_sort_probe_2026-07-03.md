# Goal4924: Columnar Reprojection/Sort Probe

Date: 2026-07-03

## Purpose

Test the only remaining plausible Numba-adjacent optimization in the current
RayJoin Section 5.7 prepared-hot path: the numeric reprojection/sort region.

This goal is deliberately narrow. It does not modify RTDL core, public APIs,
native code, docs, tutorials, or release surface. It only creates an internal
experiment wrapper around the already proven public-primitives reproduction
harness.

## Background

Goal4915 repeat 1 measured the current prepared-hot body as:

- hot body: `3.831950969994068s`
- output writer: `1.7631013467907906s`
- intersection reprojection: `0.4678172171115875s`
- sort map0 + sort map1: `0.41644977033138275s`
- LSI prepared replay: `0.0062610432505607605s`

The writer is not a Numba target. The only plausible remaining app-layer
numeric target is:

`intersection_reprojection_sec + sort_map0_sec + sort_map1_sec ~= 0.884s`

## Work

Create an internal experimental wrapper:

`history/internal_docs/goal4924_columnar_reprojection_sort_probe.py`

The wrapper must:

1. Reuse the Goal4886 public-primitives + Numba writer route.
2. Avoid importing `rtdsl.rayjoin_overlay`.
3. Keep public LSI/PIP primitives unchanged.
4. Replace only:
   - `intersection_rows_from_pairs`
   - `sort_xsects_for_map`
5. Avoid `fractions.Fraction` materialization on the hot reprojection path.
6. Preserve byte-for-byte equality to AuthorOfficial.
7. Record whether the probe is a win, neutral, or failure.

## Hard Bar

The probe is only worth continuing if:

- `intersection_reprojection_sec + sort_map0_sec + sort_map1_sec <= 0.45s`
- total hot body `<= 3.45s`
- output remains byte-equal to AuthorOfficial

If either performance bar fails or byte equality fails, this line stops.

## Expected Risk

The main correctness risk is sorting. The original route sorts intersections
with exact rational distance keys. A faster sort using truncated scaled integer
coordinates may be faster but can change order in degenerate cases. Therefore
the probe supports two modes:

- `scaled_int`: faster, approximate scaled-coordinate sort key.
- `exact_cmp`: exact rational comparator without creating `Fraction` objects.

The first mode tests whether the fast key is safe for the representative data.
If it fails byte equality, the second mode tests whether avoiding `Fraction`
materialization still helps when exact order is preserved.

## Exit Labels

- `goal4924_win_continue_columnar_path`
- `goal4924_correct_but_not_fast_stop_path`
- `goal4924_fast_but_wrong_reject_path`
- `goal4924_failed_environment_or_input_gap`

## Decision Audit

Was this goal-level decision foolish? No. It is a bounded probe against a named
0.884s phase, with byte equality and hard stop conditions.

What would be foolish? Continuing writer micro-optimization, or treating a
byte-mismatching fast sort as acceptable.

Alternative path? Stop optimization immediately and move to architectural
pushdown/output-writer decisions. This probe is only justified because it is
small and falsifiable.

Can we try a different path if this fails? Yes. If this fails, the remaining
RayJoin speed work is no longer a Python/Numba cleanup question.
