# RayJoin Datasets In RTDL

This file is the short current-state dataset map for the RayJoin-oriented RTDL
slice.

## Current Dataset Classes

RTDL currently uses three dataset classes:

1. tiny in-repo fixtures
   - for unit tests and small examples

2. bounded exact-source subsets
   - for controlled correctness and performance work

3. larger exact-source staged datasets
   - for accepted larger checks on the Linux hosts

## Representative Families Already Exercised

- `County ⊲⊳ Zipcode`
- `BlockGroup ⊲⊳ WaterBodies`
- bounded `LKAU ⊲⊳ PKAU`

## Where To Read More

- [Public Dataset Sources](rayjoin_public_dataset_sources.md)
- accepted reports in `docs/reports/`

## Boundary

This file is intentionally short. It is the dataset map, not the detailed
provenance log or the historical reproduction matrix.
