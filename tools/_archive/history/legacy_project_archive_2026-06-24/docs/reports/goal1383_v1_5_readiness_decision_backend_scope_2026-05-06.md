# Goal1383: v1.5 Readiness Decision Backend Scope

Date: 2026-05-06

Source commit before change: `51f162c87b70675cdf33796b4e1ca2ead947c60f`

## Scope

This goal mirrors the v1.5 backend policy from the full readiness gate into the
compact readiness decision.

The decision now records:

- `active_backend_scope: ("embree", "optix")`
- `frozen_before_v2_1_backends: ("vulkan", "hiprt", "apple_rt")`
- `new_backend_implementation_authorized: False`
- `pre_v2_1_frozen_backend_work_authorized: False`

The validator requires the exact active and frozen backend scopes, rejects
overlap, and rejects any decision that authorizes new backend implementation or
pre-v2.1 frozen backend work.

This keeps the decision API consistent with the project boundary: active v1.5
engineering remains Embree plus OptiX, while Vulkan, HIPRT, and Apple RT are
not active implementation targets before v2.1.

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
Ran 102 tests in 0.041s
OK
```

## Pod Validation

Pod SSH:

```text
ssh root@213.173.108.215 -p 14800 -i ~/.ssh/id_ed25519_rtdl_codex
```

Fresh Git clone validation:

```text
commit: e9d5d7d4de48f6d968801f96b8892d3ffbfb4ca8
python: Python 3.12.3
git: git version 2.43.0

PYTHONPATH=src:. python3 -m unittest tests.goal1367_v1_5_internal_readiness_gate_test
Ran 9 tests in 0.001s
OK

PYTHONPATH=src:. python3 -m unittest <v1.5 slice>
Ran 102 tests in 5.987s
OK
```
