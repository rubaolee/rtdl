# Call for review: Goal4794 final V4 tutorial surface

Date: 2026-06-28

## Review request

Please review the final V4 tutorial surface after Goals 4788-4793.

The review should answer whether the tutorial set is complete enough to tell
the user: "the V4 tutorials are finished and ready for your inspection."

## Primary files to inspect

Audit record:

- `docs/engineering/goal4794_final_tutorial_surface_audit_2026-06-28.md`

User-facing tutorial surface:

- `tutorials/current/README.md`
- `tutorials/current/01_first_run.md` through `tutorials/current/24_benchmark_app_bridge.md`
- `examples/tutorial_programs/README.md`
- all files under `examples/tutorial_programs/`
- `examples/README.md`
- `docs/public_documentation_map.md`

Validation gate:

- `tests/v4_goal4640_public_docs_cleanup_test.py`
- `tests/v4_frontdoor_test.py`
- `tests/v4_goal4643_publication_decision_test.py`

## Validation already run

Windows:

```powershell
py -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Result:

```text
Ran 21 tests in 85.405s
OK
```

Linux clean-copy simulation on `192.168.1.20`, copied to `/tmp/rtdl_goal4794_final_tutorials`:

```bash
PYTHONPATH=src:. python3 examples/tutorial_programs/hello_world.py
PYTHONPATH=src:. python3 examples/tutorial_programs/sorting_rows.py
PYTHONPATH=src:. python3 examples/tutorial_programs/fixed_radius_neighbors.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/ray_triangle_hits.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/aggregate_frontier_rows.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/partner_choices.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/measure_phases.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/benchmark_app_recipes.py
PYTHONPATH=src:. python3 -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Result:

```text
Ran 21 tests in 32.223s
OK
```

## Required questions

1. Does the current tutorial ladder have a coherent learner path from first RTDL concept to benchmark-app bridge?
2. Are hello world and sorting preserved as simple early lessons?
3. Do the tutorials teach RTDL kernel/relation/row/continuation thinking before V4 wrappers?
4. Are old tutorial pages removed from the current path and archived rather than competing with the current docs?
5. Do public tutorial files avoid stale internal process/review/history language?
6. Do tutorial programs run and expose coherent command modes?
7. Are partner, measurement, callback, and benchmark bridge boundaries clear enough for users?
8. Are Windows and Linux validations sufficient?
9. Should Goal4794 be accepted as complete, require amendments, or be blocked?

## Allowed verdict labels

- `approve_goal4794_final_tutorial_surface_complete`
- `approve_with_required_amendments`
- `block_goal4794_final_tutorial_surface`

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
