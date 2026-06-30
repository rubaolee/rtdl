# Goal4005 Partition-Convergence Candidate Front-Door Contract

Date: 2026-06-08

## Verdict

`accept-with-boundary`

Goal4005 names the next dense fixed-radius grouped-union route as an explicit
candidate strategy in the fixed-radius graph component front door:

`partition_convergence_hybrid`

It is deliberately not executable. The planner returns
`candidate_requires_native_implementation`, closes every claim flag, and records
the requirements that must be satisfied before any native implementation can be
treated as promoted.

The same planner also records two rejected default strategies from the recent
evidence chain:

- `direct_side_effect_default`
- `microcell_graph`

## Evidence Incorporated

| Goal | Lesson |
| --- | --- |
| Goal3999 | Benchmark-radius partitioning gives useful but incomplete safe/ambiguous splits; plain grids are insufficient. |
| Goal4001 | Same-root culling is required at actual radii, but the bottleneck is still candidate traversal/root-read work. |
| Goal4002 | Direct side effects are correct but mixed at app level; do not promote them as default. |
| Goal4004 | The existing corrected microcell path is correct but 23x-50x slower; do not promote it as the performance route. |

## Candidate Requirements

The candidate strategy is fail-closed until all of these exist:

- `device_resident_partition_aabb_and_count_columns`
- `safe_full_partition_pair_summary_without_pair_materialization`
- `ambiguous_boundary_pair_rt_traversal`
- `same_contract_parity_against_grouped_stream`
- `deterministic_component_root_policy`
- `explicit_convergence_and_staleness_counters`
- `actual_benchmark_radius_pod_evidence`

## Boundary

This is a planning/contract change only. It does not add a native ABI, change
the default runtime route, authorize release, authorize public speedup wording,
authorize broad RT-core wording, authorize whole-app acceleration wording,
authorize true-zero-copy wording, authorize hidden dispatch, or authorize
app-specific native-engine logic.
