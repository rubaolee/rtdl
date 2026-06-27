# v2.0 Release-Hold Checkpoint Archive

Status: archived. The release hold was cleared by the Goal2322 3-AI consensus
and the v2.0 release action.

This page records the current release-edge rule:

```text
Prepare everything needed for v2.0, keep normal commits synced online, but do
not tag, publish a GitHub release, move release branches, or announce final
v2.0 until the user explicitly presses the release button.
```

## Prepared State

The current public surface has been cleaned for release review:

- learner docs now point to current v2.0-facing material;
- advanced design and app implementation notes are under `docs/research/`;
- audit, process, reviews, reports, and history are under audit/history lanes;
- examples are organized around current public wrappers and job-oriented entry
  points;
- root-level generated/proof/schema/build clutter has been moved under the
  appropriate source, example, script, or history lane;
- scripts and tests now have reader indexes.

## Evidence Packet

| Area | Evidence |
| --- | --- |
| Documentation architecture | `docs/reports/goal2104_doc_reengineering_summary_2026-05-15.md` |
| Gemini review of doc re-engineering | `docs/reviews/goal2105_gemini_review_goal2104_doc_reengineering_summary_2026-05-15.md` |
| Front-page navigation gate | `tests.goal2101_frontpage_navigation_link_audit_test` |
| Examples organization gate | `tests.goal2102_examples_directory_organization_audit_test` |
| Root/scripts/tests organization gate | `tests.goal2103_root_scripts_tests_organization_audit_test` |
| v2.0 pre-release candidate | `docs/release_reports/v2_0_pre_release_candidate.md` |
| Streaming witness v2 perf table | `docs/reports/goal2085_v2_perf_table_after_streaming_witness_update_2026-05-15.md` |

## Historical Not-Yet-Allowed Actions

At the time of this checkpoint, these actions required explicit user release
authorization:

- create or move a `v2.0` tag;
- create a GitHub release;
- publish final v2.0 release notes as released;
- change wording from hold to final release;
- claim package-install support unless packaging metadata is present and tested;
- claim broad RT-core, arbitrary partner, or universal whole-app acceleration.

## Superseded Next Safe Work

Before the release button, safe work was:

- keep docs, reports, reviews, and tests synced to `origin/main`;
- gather remaining external reviews;
- run additional local or pod validation;
- update pre-release evidence docs with exact artifact paths;
- fix discovered documentation, link, or example issues.
