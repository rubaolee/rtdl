# Goal4025 Partition Convergence Candidate Metadata Refresh

Date: 2026-06-08

## Purpose

Goal4025 updates the `partition_convergence_hybrid` candidate metadata after the new validation chain landed.

The candidate strategy now explicitly records:

- Goal4014 compressed enumeration accounting;
- Goal4016 typed partition-summary stream contract;
- Goal4017 Python partition-summary reference;
- Goal4019 same-contract validator;
- Goal4021 component-label oracle against all-pairs fixed-radius labels;
- Goal4023 complete-candidate-coverage status invariant;
- Goal4024 edge-case and floating-point tolerance tests.

## Promotion Gate

The candidate guidance now names the native promotion gate:

`candidate_device_producer_must_pass_goal4019_goal4021_goal4023_goal4024_before_timing`.

This keeps the next native or partner producer from being timed or promoted before it proves complete coverage and same-contract component labels on deterministic cases.

## Boundary

This goal does not make `partition_convergence_hybrid` executable. In plain machine-checkable wording: it does not make partition_convergence_hybrid executable. It does not add a native ABI. It does not authorize public speedup wording, RT-core speedup wording, whole-app benchmark wording, release wording, or true zero-copy wording.
