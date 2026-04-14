# Goal 376: v0.6 release surface cleanup

## Why this goal exists

The `v0.6` graph line now has enough bounded technical substance that the repo
needs a proper release-facing package and front-door links for it.

This goal is about release-surface cleanup only. It does not make a release tag.

## Scope

In scope:

- add a canonical `v0.6` release package under `docs/release_reports/v0_6/`
- link that package from the repo front door and docs index
- keep `v0.5.0` as the current released version until an actual `v0.6` tag exists

Out of scope:

- changing the current released version number on the front page
- tagging `v0.6.0`
- new workload or backend work

## Exit condition

This goal is complete when the repo has:

- a saved `v0.6` release package
- front-door/docs-index links to that package
- a saved external review
- a saved Codex consensus note
