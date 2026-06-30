# Goal4806 Released-RTDL RayJoin Attempt Archive

This directory contains the Goal4806 exploratory work that was removed from the
main project surface on 2026-06-30.

Reason for archival:

- The active Goal4806 objective is to reproduce RayJoin Section 5.7 as a normal
  user using released RTDL V4.0.0 + Python + Numba.
- Much of the work captured here modified RTDL source/runtime code, created
  internal probes, or recorded partial evidence from a dirty development tree.
- Those materials must not remain in the public docs, scripts, tests, or source
  surface because they can mislead users and reviewers into treating an
  unreleased runtime experiment as released V4 capability.

Contents:

- `goal4806_tracked_worktree_diff.patch`: snapshot of the tracked source/script
  edits before they were reverted.
- `docs_reports/`: moved Goal4806 reports and JSON/JSONL artifacts.
- `docs_reviews/`: moved Goal4806 call-for-review files.
- `scripts/`: moved temporary Goal4806 probe/data-acquisition scripts.
- `tests/`: moved temporary Goal4806 tests.
- `tools_tmp/`: moved temporary author-code patch helpers and run scripts.

Current project rule:

- Do not restore these files into the main surface unless a later explicit goal
  authorizes a new post-release runtime-development track.
- To finish Goal4806, use a clean released V4.0.0 environment and a user-layer
  paper-reproduction app.  Do not edit `src/rtdsl/**` or `src/native/**`.

