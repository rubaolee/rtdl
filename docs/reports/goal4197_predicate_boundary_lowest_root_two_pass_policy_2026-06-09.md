# Goal4197: Predicate Boundary Lowest-Root Two-Pass Policy

Date: 2026-06-09

## Purpose

Goal4194 added a deterministic reference contract for predicate-aware boundary
union. Goal4197 threads the first executable policy hook into the existing
generic OptiX+Numba grouped-stream route:

`boundary_assignment_policy="lowest_component_root_two_pass"`

This is an explicit user-selected policy. It is not the default, not a hidden
dispatcher decision, and not a route promotion.

## What Changed

- The Numba grouped-stream adapter now accepts a boundary-assignment policy.
- The existing one-pass route remains the default as
  `lowest_candidate_then_root`.
- The new `lowest_component_root_two_pass` preview first settles predicate-true
  component roots, resets boundary candidates, then runs a second prepared RT
  pass to assign predicate-false boundary items to component roots.
- The native OptiX grouped-union fallback path now writes the observed component
  root into the fallback column instead of a raw candidate item id.
- Front-door planning metadata exposes the supported policies and rejects the
  two-pass policy for CuPy instead of pretending both partners support it.

## Why This Matters

Goal4190 showed that counts-only signatures can match while policy-bound
component-size signatures remain fragile. The design issue is boundary
assignment: a fast one-pass candidate capture can assign a boundary item through
whichever candidate/root happens to win, while the reference contract requires a
deterministic root policy.

Goal4197 does not claim this is faster. It makes the policy executable so the
next pod run can measure the tradeoff honestly:

- one-pass route: faster candidate, weaker policy boundary;
- two-pass route: stronger deterministic policy, likely more expensive;
- promotion requires same-contract correctness plus performance evidence.

## Boundary

Goal4197 does not authorize release, public speedup claims, whole-app claims,
broad RT-core claims, true-zero-copy claims, automatic partner selection, or
app-specific native engine logic. It only adds an explicit preview policy on the
generic fixed-radius grouped-union continuation.

## Next Pod Work

Build OptiX on the RTX pod and compare:

- existing grouped-stream Numba default;
- `lowest_component_root_two_pass`;
- counts-only direct-status probe from Goal4190.

The required evidence is correctness against the Goal4194 reference on small
fixtures, then scale timing on dense and sparse point distributions.
