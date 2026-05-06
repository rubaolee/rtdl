# Goal1387: v1.5 Readiness Public Evidence State

Date: 2026-05-06

Source commit before change: `b8d79cf96e4d2c75e4a01ef63afbeeecd02dd5b1`

## Scope

This goal makes the evidence boundary explicit in the compact v1.5 readiness
decision.

The readiness module now exports:

- `V1_5_INTERNAL_READINESS_EVIDENCE_STATE = "internal_pod_validated_non_claim_grade"`
- `V1_5_INTERNAL_READINESS_REQUIRED_PUBLIC_EVIDENCE = ("claim_grade_exact_subpath_evidence", "same_contract_baseline", "reviewed_public_wording_packet")`

The decision now reports:

- `evidence_state`
- `required_public_evidence`
- `claim_grade_exact_subpath_evidence_ready: False`
- `same_contract_baseline_ready: False`
- `reviewed_public_wording_packet_ready: False`

The validator requires the exact evidence state and required public evidence
tuple, and rejects any decision that marks those public-evidence prerequisites
ready.

This keeps internal pod validation separate from claim-grade public evidence.

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
Ran 102 tests in 0.034s
OK
```

## Pod Validation

Pod SSH:

```text
ssh root@213.173.108.215 -p 14800 -i ~/.ssh/id_ed25519_rtdl_codex
```

Fresh Git clone validation:

```text
commit: 20c0723199d1885560d9aa45d1950536972647b0
python: Python 3.12.3
git: git version 2.43.0

PYTHONPATH=src:. python3 -m unittest tests.goal1367_v1_5_internal_readiness_gate_test
Ran 9 tests in 0.001s
OK

PYTHONPATH=src:. python3 -m unittest <v1.5 slice>
Ran 102 tests in 5.932s
OK
```
