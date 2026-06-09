# Goal4166: Policy-Aware RT-DBSCAN Semantic Signature

Status: accepted app-layer semantic helper; no route promotion.

## Purpose

Goal4165 showed that mixed-predicate RT-DBSCAN rows expose a border-assignment
policy problem, not just a simple grouped-stream configuration mismatch. A
predicate-false item can touch multiple predicate-true components. In that case,
component-size distribution is only stable if the border assignment policy is
part of the contract.

Goal4166 adds an app-layer helper:

`policy_aware_rt_dbscan_semantic_signature(...)`

It keeps the old component-size contract available, while also exposing a
counts-only contract for comparisons where border tie-break assignment is not
semantic.

## Contracts

`policy_bound_component_sizes`

- Includes canonical component-size distribution.
- Use when the route claims a specific border assignment policy and component
  sizes are part of the observable contract.

`core_noise_assigned_counts_only`

- Compares core count, noise count, assigned count, border count, and total point
  count.
- Does not include component-size distribution.
- Use when the chosen border tie-break is deliberately outside the semantic
  contract.

## Why This Matters

The old `canonical_component_size_signature(...)` helper is still useful: it
ignores arbitrary component label ids but still treats component-size
distribution as semantic. Goal4166 does not remove it.

The new helper adds a second layer for mixed-predicate rows, where two legal
border policies can produce the same core/noise/assigned counts but different
component-size distributions.

## Validation

`tests.goal4166_policy_aware_rt_dbscan_semantic_signature_test`

The tests prove:

- The old Goal4159 `road_sparse_many_noise` mismatch is still detected under
  `policy_bound_component_sizes`.
- The same row matches under `core_noise_assigned_counts_only`.
- All Goal4165 mixed-policy probe rows match under the counts-only contract.
- Invalid contract names fail closed.

## Boundary

This does not promote predicate direct-status for mixed predicate rows. It does
not change native code, add a DBSCAN ABI, authorize release, or authorize public
speedup wording.

Native engine remains unchanged.

