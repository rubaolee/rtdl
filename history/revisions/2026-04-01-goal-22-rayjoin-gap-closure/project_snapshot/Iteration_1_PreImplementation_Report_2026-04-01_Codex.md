# Goal 22 Iteration 1 Pre-Implementation Report

## Proposed First Slice

The cleanest first slice for Goal 22 is:

1. add machine-readable registries for:
   - paper artifacts
   - dataset families
   - local profiles
2. add generator/reporting support for:
   - Table 3 analogue
   - Table 4 analogue
   - Figure 15 analogue
3. encode fidelity labels and the `overlay-seed analogue` boundary into those outputs

## Why This First Slice

This slice closes the reporting/evaluation blockers without forcing immediate large public dataset downloads in the same change.

It gives the repo:

- a stable programmatic matrix,
- stable provenance metadata,
- and the missing artifact generators

before we decide how much exact-input acquisition can realistically be done on this Mac.

## Deferred To Later Goal 22 Iterations If Needed

- actual public dataset download helpers for all missing families
- large-file conversion pipelines
- any blocker discovered only after the first analogue generators are wired up

## Review Questions

1. Is this the right first Goal 22 slice?
2. Is it acceptable to prioritize registry + generator closure before full public-dataset acquisition?
3. Does this stay within the Goal 21 blocker list?
4. Should implementation begin?
