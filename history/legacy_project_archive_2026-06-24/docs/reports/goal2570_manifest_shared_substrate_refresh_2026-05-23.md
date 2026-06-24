# Goal2570: Manifest Shared-Substrate Refresh

Date: 2026-05-23

## Scope

Goal2570 refreshes the benchmark-app evidence manifest after Goals2565-2569.
The manifest now records the shared device-column descriptor and grouped
reduction substrate contracts, so reviewers can see the latest common runtime
interfaces before reading app-specific closeouts.

## Change

Updated `docs/reports/goal2566_benchmark_app_evidence_manifest_2026-05-23.json`
to include:

- `DeviceColumnDescriptor`
- `rtdl.grouped_reduction.v1`
- grouped dispatcher metadata bridge report
- robot group-any metadata bridge report
- fail-closed grouped overflow policy

## Boundary

This is a manifest refresh only. It does not authorize public release wording,
speedup claims, true zero-copy claims, or new native backend support.

## Validation

Updated `tests/goal2566_benchmark_app_evidence_manifest_test.py` to verify the
new shared-substrate report paths and grouped-reduction contract fields.

No pod was used.
