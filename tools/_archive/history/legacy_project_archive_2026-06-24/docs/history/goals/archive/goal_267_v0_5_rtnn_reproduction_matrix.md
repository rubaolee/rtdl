# Goal 267: v0.5 RTNN Reproduction Matrix

Date: 2026-04-12
Status: proposed

## Purpose

Build the first explicit RTNN reproduction matrix on top of the dataset and
baseline registries so the `v0.5` line can answer, in one place:

- which pairings are bounded-reproduction work
- which are exact-reproduction candidates
- which are RTDL extensions

## Why This Goal Matters

The charter said `v0.5` needs labeled experiment reports. Goals 265 and 266
made the data and baseline layers concrete. This goal combines them into the
first actual matrix.

## Scope

This goal will:

1. add an RTNN matrix module in `src/rtdsl/`
2. combine dataset families, experiment targets, and baseline libraries into
   explicit matrix rows
3. label matrix rows honestly:
   - `planned_bounded_matrix`
   - `blocked_on_exact_dataset_and_adapter`
   - `planned_rtdl_extension`
   - `nonpaper_comparison_only`
4. add tests proving the matrix filters and labels

## Non-Goals

This goal does not:

- run the experiments
- claim any exact paper reproduction
- claim any third-party adapter is online

## Done When

This goal is done when the public Python surface can produce a first RTNN
reproduction matrix that preserves the exact/bounded/extension boundary without
manual spreadsheet logic.
