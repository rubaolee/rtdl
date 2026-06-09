# Goal4211: Boundary Policy Default Canonicalization

Date: 2026-06-09

## Purpose

Goals4201-4210 established that the fast one-pass fixed-radius grouped-stream
policy is better described as `single_pass_candidate_root_rebased`. Goal4211
makes that canonical name the user-facing default for the fixed-radius graph
component front door and Numba prepared adapter.

The old name `lowest_candidate_then_root` remains a supported compatibility
alias. Historical artifacts and tests may still mention it, but new plans and
new benchmark probes should prefer the canonical name.

## Boundary

This is a naming/default cleanup. It does not change native ABI, native kernels,
runtime behavior, performance, labels, release status, true-zero-copy status,
automatic partner selection, or app-specific native engine logic.
