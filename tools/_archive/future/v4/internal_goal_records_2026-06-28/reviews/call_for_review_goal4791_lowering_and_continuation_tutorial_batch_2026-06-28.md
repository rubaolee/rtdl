# Call for review: Goal4791 lowering and continuation tutorial batch

Date: 2026-06-28

## Review request

Please review Goal4791 as a tutorial-quality and public-surface correctness gate.

The goal extends the current V4 tutorial sequence with three programs and three lessons:

1. component union from fixed-radius rows,
2. bounded witness collection from emitted witness rows,
3. aggregate-frontier rows with weighted grouped continuation.

The review should determine whether these materials teach the RTDL row/relation/kernel model first, and only then introduce the V4 operator/runtime wrapper as the implementation mapping.

## Primary files to inspect

Tutorial programs:

- `examples/tutorial_programs/component_union_from_radius.py`
- `examples/tutorial_programs/bounded_witness_collection.py`
- `examples/tutorial_programs/aggregate_frontier_rows.py`

Tutorial pages:

- `tutorials/current/12_component_union_from_radius.md`
- `tutorials/current/13_bounded_witness_collection.md`
- `tutorials/current/14_aggregate_frontier_rows.md`

Indexes and gates:

- `tutorials/current/README.md`
- `examples/tutorial_programs/README.md`
- `examples/README.md`
- `docs/public_documentation_map.md`
- `tests/v4_goal4640_public_docs_cleanup_test.py`

Completion record:

- `docs/engineering/goal4791_lowering_and_continuation_tutorial_batch_2026-06-28.md`

## Validation already run

Windows:

```powershell
py -3 examples\tutorial_programs\component_union_from_radius.py --mode kernel
py -3 examples\tutorial_programs\bounded_witness_collection.py --mode kernel
py -3 examples\tutorial_programs\aggregate_frontier_rows.py --mode relation
py -3 examples\tutorial_programs\aggregate_frontier_rows.py --mode v4
py -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Result:

```text
Ran 21 tests in 84.224s
OK
```

Linux clean-copy simulation on `192.168.1.20`, copied to `/tmp/rtdl_goal4791_lowering`:

```bash
PYTHONPATH=src:. python3 examples/tutorial_programs/component_union_from_radius.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/bounded_witness_collection.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/aggregate_frontier_rows.py --mode both
PYTHONPATH=src:. python3 -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Result:

```text
Ran 21 tests in 32.212s
OK
```

## Required questions

1. Does `component_union_from_radius.py` teach fixed-radius kernel rows and app-owned component-union continuation before introducing the V4 Numba surface?
2. Does `bounded_witness_collection.py` teach kernel-produced witness rows and bounded collection before introducing the V4 grouped-argmin surface?
3. Does `aggregate_frontier_rows.py` honestly use a relation-first lesson instead of faking an `@rt.kernel` predicate that the public tutorial API does not expose?
4. Are the script modes coherent?
   - Component union: `kernel`, `v4`, `both`, `visible`.
   - Bounded witness collection: `kernel`, `v4`, `both`, `visible`.
   - Aggregate frontier: `relation`, `v4`, `both`, `visible`.
5. Do the tutorial pages explain the RTDL relation/row/continuation model clearly enough that the V4 wrapper does not become a black-box substitute for learning?
6. Are partner statements honest and bounded?
7. Are public links and commands consistent?
8. Are Windows and Linux validations sufficient for this goal?
9. Should Goal4791 be accepted as complete, require amendments, or be blocked?

## Allowed verdict labels

- `approve_goal4791_lowering_and_continuation_tutorial_batch_complete`
- `approve_with_required_amendments`
- `block_goal4791_lowering_and_continuation_batch`

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
