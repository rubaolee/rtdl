# Goal1722 Goal1660 Manifest Reality Correction After v1.0 Pod Adapter

## Verdict

`accept-with-boundary`

Goal1660's v1.6.11 versus v1.0 manifest now matches the command support observed on the pod during Goal1718 and Goal1720. The generator no longer plans unsupported v1.0 Embree baselines for legacy OptiX-only scripts that do not expose `--backend`; it keeps those rows as current-only evidence and only compares v1.0 where a real command shape exists.

## What Changed

- Added a tagged-v1.0 script inspection step to detect whether a baseline script actually supports `--backend`.
- Adapted legacy v1.0 OptiX-only rows by dropping the unsupported `--backend optix` pair while preserving the same app, engine, scale, and artifact path.
- Marked the 12 unsupported v1.0 Embree rows as `current_only_v1_0_missing_engine_selector` instead of `planned`.
- Added per-row fields for `script_supports_backend_in_v1_0` and `v1_0_command_shape`.
- Tightened validation so unsupported Embree baselines cannot silently re-enter the cross-version plan.

## Updated Counts

- Matrix rows: `36`
- Planned comparable rows: `16`
- Blocked/excluded/current-only rows: `20`
- Status distribution: `planned=16`, `current_only_v1_0_missing_engine_selector=12`, `excluded=7`, `shared_primitive_alias=1`

This matches the Goal1720 pod result: all 15 planned v1.0 OptiX rows have artifacts, the database Embree row has a real v1.0 baseline artifact, and the remaining 12 v1.0 Embree rows are unsupported by the tagged v1.0 scripts rather than failed performance rows.

## Boundary

This correction does not claim a public speedup, publish v1.6.11, or authorize a release tag. It only makes the manifest fail closed against decorative same-engine rows. Final release language still requires parity review over the completed artifacts and the existing multi-AI release gates.
