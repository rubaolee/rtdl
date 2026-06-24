# Claude Review: Phoenix V3 M4 No-Git Source Identity Amendment

Date: 2026-06-20

Scope: external review of the execution amendment discovered during pod
preflight. The intended Phoenix current tree on the pod is an expanded
worktree, not a git checkout.

## Context

During preflight, `/root/rtdl_v3_rebuild_20260620/current` was confirmed as the
Phoenix current tree with `VERSION=v3-rebuild-2026-06-20` and built native
libraries, but it has no `.git` directory. The older
`/workspace/rtdl_v2_vs_v3_pod_20260620_024503/v3.0.2` tree has git provenance,
but it is not the Phoenix current tree.

Codex proposed a fallback source-identity path:

- use `git rev-parse HEAD` when git provenance is available;
- otherwise write `current_commit.txt=no_git_worktree`;
- write `source_version.txt` from `VERSION`;
- write `source_manifest.sha256` over the measured scripts.

## Verdict

VERDICT: ACCEPT_WITH_REQUIRED_AMENDMENTS

## Required Amendments

- `source_manifest.sha256` must also cover the built native libraries/binaries
  actually exercised by M9/M10/M11/M18/M23/M28, not just the measurement
  scripts.
- Before falling back, the probe must actively check for retrievable git
  provenance or build provenance elsewhere and record what was checked.
- The final report/packet must carry a prominent caveat that source identity is
  VERSION-string plus file-hash based, not git-commit based.
- `source_version.txt` value `v3-rebuild-2026-06-20` must be cross-checked
  against the expected Phoenix V3 M4 baseline identity and recorded as pass/fail.

## Risk Notes

- VERSION plus a small hash set is weaker than a git commit and can miss drift
  in source files, build scripts, or dependencies outside the hashed set.
- Built native libraries without source commit provenance make after-the-fact
  binary questions harder unless the libraries themselves are hashed.
- A stripped expanded worktree should be called out explicitly because it
  changes how much trust reviewers can place in the identity artifacts.

## Codex Follow-Up

Codex applied the required amendments to:

- `docs/rebuild/v3/phoenix_v3_m4_grouped_continuation_rerun_packet_2026-06-20.json`
- `docs/rebuild/v3/phoenix_v3_m4_grouped_continuation_rerun_packet_2026-06-20.md`
- `tests/v3_phoenix_m4_grouped_continuation_packet_test.py`

The amended fallback now records:

- `source_identity_check.txt` with expected version
  `v3-rebuild-2026-06-20` and `source_version_match=pass`;
- `provenance_search.txt` with searched git/build provenance locations;
- `source_manifest.sha256` including `build/librtdl_embree.so`,
  `build/librtdl_optix.so`, and `src/` plus `scripts/` source files;
- a caveat that no-git source identity is file-hash based, not git-commit
  based.

