# Goal 234: External User UX Cleanup

Date: 2026-04-11
Status: implemented

## Goal

Resolve the specific public-surface issues identified by the external
fresh-clone user-experience audit so the release-prep package is no longer
misleading for first-time users.

## Acceptance

- public onboarding/tutorial pages use a consistent `python` command convention
- public nearest-neighbor example docs no longer overclaim unsupported
  `optix` / `vulkan` CLI flags
- maintainer-local absolute paths are removed from the public workload cookbook
- the external UX audit is preserved in the release-prep audit trail

## Boundary

- docs-only cleanup
- no `VERSION` bump
- no tag
