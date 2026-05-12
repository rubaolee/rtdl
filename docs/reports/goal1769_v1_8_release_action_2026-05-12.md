# Goal1769: v1.8 Release Action

Status: `v1_8_source_tree_python_rtdl_release_action_authorized`

Date: 2026-05-12

## Decision

The user explicitly authorized the release after the v1.8 documentation,
post-v1.5 rule audit, learner-readiness audit, and distinct-AI review packet
were completed.

This goal performs the v1.8 release action:

- bump `VERSION` to `v1.8`;
- publish the v1.8 source-tree release package under `docs/release_reports/v1_8/`;
- update front-door docs from candidate wording to released source-tree wording;
- preserve source-tree-only, evidence-only, and partner-boundary caveats;
- tag the committed tree as `v1.8` after the final release gate passes.

## Release Boundary

v1.8 is the first source-tree Python+RTDL language release. Python remains the
application/control layer, while RTDL owns the supported RT-shaped kernel
contract and backend bridge. The tracked native release surface has been
migrated to app-agnostic source/ABI terminology.

v1.8 does not claim package-install support, universal whole-application
speedup, Python+partner+RTDL readiness, PyTorch zero-copy, CuPy zero-copy, or
v2.0 partner readiness.

## Protected Local Files

The release staging step must keep the known protected local artifacts out of
git:

- `docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz`
- `id_ed25519_rtdl_codex`
- `rtdl_v0_4.tar.gz`
- `scratch/`

## Validation Command

The release gate is the focused v1.8 gate plus docs/audit/learner/release-action
tests:

```text
PYTHONPATH=src;. py -3 -m unittest ...
```

Observed result:

```text
Ran 266 tests in 8.446s

OK (skipped=1)
```

## Verdict

`accept`: v1.8 is ready to tag and push as the first source-tree Python+RTDL
language release, with the bounded public claims above.
