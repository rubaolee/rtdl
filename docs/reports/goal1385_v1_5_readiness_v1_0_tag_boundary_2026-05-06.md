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
