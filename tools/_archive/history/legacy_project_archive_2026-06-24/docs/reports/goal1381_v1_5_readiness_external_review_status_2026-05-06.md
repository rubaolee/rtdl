# Goal1381: v1.5 Readiness External Review Status Guard

Date: 2026-05-06

Source commit before change: `e801f88929571257c47c419584e84f6f9bfd3909`

## Scope

This goal makes the external-review status explicit in the internal v1.5
readiness decision. It distinguishes accepted review evidence from completed
3-AI consensus.

## Added Guard

The readiness module now exports exact review-partner constants:

- `V1_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PARTNERS = ("claude", "gemini")`
- `V1_5_INTERNAL_READINESS_ACCEPTED_EXTERNAL_REVIEW_PARTNERS = ("claude",)`

`v1_5_internal_readiness_decision()` now reports:

- `required_external_review_partners`
- `accepted_external_review_partners`
- `missing_external_review_partners`
- `external_3_ai_consensus_ready: False`

`validate_v1_5_internal_readiness_decision()` requires exact review-partner
state, recomputes missing partners, and rejects any decision that implies 3-AI
consensus is complete.

The current state is intentionally non-public:

- Claude has accepted review artifacts.
- Gemini does not have a usable accepted review artifact for this readiness
  boundary.
- Public claims remain blocked.

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
Ran 102 tests in 0.030s
OK
```

## Pod Validation

Pod SSH:

```text
ssh root@213.173.108.215 -p 14800 -i ~/.ssh/id_ed25519_rtdl_codex
```

Fresh Git clone validation:

```text
commit: d0b7798a5174cd744d8f2054a783ea1ff4e34850
python: Python 3.12.3
git: git version 2.43.0

PYTHONPATH=src:. python3 -m unittest tests.goal1367_v1_5_internal_readiness_gate_test
Ran 9 tests in 0.001s
OK

PYTHONPATH=src:. python3 -m unittest <v1.5 slice>
Ran 102 tests in 5.986s
OK
```
