# Goal4209: Boundary Policy Canonical Alias Cleanup

Date: 2026-06-09

## Purpose

Goals4201-4206 showed that the fast one-pass policy is better described as a
candidate-root route whose stored candidate is resolved through final component
roots. The old name `lowest_candidate_then_root` is still accepted for
compatibility, but it is not the clearest reader-facing concept.

Goal4209 adds the canonical policy name:

`single_pass_candidate_root_rebased`

The old name remains a supported alias. Metadata now reports both the
user-selected policy and the canonical policy.

## Boundary

This is a compatibility-safe metadata/API cleanup. It does not change native ABI,
route behavior, result labels, performance, release status, zero-copy status, or
app semantics.
