# Goal1390: v1.5 Readiness Broad Suite State

Date: 2026-05-06

Source commit before change: `667709beaee376ae1d476ac4c1324d2144742d8a`

## Scope

This goal exposes the broad local suite result in the compact v1.5 readiness
decision as internal regression evidence.

The readiness module now exports:

- `V1_5_INTERNAL_READINESS_BROAD_LOCAL_SUITE_STATE = "passed_internal_regression"`
- `V1_5_INTERNAL_READINESS_BROAD_LOCAL_SUITE_TESTS = 2656`
- `V1_5_INTERNAL_READINESS_BROAD_LOCAL_SUITE_SKIPPED = 197`

The decision now reports:

- `broad_local_suite_state`
- `broad_local_suite_tests`
- `broad_local_suite_skipped`
- `broad_local_suite_claim_grade_evidence: False`

The validator preserves the exact broad-suite state and count fields, while
rejecting any decision that treats the broad local suite as public claim-grade
evidence.

## Local Validation

Focused readiness gate:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1367_v1_5_internal_readiness_gate_test
Ran 9 tests in 0.001s
OK
```

v1.5 slice:

```text
PYTHONPATH=src:. python3 -m unittest <v1.5 slice>
Ran 102 tests in 0.029s
OK
```

## Pod Validation

Pod SSH:

```text
ssh root@213.173.108.215 -p 14800 -i ~/.ssh/id_ed25519_rtdl_codex
```

Fresh Git clone validation:

```text
commit: 60bbc84de69f3470eb55196be9476abe3f080cc9
python: Python 3.12.3
git: git version 2.43.0

PYTHONPATH=src:. python3 -m unittest tests.goal1367_v1_5_internal_readiness_gate_test
Ran 9 tests in 0.001s
OK

PYTHONPATH=src:. python3 -m unittest <v1.5 slice>
Ran 102 tests in 6.032s
OK
```
