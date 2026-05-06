# Goal1391: v1.5 Readiness Decision Fingerprint

Date: 2026-05-06

Source commit before change: `a37b03135a5109240dcfdb6966da58caa35e9ae2`

## Scope

This goal adds a deterministic fingerprint to the compact v1.5 readiness
decision for drift detection.

The readiness module now exports:

- `V1_5_INTERNAL_READINESS_DECISION_FINGERPRINT_ALGORITHM = "sha256"`
- `V1_5_INTERNAL_READINESS_DECISION_FINGERPRINT_FIELDS`

`v1_5_internal_readiness_decision()` now reports:

- `decision_fingerprint_algorithm`
- `decision_fingerprint_fields`
- `decision_fingerprint`

`validate_v1_5_internal_readiness_decision()` recomputes the fingerprint from
the selected stable decision fields and rejects mismatches.

This fingerprint is internal drift-detection metadata only. It does not
authorize public v1.5 release wording, public speedup claims, or claim-grade
evidence.

## Local Validation

Focused readiness gate:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1367_v1_5_internal_readiness_gate_test
Ran 9 tests in 0.002s
OK
```

v1.5 slice:

```text
PYTHONPATH=src:. python3 -m unittest <v1.5 slice>
Ran 102 tests in 0.030s
OK
```
