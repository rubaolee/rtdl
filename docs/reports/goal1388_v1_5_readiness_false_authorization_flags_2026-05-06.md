# Goal1388: v1.5 Readiness False Authorization Flags

Date: 2026-05-06

Source commit before change: `bfb7fdff7546bd4e86dfc5981675e769a78a4812`

## Scope

This goal centralizes the compact v1.5 readiness decision's fail-closed
authorization flags.

The readiness module now exports:

- `V1_5_INTERNAL_READINESS_FALSE_AUTHORIZATION_FLAGS`

`v1_5_internal_readiness_decision()` now reports `false_authorization_flags`,
and `validate_v1_5_internal_readiness_decision()` requires the exact tuple
before checking every listed decision field is `False`.

This gives downstream tools a single machine-checkable list of fields that
must remain false for the internal non-public v1.5 readiness decision.

## Local Validation

Focused readiness gate:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1367_v1_5_internal_readiness_gate_test
Ran 9 tests in 0.003s
OK
```

v1.5 slice:

```text
PYTHONPATH=src:. python3 -m unittest <v1.5 slice>
Ran 102 tests in 0.041s
OK
```
