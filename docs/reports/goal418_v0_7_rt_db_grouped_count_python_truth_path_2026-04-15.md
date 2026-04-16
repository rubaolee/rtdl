# Goal 418 Report: v0.7 RT DB Grouped Count Python Truth Path

Date: 2026-04-15
Goal:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_418_v0_7_rt_db_grouped_count_python_truth_path.md`

## Summary

The bounded `grouped_count` kernel is now implemented in the Python truth path.

Implemented surface:

- `rt.GroupedQuery`
- `mode="db_group"`
- `rt.grouped_count(group_keys=...)`

Bounded authoring shape:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def sales_grouped_count_reference():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(candidates, predicate=rt.grouped_count(group_keys=("region",)))
    return rt.emit(groups, fields=["region", "count"])
```

## Implemented behavior

- grouped queries normalize from mapping inputs
- scan predicates inside the grouped query are applied before grouping
- grouped counts emit stable ordered grouped rows
- empty `group_keys` are rejected

## Verification

Focused test:

- `python3 -m unittest tests.goal418_v0_7_rt_db_grouped_count_truth_path_test`
  - `Ran 3 tests`
  - `OK`

Combined local DB truth-path band:

- `python3 -m unittest tests.goal417_v0_7_rt_db_conjunctive_scan_truth_path_test tests.goal418_v0_7_rt_db_grouped_count_truth_path_test tests.goal419_v0_7_rt_db_grouped_sum_truth_path_test tests.goal423_v0_7_postgresql_db_correctness_test tests.goal424_v0_7_postgresql_db_grouped_correctness_test`
  - `Ran 19 tests`
  - `OK (skipped=2)`

## Boundary

This goal closes only the bounded Python truth path for `grouped_count`.
