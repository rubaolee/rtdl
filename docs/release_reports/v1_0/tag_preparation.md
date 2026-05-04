# RTDL v1.0 Tag Record

Status: released as `v1.0`.

Date: 2026-05-04

## Release Boundary

The `v1.0` tag represents the app-shaped RTDL proof release:

- current docs explain the Python-facing RTDL model clearly;
- tutorials and app/example docs are usable entry points;
- app acceleration inventory documents what each app accelerates and what
  remains outside the RT sub-path;
- RTX public wording is limited to `12` reviewed bounded sub-path rows;
- blocked, not-reviewed, and non-NVIDIA rows are explicitly bounded;
- v1.5 and v2.0 follow-up scope is documented without being claimed as already
  complete.

## Release Scope Satisfied

- The current released version is `v1.0`.
- v1.0 positioning and engine-customization boundary docs exist.
- Front page and tutorial polish have recent focused tests and external review
  consensus.
- No immediate pod is required for the currently documented v1.0 proof scope.

## Requirements Satisfied Before Tag

- Completed final v1.0 release-candidate audit.
- Completed external-AI review of this v1.0 package and saved it under
  `docs/reports/`.
- Saved Codex consensus for the final v1.0 package.
- Ran the agreed release-surface and full-discovery test gates.
- Saved final authorization before updating `VERSION`.
- Updated `VERSION` from `v0.9.8` to `v1.0` as part of the release action.

## Tag Commands

The release action uses:

```bash
git tag -a v1.0 -m "Release RTDL v1.0"
git push origin main
git push origin v1.0
```

## Boundary

This file records the tag procedure. It does not widen the v1.0 claim scope.
