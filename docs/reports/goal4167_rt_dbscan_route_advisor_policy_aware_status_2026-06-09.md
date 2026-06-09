# Goal4167: RT-DBSCAN Advisor After Policy-Aware Semantics

Status: accepted advisor update; no route promotion.

## Purpose

Goal4166 clarified that mixed-predicate comparisons need a policy-aware semantic
contract. That clarification should not be misread as a performance promotion.

Goal4167 updates `explain_rt_dbscan_explicit_route_choice(...)` so the advisor
now names both:

- Goal4165: mixed-predicate policy variant probe
- Goal4166: policy-aware RT-DBSCAN semantic signature

## What Changed

The advisor now reports:

- `policy_aware_semantic_signature_helper`
- `mixed_predicate_comparison_contracts`
- `mixed_predicate_policy_probe`
- `mixed_predicate_policy_aware_contract`
- `mixed_predicate_performance_status`

The grouped-stream option remains the conservative mixed-predicate route unless
the caller explicitly accepts a different policy-aware semantic contract.

The direct-status option now says custom mixed-predicate overrides must choose a
policy-aware semantic contract and are not broadly faster in Goal4165.

## Boundary

Policy-aware counts-only semantics can pass even when component-size policy
differs, but Goal4165 does not show broad performance advantage for mixed
predicate direct-status. Goal4167 therefore does not promote mixed predicate
direct-status.

policy-aware counts-only semantics can pass, but performance still blocks a broad mixed-predicate promotion.

Goal4167 does not promote mixed predicate direct-status.

No hidden dispatch or public speedup claim is authorized.

Native engine remains unchanged.

## Validation

`tests.goal4167_rt_dbscan_route_advisor_policy_aware_status_test`
