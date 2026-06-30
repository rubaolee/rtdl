# Goal1385: v1.5 Readiness v1.0 Tag Boundary

Date: 2026-05-06

Source commit before change: `a7e211a62528589054c66022a0fb0bbdc1df9cef`

## Scope

This goal makes the current public release tag boundary explicit in the compact
v1.5 readiness decision.

The readiness module now exports:

- `V1_5_INTERNAL_READINESS_CURRENT_PUBLIC_RELEASE_TAG = "v1.0"`

The decision now reports:

- `current_public_release_tag: "v1.0"`
- `current_public_release_tag_move_authorized: False`
- `new_public_release_tag_authorized: False`

The validator requires the exact current public release tag and rejects any tag
movement or new public release tag authorization.

This preserves the project boundary: internal v1.5 contract readiness does not
move or retag `v1.0`, and it does not authorize a new public release tag.

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
Ran 102 tests in 0.039s
OK
```

## Pod Validation

Pod SSH:

```text
ssh root@213.173.108.215 -p 14800 -i ~/.ssh/id_ed25519_rtdl_codex
```

Fresh Git clone validation:

```text
commit: 77690263c08c1c70510ad7c6418bb66463d91395
python: Python 3.12.3
git: git version 2.43.0

PYTHONPATH=src:. python3 -m unittest tests.goal1367_v1_5_internal_readiness_gate_test
Ran 9 tests in 0.001s
OK

PYTHONPATH=src:. python3 -m unittest <v1.5 slice>
Ran 102 tests in 5.961s
OK
```
