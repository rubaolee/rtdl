# Call for review: Goal4793 tutorial tail

Date: 2026-06-28

## Review request

Please review Goal4793 as a tutorial-quality and public-surface correctness
gate.

The goal completes the final V4 tutorial tail:

1. partner choice and device-array bridge,
2. phase measurement,
3. callback planning boundary,
4. benchmark-app bridge.

## Primary files to inspect

Tutorial programs:

- `examples/tutorial_programs/partner_choices.py`
- `examples/tutorial_programs/measure_phases.py`
- `examples/tutorial_programs/operator_callback_planning.py`
- `examples/tutorial_programs/custom_predicate_early_exit_planning.py`
- `examples/tutorial_programs/benchmark_app_recipes.py`

Tutorial pages:

- `tutorials/current/21_partner_choice_device_arrays.md`
- `tutorials/current/22_measurement_phases.md`
- `tutorials/current/23_callback_planning_boundary.md`
- `tutorials/current/24_benchmark_app_bridge.md`

Indexes and gates:

- `tutorials/current/README.md`
- `examples/tutorial_programs/README.md`
- `examples/README.md`
- `docs/public_documentation_map.md`
- `tests/v4_goal4640_public_docs_cleanup_test.py`

Completion record:

- `docs/engineering/goal4793_tutorial_tail_partner_measurement_callback_bridge_2026-06-28.md`

## Validation already run

Windows:

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

Linux clean-copy simulation on `192.168.1.20`, copied to `/tmp/rtdl_goal4793_tutorial_tail`:

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

## Required questions

1. Does the partner lesson teach relation shape first and partner as execution policy second?
2. Does the device-array bridge avoid hiding app meaning behind a one-shot API?
3. Does the measurement lesson clearly separate setup, hot relation, continuation, validation, and materialization boundaries?
4. Does the callback lesson honestly reject arbitrary action-shaped callbacks and keep constrained predicates narrow?
5. Does the benchmark bridge connect concepts to the 10 apps without becoming an app-specific first tutorial?
6. Are public links and commands consistent?
7. Are Windows and Linux validations sufficient for this goal?
8. Should Goal4793 be accepted as complete, require amendments, or be blocked?

## Allowed verdict labels

- `approve_goal4793_tutorial_tail_complete`
- `approve_with_required_amendments`
- `block_goal4793_tutorial_tail`

## Non-authorization boundary

This review must not authorize:

- a V4 public tag,
- broad V4 speedup wording,
- whole-app performance claims,
- Tier-3 arbitrary callback claims,
- raw OptiX callback claims,
- C ABI or embedding claims,
- paper-reproduction claims,
- app-specific native-kernel claims.
