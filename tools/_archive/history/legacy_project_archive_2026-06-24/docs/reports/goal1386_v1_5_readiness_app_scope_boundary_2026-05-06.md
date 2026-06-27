# Goal1386: v1.5 Readiness App Scope Boundary

Date: 2026-05-06

Source commit before change: `e93395a1a3c599d40879155bca994aea3395d67a`

## Scope

This goal makes the app-scope boundary explicit in the compact v1.5 readiness
decision.

The readiness module now exports:

- `V1_5_INTERNAL_READINESS_SCOPE_KIND = "generic_traversal_plus_reduction_subpaths"`
- `V1_5_INTERNAL_READINESS_EXCLUDED_APP_SCOPE = ("app_level_continuations", "whole_app_speedup", "public_nvidia_speedup")`

The decision now reports:

- `scope_kind`
- `excluded_app_scope`
- `app_level_continuations_authorized_as_generic: False`
- `whole_app_speedup_claim_authorized: False`
- `public_nvidia_speedup_claim_authorized: False`

The validator requires the exact generic subpath scope, preserves the excluded
app-scope tuple, and rejects any decision that authorizes app-level
continuations as generic or public whole-app/NVIDIA speedup claims.

This keeps internal v1.5 readiness scoped to generic traversal-plus-reduction
subpaths, not whole-app acceleration.

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
commit: 519dfa68d93e02562bd1ced39e238e06c64b0650
python: Python 3.12.3
git: git version 2.43.0

PYTHONPATH=src:. python3 -m unittest tests.goal1367_v1_5_internal_readiness_gate_test
Ran 9 tests in 0.001s
OK

PYTHONPATH=src:. python3 -m unittest <v1.5 slice>
Ran 102 tests in 5.912s
OK
```
