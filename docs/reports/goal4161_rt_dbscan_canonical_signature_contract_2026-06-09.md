# Goal4161 RT-DBSCAN Canonical Signature Contract

Date: 2026-06-09

Status: accepted app-layer comparison helper.

## Purpose

Goal4159 showed that exact `cluster_sizes` dictionaries can differ when two generic routes assign arbitrary component labels in a different order. For signature-only performance comparisons, label ids are not semantic. The useful app-level contract is:

- same core count
- same noise count
- same sorted component-size multiset

Goal4161 adds app-layer helpers to express that contract:

- `canonical_component_size_signature(signature)`
- `same_canonical_component_size_signature(left, right)`

These helpers do not change native output, partner output, or benchmark route behavior. They only prevent future diagnostics from confusing label-id permutation with a real border-assignment difference.

## Boundary

This does not solve the Goal4159 `road_sparse_many_noise` gap. That row differs even after canonicalization, so it still needs a generic border-assignment policy decision.

The helpers live in the benchmark app layer because the native engine must remain app-agnostic.
