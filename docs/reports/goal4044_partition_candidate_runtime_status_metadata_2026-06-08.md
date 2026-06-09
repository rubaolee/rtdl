# Goal4044 Partition Candidate Runtime-Status Metadata

Date: 2026-06-08

## Purpose

Goal4044 fixes stale planner wording for the fixed-radius
`partition_convergence_hybrid` candidate after the Goal4040/4041 executable
preview work.

The old fail-closed planner status, `candidate_requires_native_implementation`,
is retained for backward compatibility and for the prepared front door. Its
meaning is now made explicit: there is no promoted prepared/native/default route
for this candidate. That does not mean the project has no executable preview.

## New Metadata

The front-door description and candidate plan now expose
`candidate_strategy_runtime_status` with these facts:

- `executable_preview_available: true`;
- `prepared_front_door_runtime_executable: true`;
- `prepared_front_door_runtime_status: explicit_cupy_preview_not_promoted`;
- `default_route_promoted: false`;
- `partition_convergence_hybrid_promoted: false`;
- `latest_preview_evidence_goals: Goal4040, Goal4041, Goal4062`;
- promotion blockers:
  - `Goal4041_mixed_timing_not_universal_speed_win`;
  - `prepared_front_door_still_grouped_stream_only`;
  - `host_compact_label_materialization_breaks_resident_output`;
  - `separate_ambiguous_classifier_kernel_not_fused`;
  - `no_promoted_prepared_native_partition_handle`.

Goal4062 follow-up note: the candidate now has an explicit CuPy prepared-summary
preview handle. It is executable and useful for repeated continuation probes, but
it is not a promoted default route and it is not a native prepared partition
producer.

## Decision

This is not a performance promotion. It is a planner/explanation correction.

The next implementation target remains a larger generic continuation:

`fused resident component-label continuation or promoted native partition handle`

That target is large enough to matter because it attacks the actual Goal4041
limits: separate small kernels and host compact-label materialization.

## Boundary

This goal does not promote `partition_convergence_hybrid`, does not change the
prepared front-door default, does not add a native ABI, does not authorize
release action, public speedup wording, broad RT-core wording, whole-app
benchmark wording, hidden dispatch, automatic partner selection, app-specific
native-engine logic, or true-zero-copy wording.
