# Goal2898: RayDB Perf-Gate Readiness Integration

Date: 2026-05-31
Status: accepted as metadata/readiness integration

## Purpose

Goal2896 produced the current pod-backed same-contract performance-decision gate for RayDB-style scalar grouped reductions. Goal2898 wires that decision into the v2.5 migration metadata and readiness index so the repository no longer relies only on older Goal2727/2728 wording.

## What Changed

Updated:

- `src/rtdsl/v2_5_triton_app_migration.py`
- `src/rtdsl/v2_5_internal_readiness.py`
- `tests/goal2898_raydb_perf_gate_readiness_integration_test.py`

The RayDB migration row now states:

- current hot path: primitive-first fused RTDL for grouped scalar reductions;
- current evidence: Goal2896 same-contract performance gate;
- measured result: prepared hit-stream plus Triton is `22.58x-205.08x` slower than primitive-first for the measured count/sum rows;
- policy: do not promote Triton simply to use Triton.

The tiered benchmark manifest now indexes Goal2896 as the current RayDB same-contract gate and keeps the typed hit-stream plus Triton path as the alternative reserved for unfused continuations.

The internal readiness packet now requires the Goal2896 report and exposes the next action:

`triage_goal2897_external_review_for_goal2896_raydb_perf_gate`

## Boundary

This is not a release authorization.

It does not authorize public speedup wording, true-zero-copy wording, broad RT-core claims, whole-app RayDB reproduction claims, automatic Triton selection, or package-install claims. external review remains required before Goal2896 can feed any future release packet.

## Validation

Local validation:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2898_raydb_perf_gate_readiness_integration_test

Ran 4 tests in 0.132s
OK
```

The broader focused validation also includes:

- `tests.goal2783_v2_5_app_migration_selection_guidance_test`
- `tests.goal2806_v2_5_internal_readiness_packet_test`
- `tests.goal2896_raydb_same_contract_performance_decision_gate_test`

```text
Ran 20 tests in 0.391s
OK
```

Python compile validation also passed for the touched readiness/planner modules, the Goal2896 analyzer, and the Goal2898 test.
