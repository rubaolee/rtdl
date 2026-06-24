# Goal4062 Prepared Partition-Convergence Summary Preview

Date: 2026-06-09

## Purpose

Goal4059 made the RT-DBSCAN column-signature path faster by adding a direct
Numba component-size signature front door. The remaining grouped-union debt is
now in the reusable fixed-radius graph-component runtime itself: repeated
component-label or component-signature probes still need a clean way to reuse
the same partition-summary columns instead of rebuilding them as an ad hoc
caller convention.

Goal4062 adds that explicit runtime shape:

`V28PreparedFixedRadiusPartitionConvergenceSummaryCupyPreview3D`

and the public helper:

`prepare_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(...)`.

The prepared handle owns one explicit CuPy preview summary for the generic
`fixed_radius_partition_convergence_summary_3d` stream. It then exposes two
generic consumers:

- `run_v2_8_fixed_radius_partition_convergence_component_labels_cupy_prepared_preview_3d(...)`;
- `run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_preview_3d(...)`.

Both consumers pass the existing `partition_summary=` into the established
component-label/signature previews and mark the output metadata with
`prepared_partition_summary_handle: true`,
`prepared_partition_summary_reused: true`, and
`explicit_cupy_preview_not_promoted`.

## What Changed

- Added an explicit prepared CuPy preview handle for partition-summary reuse.
- Added optional same-contract validation at prepare time.
- Added reusable metadata digests for the prepared summary so timing artifacts
  can distinguish summary build cost from continuation replay cost.
- Refreshed the partition-convergence candidate status:
  - `prepared_front_door_runtime_executable: true`;
  - `prepared_front_door_runtime_status: explicit_cupy_preview_not_promoted`;
  - `latest_preview_evidence_goals: Goal4040, Goal4041, Goal4062`;
  - stale blocker `no_prepared_native_or_partner_partition_handle` replaced by
    `no_promoted_prepared_native_partition_handle`.

## Boundaries

This is a prepared preview handle, not a promoted runtime route.

Goal4062 does not add a native ABI. It does not promote
`partition_convergence_hybrid` as a default route; in plainer gate language,
there is no promoted default route. It does not choose partners automatically.
It does not authorize public speedup wording, release wording, broad RT-core
wording, whole-app benchmark wording, hidden dispatch, app-specific native
engine logic, or true-zero-copy wording.

The next larger engineering step remains a fused resident component-label or
component-signature continuation, or a promoted native partition producer that
can beat the grouped-stream route on representative workloads.

## Validation

Added:

- `tests/goal4062_prepared_partition_convergence_summary_preview_test.py`.
- `scripts/goal4062_prepared_partition_summary_timing.py`.
- `docs/reports/goal4062_prepared_partition_summary_timing_pod.json`.
- `docs/reports/goal4062_prepared_partition_summary_timing_pod.stdout.txt`.

The test verifies:

- the prepared handle and wrapper functions are available from `rtdsl`;
- the candidate metadata records the prepared preview while keeping promotion
  false;
- the new prepared-handle source section does not contain app-specific
  vocabulary;
- when CuPy is available, one prepared summary can feed both component labels
  and component-size signatures with matching results.

The timing script compares one-shot component-size signature execution against
prepared-summary replay on representative clustered and road-like point clouds.
It records replay-only speedups and three-run amortized speedups separately so a
reader can see whether the prepared handle is useful for repeated workloads
without confusing that with a single-call speedup claim.

Pod evidence at source commit `ddcc0680` on RTX 4000 Ada:

| Profile | Points | Replay Speedup Min | Three-Run Amortized Median |
| --- | ---: | ---: | ---: |
| clustered3d_1024 | 1024 | 5.576x | 2.172x |
| road3d_1024 | 1024 | 5.619x | 2.230x |
| clustered3d_4096 | 4096 | 6.445x | 2.285x |
| road3d_4096 | 4096 | 6.275x | 2.266x |
| clustered3d_8192 | 8192 | 8.826x | 2.437x |
| road3d_8192 | 8192 | 6.480x | 2.312x |

This is positive prepared-replay evidence for a generic runtime pattern. It is
not a whole-app result, not a release result, and not a broad RT-core speedup
claim.
