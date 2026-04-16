# Goal 417 Report: v0.7 RT DB Conjunctive Scan Python Truth Path

Date: 2026-04-15
Goal:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_417_v0_7_rt_db_conjunctive_scan_python_truth_path.md`

## Summary

The first executable `v0.7` database-style RTDL kernel is now real in the
Python truth path.

Implemented surface:

- `rt.DenormTable`
- `rt.PredicateSet`
- `mode="db_scan"`
- `rt.conjunctive_scan(...)`

The bounded authoring shape is:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def sales_conjunctive_scan_reference():
    predicates = rt.input("predicates", rt.PredicateSet, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(predicates, table, accel="bvh", mode="db_scan")
    matches = rt.refine(candidates, predicate=rt.conjunctive_scan(exact=True))
    return rt.emit(matches, fields=["row_id"])
```

## Implemented behavior

- bounded conjunctive predicates normalize from tuples or mappings
- denormalized rows normalize from mapping records
- Python truth-path execution emits stable ordered `row_id` matches
- invalid predicate operators are rejected

## Verification

Focused test:

- `python3 -m unittest tests.goal417_v0_7_rt_db_conjunctive_scan_truth_path_test`
  - `Ran 5 tests`
  - `OK`

Regression check:

- `python3 -m unittest tests.goal389_v0_6_rt_graph_bfs_truth_path_test`
  - `Ran 7 tests`
  - `OK`

## Boundary

This goal closes only the bounded Python truth path for
`conjunctive_scan`. It does not claim PostgreSQL correctness or release closure
by itself.
