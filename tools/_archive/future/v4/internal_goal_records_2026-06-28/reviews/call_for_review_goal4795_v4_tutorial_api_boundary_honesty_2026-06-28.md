# Call for review: Goal4795 V4 tutorial/API boundary honesty

Date: 2026-06-28

## Review request

Please review Goal4795 as a public honesty and tutorial/API boundary gate.

The specific issue: `sorting_rows.py` belongs in the V4 tutorial path as an RTDL
kernel/relation lesson, but it does not have a V4 sorting operator, V4
segment-intersection runtime surface, or V4 prepared runtime mapping.

The review should determine whether the public materials now make that
distinction clear enough for users.

## Primary files to inspect

- `examples/tutorial_programs/sorting_rows.py`
- `tutorials/current/03_sorting_rows.md`
- `tutorials/current/README.md`
- `examples/tutorial_programs/README.md`
- `examples/README.md`
- `docs/current_v4_status.md`
- `docs/public_documentation_map.md`
- `README.md`
- `tests/v4_goal4640_public_docs_cleanup_test.py`
- `docs/engineering/goal4795_v4_tutorial_api_boundary_honesty_2026-06-28.md`

## Validation already run

Windows:

```powershell
py -3 examples\tutorial_programs\sorting_rows.py
py -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Result:

```text
Ran 22 tests in 82.827s
OK
```

Linux clean-copy simulation on `192.168.1.20`, copied to `/tmp/rtdl_goal4795_boundary_honesty`:

```bash
PYTHONPATH=src:. python3 examples/tutorial_programs/sorting_rows.py
PYTHONPATH=src:. python3 -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Result:

```text
Ran 22 tests in 32.683s
OK
```

## Required questions

1. Do the public docs now clearly distinguish RTDL language-layer lessons from V4 runtime/operator-surface lessons?
2. Does `sorting_rows.py` now machine-state that it has no V4 operator surface?
3. Does `03_sorting_rows.md` clearly say there is no V4 sorting operator surface and no V4 segment-intersection runtime surface?
4. Do the tutorial and examples indexes avoid implying every V4 tutorial-path program has a V4 runtime surface?
5. Does the new test protect this boundary from regression?
6. Are Windows and Linux validations sufficient for this goal?
7. Should Goal4795 be accepted as complete, require amendments, or be blocked?

## Allowed verdict labels

- `approve_goal4795_v4_tutorial_api_boundary_honesty_complete`
- `approve_with_required_amendments`
- `block_goal4795_v4_tutorial_api_boundary_honesty`

## Non-authorization boundary

This review must not authorize:

- a V4 sorting operator claim,
- a V4 segment-intersection runtime-surface claim,
- broad V4 speedup wording,
- whole-app performance claims,
- a V4 public tag,
- Tier-3 arbitrary callback claims,
- raw OptiX callback claims,
- C ABI or embedding claims,
- paper-reproduction claims.
