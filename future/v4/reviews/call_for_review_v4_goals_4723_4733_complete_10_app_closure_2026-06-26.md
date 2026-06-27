# Call For Review: V4 Goals4723-4733 Complete 10-App Closure

Date: 2026-06-26

Review target:

- `future/v4/v4_goals_4723_4733_complete_10_app_app_level_benchmark_closure_2026-06-26.md`

Requested verdict labels:

- `approve_goals_4723_4733_as_correct_next_v4_release_path`
- `approve_with_required_amendments`
- `reject_too_app_specific`
- `reject_incomplete_or_still_operator_only`

## Questions

1. Is it correct to block final V4 tag until all 10 benchmark apps have explicit
   app-level V2.14-vs-V4 rows or blocker/no-go rows?
2. Do Goals4723-4733 preserve the principle that RTDL is a language/runtime
   project, not an app-specific kernel collection?
3. Are the remaining five apps handled correctly:
   `robot_collision`, `contact_manifold`, `rtnn`, `spatial_rayjoin`,
   `barnes_hut`?
4. Are the exit gates strict enough to prevent operator/subprobe wins from being
   misrepresented as full-app wins?
5. Should any goal be split, reordered, or killed before execution?

## Non-Authorization

This review must not authorize final public V4 tag, broad V4 speedup wording,
whole-application speedups, all-benchmark speedups, arbitrary callback support,
raw OptiX callbacks, C ABI, embedding, non-Python host bindings, app-specific
native kernels, or using operator/subprobe results as full benchmark-app
evidence.
