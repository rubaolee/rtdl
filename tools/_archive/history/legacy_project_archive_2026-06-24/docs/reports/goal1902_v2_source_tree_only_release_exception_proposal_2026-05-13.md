# Goal1902 - v2 Source-Tree-Only Release Exception Proposal

Status: proposal-needs-3ai-review

Date: 2026-05-13

## Scope

Goal1902 proposes one possible way to close the Goal1814 package-install blocker
without adding packaging metadata before v2.0: release v2.0 as explicitly
source-tree-only, with no package-install promise.

This is a proposal only. It does not authorize v2.0 release wording.

## Proposed Policy

RTDL v2.0 may remain source-tree-only if the final v2.0 release packet says so
plainly and 3-AI consensus accepts that policy.

Allowed wording:

```text
RTDL v2.0 is used from the repository source tree. Set `PYTHONPATH=src:.` before
running examples, tests, or scripts. Package-install support is not part of this
release.
```

Blocked wording:

- `pip install rtdl`
- `pip install -e .`
- `RTDL is available as a Python package`
- `Install RTDL from PyPI`
- `Package-install support is validated`

## Rationale

Source-tree-only is honest for the current repo because:

- no packaging metadata exists;
- native backend builds are still local environment operations;
- partner dependencies are optional, heavy, and backend-specific;
- public examples and validation commands already use `PYTHONPATH=src:.`;
- v2.0 engineering risk is concentrated in partner-device contracts and pod
  evidence, not packaging.

## Required Review

This proposal can close the package-install blocker only if:

1. Codex reviews and accepts the wording.
2. Claude or Gemini reviews the proposal.
3. A second distinct external AI reviews the proposal.
4. A final 3-AI consensus file explicitly accepts source-tree-only v2.0 as a
   release boundary.

If reviewers reject this policy, v2.0 must instead add and validate packaging
metadata before release.

## Boundary

This proposal does not weaken any other v2.0 blocker:

- RTX pod evidence is still required for road-hazard prepared reuse.
- Whole-app and broad RT-core speedup claims remain evidence-limited.
- Arbitrary PyTorch/CuPy acceleration remains blocked outside explicit RTDL
  primitive calls.
- Final v2.0 release still requires a refreshed release packet and consensus.
