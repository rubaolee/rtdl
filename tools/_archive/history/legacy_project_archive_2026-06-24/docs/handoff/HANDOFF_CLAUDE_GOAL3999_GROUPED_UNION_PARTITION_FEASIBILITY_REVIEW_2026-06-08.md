# Handoff: Claude Review Goal3999 Grouped-Union Partition Feasibility

Please perform a read-only independent review of Goal3999 and write the review
to:

`docs/reviews/goal4000_claude_review_goal3999_grouped_union_partition_feasibility_2026-06-08.md`

## Files To Inspect

- `docs/reports/goal3999_grouped_union_partition_feasibility_2026-06-08.md`
- `docs/reports/goal3999_grouped_union_partition_feasibility.json`
- `scripts/goal3999_grouped_union_partition_feasibility_probe.py`
- `tests/goal3999_grouped_union_partition_feasibility_test.py`
- `docs/research/future_version_to_do_list.md`
- Context reports:
  - `docs/reports/goal3996_grouped_union_extended_telemetry_sweep_pod.json`
  - `docs/reports/goal3998_grouped_union_source_root_payload_negative_probe_2026-06-08.md`
  - `docs/reports/goal3989_rt_dbscan_grouped_union_atomic_telemetry_2026-06-08.json`

## Questions

1. Does Goal3999 correctly separate the current RT-DBSCAN benchmark radii
   (`clustered3d=0.055`, `road3d=0.030`, `ngsim_dense=0.012`) from the
   radius-`0.5` stress evidence used in Goals3996/3998?
2. Is the partition feasibility method internally consistent: do
   `safe_full + safe_skip + ambiguous` pair upper bounds account for all pairs?
3. Is the conclusion justified that a plain uniform-grid rewrite is insufficient
   and the next direction should be a generic hybrid primitive:
   device-resident partitions for safe summaries plus RT traversal for
   ambiguous boundary pairs?
4. Does the report avoid release, speedup, broad RT-core, true-zero-copy,
   paper-reproduction, automatic-dispatch, and app-specific-engine overclaims?
5. Are there any design risks before the next native implementation goal?

## Expected Verdict

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
Lead with findings by severity, then verdict and required-before-next-step items.
