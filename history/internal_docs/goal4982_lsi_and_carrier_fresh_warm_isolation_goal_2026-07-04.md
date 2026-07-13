# Goal4982: Symmetric Fresh/Warm Isolation For LSI Producer And Carrier Builder

Date: 2026-07-04

## Purpose

Claude's review of the v2.14.3 closeout plan identified an asymmetry:

- carrier first-large-call cost is about `0.69s`;
- LSI producer setup cost is about `2.6-2.7s`;
- both appear to be warmable/setup-like costs.

Goal4982 measures both symmetrically. It must not warm only the smaller carrier cost while ignoring the larger LSI producer cost.

## Work

Run the top4 writer-free binary route and record:

1. fresh process, normal route;
2. same-process or repeated route after LSI/carrier warm state;
3. LSI extended timings:
   - scaled cache ensure
   - grouped range ensure
   - exact pipeline ensure
   - split kernel ensure
   - native launch
4. carrier side-builder timings:
   - side0 builder
   - side1 builder
   - carrier total

## Required Interpretation Rules

- Fresh and warm must always be reported side by side.
- Warm numbers are not allowed as a standalone headline.
- Any cost that cannot be justified as real prepare-once/query-many product behavior remains in the fresh number.
- If warm cost is used, the use case must be named explicitly.

## Boundary

Allowed:

- benchmark/control measurement scripts
- app-owned CLI routes already present
- no new optimization unless measurement proves the target

Forbidden:

- no public high-performance claim
- no author-performance headline
- no RTDL core/native changes
- no warm-only result

## Exit Labels

- `completed_lsi_and_carrier_warmup_symmetric_matrix`
- `completed_warmup_not_product_strategy_keep_fresh_headline`
- `fail_redo_due_to_lsi_carrier_asymmetry`
