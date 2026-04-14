# Goal 378: v0.6 total doc review, update, and verification

## Why this goal exists

The `v0.6` line now has:

- front-door references
- a release package
- many goal reports
- real-data evaluation reports
- audit and consensus documents

That means documentation risk is now a release blocker by itself.

## Scope

In scope:

- total review of the public/reviewer-facing `v0.6` documentation surface
- fix or call out stale wording, missing links, wrong status labels, and weak release wording
- verify that major claims still point to real saved evidence

Out of scope:

- writing a new large tutorial line from scratch
- re-running all technical evaluations
- release tagging

## Required review targets

At minimum, this gate should cover:

- `README.md`
- `docs/README.md`
- `docs/release_reports/v0_6/`
- `docs/v0_6_graph_workloads_consensus.md`
- the key `goal37x` reports that the release package depends on

## Exit condition

This goal is complete when the repo has:

- a saved total doc review report
- any bounded doc fixes applied
- at least one external review
- a saved Codex consensus note
- an honest verdict on whether the `v0.6` doc surface is release-clean enough
