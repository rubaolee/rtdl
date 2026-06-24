# Goal1174 Pre-Pod Readiness Gate

Date: 2026-04-30

## Verdict

POD EXECUTION IS READY ONLY AFTER SOURCE CLEANLINESS IS RESOLVED.

The pre-pod tooling is ready and reviewed, but the current local working tree is
not claim-grade source material. A pod run from this dirty tree would be
engineering evidence only, repeating the Goal1166 limitation.

## Ready

- Goal1168 closed: Goal1166 live RTX pod artifacts are engineering-accepted and
  claim-grade blocked by dirty source.
- Goal1169 closed: clean-source RTX claim-grade batch plan accepted.
- Goal1170-Goal1172 closed: manifest, runner, intake, preflight, and runbook
  accepted by Gemini review.
- Goal1173 closed: staged source manifest tool accepted by Gemini review.
- Goal1175 closed: staged source archive built, SHA-verified, and accepted by
  Gemini review.
- Focused local tests passed:
  `tests.goal1168_goal1166_live_pod_intake_audit_test`,
  `tests.goal1170_clean_source_rtx_batch_manifest_test`,
  `tests.goal1171_clean_source_rtx_pod_preflight_test`,
  `tests.goal1172_clean_source_rtx_pod_runbook_test`,
  `tests.goal1173_staged_source_archive_manifest_test`.

## Blocker

Current local `git status --short` contains hundreds of changed/untracked paths.
Therefore:

- do not copy this local tree to a pod for claim-grade work;
- do not run `scripts/goal1170_clean_source_rtx_batch_runner.sh` from this dirty
  tree;
- do not promote any future artifact from this dirty state to public wording.

## Allowed Next Source Modes

Mode 1: clean pushed git commit.

- Prepare and push a clean commit containing the accepted Goal1170-Goal1173
  files and their dependencies.
- On the pod, clone the repo and check out that exact commit.
- Run `docs/reports/goal1172_clean_source_rtx_pod_runbook_2026-04-30.md`.

Mode 2: staged source archive.

- Use the Goal1175 archive:
  `docs/reports/goal1175_rtdl_staged_source_2026-04-30.tar.gz`.
- Verify SHA256 before pod use:
  `e6978ed37cdab26737df80efbcb1d34411900a66f9ce1c79063620d128bcce37`.
- Transfer that archive to the pod and extract it as the source tree.
- Treat it as claim-grade only if the archive digest and manifest are preserved
  and reviewed before public wording.

## Not Allowed

- No dirty local rsync/tar copy to pod for claim-grade evidence.
- No manual pod patching without demoting the run to engineering-only evidence.
- No timing-only rows as correctness proof.
- No public RTX wording from Goal1170 artifacts until pod artifacts are copied
  back, intake passes, and external review accepts the evidence.

## Recommendation

Use Mode 1 if possible. It is simpler and less risky than staged archive
workflow. Mode 2 is now available as a reviewed fallback source path if a clean
pushed commit is temporarily impossible.
