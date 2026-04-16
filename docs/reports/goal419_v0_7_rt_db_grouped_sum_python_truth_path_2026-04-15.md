# Goal 419 Report: v0.7 RT DB Grouped Sum Python Truth Path

Date: 2026-04-15
Goal:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_419_v0_7_rt_db_grouped_sum_python_truth_path.md`

## Summary

The bounded `grouped_sum` kernel is now implemented in the Python truth path.

Implemented surface:

- `rt.GroupedQuery`
- `rt.grouped_sum(group_keys=..., value_field=...)`

Bounded authoring shape:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def sales_grouped_sum_reference():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(
        candidates,
        predicate=rt.grouped_sum(group_keys=("region",), value_field="revenue"),
    )
    return rt.emit(groups, fields=["region", "sum"])
```

## Implemented behavior

- grouped sum runs over filtered denormalized rows
- emitted rows are stable and grouped by the declared keys
- integer-looking sums are emitted as integers in the bounded truth path
- empty `value_field` is rejected

## Verification

Focused test:

- `python3 -m unittest tests.goal419_v0_7_rt_db_grouped_sum_truth_path_test`
  - `Ran 3 tests`
  - `OK`

Combined local DB truth-path band:

- `python3 -m unittest tests.goal417_v0_7_rt_db_conjunctive_scan_truth_path_test tests.goal418_v0_7_rt_db_grouped_count_truth_path_test tests.goal419_v0_7_rt_db_grouped_sum_truth_path_test tests.goal423_v0_7_postgresql_db_correctness_test tests.goal424_v0_7_postgresql_db_grouped_correctness_test`
  - `Ran 19 tests`
  - `OK (skipped=2)`

## Boundary

This goal closes only the bounded Python truth path for `grouped_sum`.
