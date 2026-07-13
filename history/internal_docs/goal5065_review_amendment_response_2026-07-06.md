# Goal5065 Review Amendment Response

Date: 2026-07-06

Review file:

- `history/internal_docs/review_goal5065_rt_barneshut_hierarchy_traversal_api_design_2026-07-06.md`

Verdict received:

```text
approve_with_required_amendments
```

## Amendment Summary

All blocking findings and required amendments from the review have been
addressed in the implementation report, design plan, call-for-review, manifest,
status entrypoint, README, and tests.

## BF-1 - `BarnesHutOpening` Naming Contradiction

Status: fixed.

Changes:

- Replaced proposed public API examples using `rtdl.BarnesHutOpening(...)` with
  `rtdl.SizeDistanceOpening(max_ratio=...)`.
- Added explicit contract acceptance language that generic API examples must
  avoid app-identity opening names.
- Updated the call-for-review to ask reviewers to block app-identity opening
  names.

Files:

- `history/internal_docs/goal5065_rt_barneshut_hierarchy_traversal_api_design_and_plan_2026-07-06.md`
- `history/internal_docs/call_for_review_goal5065_rt_barneshut_hierarchy_traversal_api_design_2026-07-06.md`

## BF-2 - Completion Boolean Conflict

Status: fixed.

Changes:

- Manifest now distinguishes full paper completion from bounded same-input
  completion:

  ```json
  "paper_reproduction_complete": false,
  "bounded_same_input_reproduction_complete": true
  ```

- Status entrypoint now reports:

  ```text
  status = bounded_same_input_complete
  paper_reproduction_complete = false
  bounded_same_input_reproduction_complete = true
  same_input_comparator_closed = true
  ```

- Current implementation report explains that individual sub-gates correctly
  report `paper_reproduction_complete = false`; only the completion audit can
  report completion for the bounded same-input packet.

Files:

- `Paper-reproduction-apps/rt-barneshut-paper/data/manifest.json`
- `Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py`
- `history/internal_docs/goal5064_rt_barneshut_current_implementation_report_2026-07-06.md`
- `tests/goal5063_rt_barneshut_paper_reproduction_scaffold_test.py`

## RA-1 - Narrow Ratio Must Carry Full Phase Context

Status: fixed.

Changes:

- README, implementation report, design plan, call-for-review, and manifest now
  pair the narrow kernel ratio with the broader reported envelope:

  ```text
  narrow force-kernel ratio:
    RTDL resident_kernel_min 1.1904959678649902 ms
    Author rt_core_force 5.579 ms
    RTDL / Author = 0.21338877359114364

  broader reported envelope:
    RTDL tree prepare + tensor transfer + extension compile + kernel ~= 336.98 ms
    Author preprocessing + execution ~= 99.91 ms
    RTDL / Author ~= 3.37x slower
  ```

Files:

- `Paper-reproduction-apps/rt-barneshut-paper/README.md`
- `Paper-reproduction-apps/rt-barneshut-paper/data/manifest.json`
- `history/internal_docs/goal5064_rt_barneshut_current_implementation_report_2026-07-06.md`
- `history/internal_docs/goal5065_rt_barneshut_hierarchy_traversal_api_design_and_plan_2026-07-06.md`
- `history/internal_docs/call_for_review_goal5065_rt_barneshut_hierarchy_traversal_api_design_2026-07-06.md`

## RA-2 - Min-Vs-Single Sampling Caveat

Status: fixed.

Changes:

- Implementation report and design plan now state that `0.21338877359114364`
  uses RTDL `resident_kernel_min` over the author's single reported force
  value.
- They also report RTDL mean over the same author denominator:

  ```text
  1.2389567852020265 / 5.579 ~= 0.2221
  ```

- Future migration gates are based on RTDL mean, not best min sample.

Files:

- `history/internal_docs/goal5064_rt_barneshut_current_implementation_report_2026-07-06.md`
- `history/internal_docs/goal5065_rt_barneshut_hierarchy_traversal_api_design_and_plan_2026-07-06.md`
- `history/internal_docs/call_for_review_goal5065_rt_barneshut_hierarchy_traversal_api_design_2026-07-06.md`

## RA-3 - Genericity Evidence Must Differ Substantially

Status: fixed in plan.

Changes:

- Goal5070 now requires a non-RT-BarnesHut genericity smoke with a
  substantially different reducer and opening configuration.
- The design explicitly rejects another inverse-square force field as
  sufficient proof.

File:

- `history/internal_docs/goal5065_rt_barneshut_hierarchy_traversal_api_design_and_plan_2026-07-06.md`

## RA-4 - Quantified Regression Gate

Status: fixed.

Changes:

- Goal5069 migration acceptance now specifies:

  ```text
  resident_kernel_mean <= 1.37 ms
  ```

  This is no more than about +10% over the current
  `1.2389567852020265 ms` RTDL mean baseline.

File:

- `history/internal_docs/goal5065_rt_barneshut_hierarchy_traversal_api_design_and_plan_2026-07-06.md`

## Verification

Commands run:

```text
py -m unittest tests.goal5063_rt_barneshut_paper_reproduction_scaffold_test
```

Result:

```text
Ran 25 tests in 3.127s
OK
```

Status entrypoint read-back:

```text
paper_reproduction_complete = false
bounded_same_input_reproduction_complete = true
same_input_comparator_closed = true
status = bounded_same_input_complete
```

## Revised Authorization Request

With the amendments above, Goal5066 should remain limited to a
contract/schema-only goal:

```text
AggregateHierarchy3D
PreparedAggregateHierarchy3D
SizeDistanceOpening
aggregate_frontier_reduce_3d
generic reducer contracts
generic continuation columns
```

It should not yet perform a backend rewrite or promote paper-app comparator
machinery into RTDL core.
