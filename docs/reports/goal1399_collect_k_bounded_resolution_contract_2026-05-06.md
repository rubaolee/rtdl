# Goal 1399 - COLLECT_K_BOUNDED Resolution Contract

Date: 2026-05-06

## Status

Defined the standalone-v1.5 resolution strategy for `COLLECT_K_BOUNDED`.

This does not promote `COLLECT_K_BOUNDED` to stable. It converts the previous
open-ended blocker into an explicit promotion-or-exclusion decision contract.

Current resolution status:

```text
defined_pending_evidence
```

## Resolution Strategy

Primary strategy:

```text
promote_to_standalone_if_native_fail_closed_parity_and_benchmarks_pass
```

Fallback strategy:

```text
exclude_row_returning_apps_from_standalone_v1_5_if_gates_do_not_pass
```

This means v1.5 will not remain ambiguous:

- if bounded collection passes the required gates, it can be promoted into the
  standalone language surface;
- if it does not pass, row-returning apps must be explicitly excluded from
  standalone-complete v1.5 scope.

## Preserved Semantics

The resolution preserves the existing fail-closed policy:

- primitive: `COLLECT_K_BOUNDED`
- capacity parameter: `k`
- capacity unit: `candidate_pair_rows`
- ordering policy: stable by `(left_id, right_id)` after candidate discovery
- overflow policy: no silent truncation
- failure mode: fail closed on overflow
- truncation allowed: false
- complete candidate coverage required: true
- score reduction after overflow: false
- public wording allowed: false
- release/tag action authorized: false

## Promotion Gates

The promotion gates are now machine-readable:

- `published_capacity_ordering_overflow_contract`
- `python_fail_closed_reference_tests`
- `embree_native_fail_closed_collection`
- `optix_native_fail_closed_collection`
- `cross_backend_complete_candidate_coverage_parity`
- `score_reduction_guarded_by_complete_collection`
- `row_returning_app_scope_classified`
- `same_contract_app_correctness_suite`
- `same_contract_app_benchmark_suite`
- `external_review_before_public_promotion`

Currently passed:

- `published_capacity_ordering_overflow_contract`
- `python_fail_closed_reference_tests`
- `score_reduction_guarded_by_complete_collection`

Currently failed:

- `embree_native_fail_closed_collection`
- `optix_native_fail_closed_collection`
- `cross_backend_complete_candidate_coverage_parity`
- `row_returning_app_scope_classified`
- `same_contract_app_correctness_suite`
- `same_contract_app_benchmark_suite`
- `external_review_before_public_promotion`

## API

Added exports:

- `V1_5_COLLECT_K_BOUNDED_RESOLUTION_STATUS`
- `V1_5_COLLECT_K_BOUNDED_RESOLUTION_STRATEGY`
- `V1_5_COLLECT_K_BOUNDED_FALLBACK_STRATEGY`
- `V1_5_COLLECT_K_BOUNDED_PROMOTION_GATES`
- `v1_5_collect_k_bounded_resolution`
- `validate_v1_5_collect_k_bounded_resolution`

The standalone release gate now embeds the resolution plan while keeping
`collect_k_bounded_resolution` as a failed release gate.

## Validation

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1399_collect_k_bounded_resolution_test tests.goal1398_v1_5_standalone_release_gate_test tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test
```

Result:

```text
Ran 20 tests in 0.027s
OK
```

## Next Work

The next technical slice is to turn the native collection gates from policy
claims into current-source evidence:

1. Validate Embree native fail-closed bounded collection from current source.
2. Validate OptiX native fail-closed bounded collection from current source.
3. Compare candidate-coverage parity and guarded score-reduction behavior.
4. Keep release/tag blocked until same-contract app correctness and benchmark
   suites exist.

