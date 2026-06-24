# Goal1736 v1.6.11 Commit-Ready Inventory

## Verdict

`inventory_ready_with_exclusions`

The workspace contains the release-candidate evidence chain and final decision artifacts for v1.6.11, plus older migration/report artifacts from the same long session. It also contains local/protected files that must not be staged for release.

## Commit Core For Final Decision Trail

These files are the final decision trail and should be included with the release-candidate evidence commit:

- `docs/reports/goal1729_v1_6_11_release_candidate_evidence_packet_2026-05-12.md`
- `tests/goal1729_v1_6_11_release_candidate_evidence_packet_test.py`
- `docs/reviews/goal1730_claude_review_goal1729_v1_6_11_release_candidate_packet_2026-05-12.md`
- `docs/reviews/goal1731_gemini_review_goal1729_v1_6_11_release_candidate_packet_2026-05-12.md`
- `docs/reports/goal1732_v1_6_11_final_release_decision_note_2026-05-12.md`
- `tests/goal1732_v1_6_11_final_release_decision_note_test.py`
- `docs/reviews/goal1733_claude_review_goal1732_final_release_decision_note_2026-05-12.md`
- `docs/reviews/goal1734_gemini_review_goal1732_final_release_decision_note_2026-05-12.md`
- `docs/reports/goal1735_v1_6_11_final_release_consensus_2026-05-12.md`
- `tests/goal1735_v1_6_11_final_release_consensus_test.py`
- `docs/reports/goal1736_v1_6_11_commit_ready_inventory_2026-05-12.md`
- `tests/goal1736_v1_6_11_commit_ready_inventory_test.py`

## Evidence Chain To Include

The commit should also include the supporting reports, reviews, tests, and generated JSON artifacts from Goals 1668 through 1728 that created the app-agnostic native migration, pod validation, Goal1659/Goal1660 evidence, and boundary companion evidence.

Key supporting groups:

- app-agnostic native migration reports/tests: Goals 1668, 1672, 1676, 1681, 1682, 1688, 1690, 1695, 1697, 1699, 1704, 1708, 1711
- pod/hardware reports/tests and reviews: Goals 1714, 1716, 1718, 1720, 1722, 1723, 1726
- external reviews: Goals 1715, 1717, 1719, 1721, 1724, 1727, 1728, 1730, 1731, 1733, 1734
- current-version Goal1659 pod artifacts: `docs/reports/goal1659_*_optix.json`
- v1.0/current Goal1660 artifact pairs and raw runner summaries: `docs/reports/goal1660_v1_*.json`, Goal1718 raw JSON, Goal1720 adapter raw JSON

## Code Changes To Include

The release evidence depends on code changes in:

- `Makefile`
- `scripts/goal1660_v1_6_11_vs_v1_0_perf_matrix.py`
- `src/rtdsl/embree_runtime.py`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/oracle_runtime.py`
- app-agnostic native/runtime migration files under `src/native/**` and `src/rtdsl/**`
- corresponding tests under `tests/goal*.py`

These should be reviewed with `git diff` before staging because the worktree is large and contains long-session edits.

## Do Not Stage

Do not stage local/protected files:

- `docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz`
- `id_ed25519_rtdl_codex`
- `rtdl_v0_4.tar.gz`
- `scratch/`

The protected Goal1204 tarball was explicitly excluded from pod sync and should remain untouched.

## Pre-Tag Checklist

Before any release/tag command:

1. Re-run the focused final gate.
2. Inspect `git status --short`.
3. Stage only the intended source, report, review, test, and evidence artifacts.
4. Do not stage protected/local files.
5. Commit.
6. Only tag/push if the user explicitly authorizes that release operation.

## Boundary

This is an inventory, not a staging command and not a release command.
