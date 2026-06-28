# Goal4793 tutorial tail: partner, measurement, callback, benchmark bridge

Date: 2026-06-28

## Purpose

Goal4793 completes the final V4 tutorial tail after the app-lowering bridge.
This batch teaches:

1. explicit partner choice and device-array bridge boundaries,
2. phase measurement boundaries,
3. callback planning boundaries,
4. the benchmark-app bridge from concept programs to the 10 benchmark apps.

The purpose is to help a learner use RTDL V4 as a programming model without
turning V4 into a black-box planner call or a benchmark-app recipe book.

## Files changed

| File | Action | Purpose |
| --- | --- | --- |
| `examples/tutorial_programs/partner_choices.py` | Rewritten. | Adds `relation`, `v4`, `both`, and `visible` modes. Teaches that operator intent is stable and partner choice is an explicit execution policy. |
| `examples/tutorial_programs/measure_phases.py` | Rewritten. | Adds `relation`, `v4`, `both`, and `visible` modes. Teaches setup, hot relation work, continuation, and validation as separate phases. |
| `tutorials/current/21_partner_choice_device_arrays.md` | Added. | Teaches partner choice and device-array bridge examples after the relation is understood. |
| `tutorials/current/22_measurement_phases.md` | Added. | Teaches phase boundaries and why timing denominators matter. |
| `tutorials/current/23_callback_planning_boundary.md` | Added. | Teaches recognized V4 operators, constrained predicate paths, and deferred arbitrary action-shaped callbacks. |
| `tutorials/current/24_benchmark_app_bridge.md` | Added. | Teaches how to read the benchmark-app bridge as a concept map, not as the first tutorial. |
| `tutorials/current/README.md` | Updated. | Adds lessons 21-24 and the tail learning outcomes. |
| `examples/tutorial_programs/README.md` | Updated. | Uses `--mode both` for partner and measurement commands. |
| `examples/README.md` | Updated. | Uses `--mode both` for partner command in the first example path. |
| `docs/public_documentation_map.md` | Updated. | Uses `--mode both` for partner and measurement in the quick-check path. |
| `tests/v4_goal4640_public_docs_cleanup_test.py` | Updated. | Adds lessons 21-24 to the public documentation gate. |

## Teaching contract

The tutorial tail keeps the same rule as the previous batches:

```text
RTDL relation or continuation shape first
V4 operator/runtime mapping second
```

The partner lesson must not imply that Torch, CuPy, Numba, and RTDL native
change the app meaning. They are execution policies.

The measurement lesson must not mix setup, hot relation work, continuation, and
validation into one unexplained number.

The callback lesson must not imply arbitrary user callbacks are public V4.0
support. It teaches recognized operators, constrained pure boolean predicates,
and decomposition for action-shaped logic.

The benchmark bridge must not teach full benchmark apps as first lessons. It is
a map from concepts to full app sources.

## Validation

### Windows workspace

Commands:

```powershell
py -3 examples\tutorial_programs\partner_choices.py --mode both
py -3 examples\tutorial_programs\measure_phases.py --mode both
py -3 examples\tutorial_programs\operator_callback_planning.py --case tier2
py -3 examples\tutorial_programs\operator_callback_planning.py --case scalar-callback
py -3 examples\tutorial_programs\operator_callback_planning.py --case complex-callback
py -3 examples\tutorial_programs\custom_predicate_early_exit_planning.py
py -3 examples\tutorial_programs\benchmark_app_recipes.py
py -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Result:

```text
Ran 21 tests in 85.192s
OK
```

The Windows Python process printed the known local prefix warning on subprocess
runs, but all commands exited successfully.

### Local Linux clean-copy simulation

Host: `192.168.1.20`

The workspace was copied to `/tmp/rtdl_goal4793_tutorial_tail` and run as a
clean user checkout with `PYTHONPATH=src:.`.

Commands:

```bash
PYTHONPATH=src:. python3 examples/tutorial_programs/partner_choices.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/measure_phases.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/operator_callback_planning.py --case complex-callback
PYTHONPATH=src:. python3 examples/tutorial_programs/custom_predicate_early_exit_planning.py
PYTHONPATH=src:. python3 examples/tutorial_programs/benchmark_app_recipes.py
PYTHONPATH=src:. python3 -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Result:

```text
Ran 21 tests in 32.318s
OK
```

## Non-claims

This goal does not authorize:

- a V4 public tag,
- broad V4 speedup wording,
- whole-app performance claims,
- Tier-3 arbitrary callback claims,
- raw OptiX callback claims,
- C ABI or embedding claims,
- paper-reproduction claims,
- app-specific native-kernel claims.

## Goal status

Implementation and Windows/Linux validation are complete. External review is
required before marking the goal complete.
