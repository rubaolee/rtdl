# RTDL v1.6 Tag Preparation

Status: completed. The `v1.6` annotated tag was published after final 3-AI
release consensus and explicit release/tag authorization.

## Candidate Tag

```text
v1.6
```

## Validation Commit

The Goal 1605 validation evidence was collected at:

```text
ae92aa8eabc969da856ea730c7b82e19345ca3a3
```

## Tag Target Commit

The final tag target is the reviewed release commit that contains:

- this `docs/release_reports/v1_6/` package;
- the final 3-AI release consensus;
- no uncommitted release-package changes.

Because this release package and final consensus were committed after Goal
1605, the Goal 1605 validation commit above is evidence provenance, not the
final tag target.

## Required Preconditions

- Worktree clean except known unrelated local artifacts.
- Release package present at `docs/release_reports/v1_6/`.
- Final 3-AI release consensus accepted.
- Final tag target commit is the reviewed commit that contains the release
  package and final consensus.
- Windows source-tree validation recorded.
- Linux source-tree validation recorded.
- Real NVIDIA OptiX validation recorded for the scoped stable surface.
- No package-install claim is added.
- No whole-app speedup claim is added.
- No broad NVIDIA RTX/GPU claim is added.
- No true zero-copy claim is added.
- `COLLECT_K_BOUNDED` remains pending/experimental.
- Native internals are not described as fully app-agnostic.
- Vulkan, HIPRT, and Apple RT remain frozen/proof surfaces before v2.1.
- Explicit release/tag authorization is confirmed.

## Suggested Final Verification Before Tag

```sh
PYTHONPATH=src:. python -m unittest \
  tests.goal1605_v1_6_windows_linux_optix_validation_test \
  tests.goal1604_v1_6_blocked_claim_regression_gate_test \
  tests.goal1603_v1_6_stable_native_path_app_leakage_audit_test \
  tests.goal1602_v1_6_public_docs_overclaim_audit_test \
  tests.goal1601_v1_6_release_surface_proposal_test \
  tests.goal1600_v1_6_python_rtdl_readiness_gate_test
```

## Tag Command Shape

The tag action used this command shape after the required preconditions were
complete:

```sh
git tag -a v1.6 -m "RTDL v1.6"
git push origin v1.6
```

This document does not authorize moving `v1.6`, moving `v1.5`, moving `v1.0`,
or broadening the public claims listed above.
