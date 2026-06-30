# Goal1384: v1.5 Readiness Decision Experimental Primitives

Date: 2026-05-06

Source commit before change: `488ec69a8bb166f3c54aa4ee3af568167555d720`

## Scope

This goal mirrors the stable and experimental primitive boundary from the full
readiness gate into the compact readiness decision.

The decision now reports:

- `stable_summary_primitives`
- `experimental_primitives`
- `experimental_contract_status_counts`
- `stable_collect_k_bounded_promotion_authorized: False`

The validator requires the exact stable primitive target, requires
`COLLECT_K_BOUNDED` to remain experimental, rejects `COLLECT_K_BOUNDED` in the
stable summary primitive tuple, and preserves the experimental diagnostic-only
status count.

This keeps the decision API consistent with the v1.5 scope: scalar summary
primitives can be stable, while `COLLECT_K_BOUNDED` remains experimental until
the scalar primitives are stable.

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
Ran 102 tests in 0.055s
OK
```

## Pod Validation

Pod SSH:

```text
ssh root@213.173.108.215 -p 14800 -i ~/.ssh/id_ed25519_rtdl_codex
```

Fresh Git clone validation:

```text
commit: aa5c35db99e723b61db347b81e75e6e162e1030c
python: Python 3.12.3
git: git version 2.43.0

PYTHONPATH=src:. python3 -m unittest tests.goal1367_v1_5_internal_readiness_gate_test
Ran 9 tests in 0.001s
OK

PYTHONPATH=src:. python3 -m unittest <v1.5 slice>
Ran 102 tests in 6.085s
OK
```
