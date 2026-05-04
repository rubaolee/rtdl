# RTDL v1.0 Tag Preparation

Status: draft release candidate for `v1.0`; not released.

Date: 2026-05-04

## Release Boundary

The future `v1.0` tag should represent the app-shaped RTDL proof release:

- current docs explain the Python-facing RTDL model clearly;
- tutorials and app/example docs are usable entry points;
- app acceleration inventory documents what each app accelerates and what
  remains outside the RT sub-path;
- RTX public wording is limited to `12` reviewed bounded sub-path rows;
- blocked, not-reviewed, and non-NVIDIA rows are explicitly bounded;
- v1.5 and v2.0 follow-up scope is documented without being claimed as already
  complete.

## Requirements Already Satisfied For Candidate Prep

- The current released version remains `v0.9.8`.
- v1.0 positioning and engine-customization boundary docs exist.
- Front page and tutorial polish have recent focused tests and external review
  consensus.
- No immediate pod is required for the currently documented v1.0 proof scope.

## Requirements Before Tag

- Complete final v1.0 release-candidate audit.
- Complete external-AI review of this v1.0 package and save it under
  `docs/reports/`.
- Save Codex consensus for the final v1.0 package.
- Run the agreed release-surface and full-discovery test gates.
- Update `VERSION` from `v0.9.8` to `v1.0` only after final authorization.
- Commit release docs before tagging.

## Tag Commands

Do not run these until final authorization is saved:

```bash
git tag -a v1.0 -m "Release RTDL v1.0"
git push origin main
git push origin v1.0
```

## Boundary

This file is tag preparation only. It is not a release authorization.
