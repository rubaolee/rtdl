# Goal4277 v2.10 Release Artifact Alignment

Status: local source-tree release-artifact cleanup after the v2.10 milestone
tag and current learner-doc reorganization.

## Purpose

After the v2.10 source-tree milestone tag and the top-level tutorial cleanup,
three release artifacts needed alignment:

- the root `VERSION` marker still said `v2.6`;
- `docs/release_reports/` had a historical v2.6 package but no v2.10 package;
- `docs/partner_acceleration_boundaries.md` named three stale Goal4266/4267/4270
  report paths.

This goal fixes those artifacts without changing any benchmark code,
performance claim, backend behavior, or the already-published `v2.10` tag.

## Tag Position

| Item | Value |
| --- | --- |
| Current source-tree surface | `v2.10` |
| Existing tag | `v2.10` |
| Tag commit observed before this cleanup | `2888b5ba` |
| Current `main` commit observed before this cleanup | `1b66bddf` |
| Policy | Do not move the existing tag without explicit maintainer authorization |

The post-tag documentation cleanup commits keep the same v2.10 source-tree
surface. They do not widen release claims and do not authorize moving the tag.

## File Operations

| File | Old problem | Action | Explanation |
| --- | --- | --- | --- |
| `VERSION` | Root marker still said `v2.6`. | Updated to `v2.10`. | Current front page, docs, examples, tutorials, and release consensus all identify the active source-tree surface as v2.10. |
| `docs/release_reports/v2_10/README.md` | No v2.10 release package existed under `docs/release_reports/`. | Added a source-tree release package. | Gives reviewers one stable place for v2.10 scope, benchmark app surface, smoke commands, evidence links, and non-claims. |
| `docs/partner_acceleration_boundaries.md` | Stale inline report paths for Goal4266, Goal4267, and Goal4270. | Replaced with existing report filenames. | Keeps public partner guidance tied to real evidence artifacts. |
| `tests/goal4277_v2_10_release_artifact_alignment_test.py` | No focused test covered the v2.10 package and version marker. | Added focused release-artifact tests. | Fails closed if the marker regresses, the package uses old example paths, or stale report names return. |

## Boundaries

This is not a performance rerun, pod validation, package-install release, or
new 3-AI release consensus. The v2.10 release authorization remains the Goal4270
3-AI consensus. This cleanup only makes current source-tree artifacts internally
consistent after later learner-doc work.

## Validation

Focused validation command:

```bash
PYTHONPATH=src:. python -m unittest \
  tests.goal4277_v2_10_release_artifact_alignment_test \
  tests.goal4271_v2_10_user_doc_cleanup_test \
  tests.goal4274_current_doc_recheck_test \
  tests.goal4276_top_level_tutorial_reorganization_test \
  tests.goal4267_v2_10_milestone_release_packet_test \
  tests.goal4270_v2_10_milestone_release_consensus_test
```

Result recorded after implementation: 23 tests ran, all passed.
