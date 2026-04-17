# Goal 156: v0.2 Release Refresh After OptiX Robustness

## Why

Goal 154 closed the final release-audit and tag-preparation package, but Goal
155 then repaired a real Linux release-path robustness problem in the OptiX
build pipeline.

So the canonical v0.2 release set should be refreshed once more to include that
repair explicitly instead of pretending the release story stopped at Goal 153.

## Scope

- update the canonical v0.2 release docs to include Goal 155
- update the release-audit script to require Goal 155 coverage
- keep the release story honest:
  - the OptiX Linux path issue was real
  - it is now repaired
  - this strengthens release readiness without broadening scope

## Acceptance

- `docs/release_reports/v0_2/` explicitly incorporates Goal 155
- `scripts/goal154_release_audit.py` includes Goal 155 in its release checks
- the refreshed release package is reviewed before it is treated as online
