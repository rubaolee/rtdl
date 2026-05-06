# RTDL v1.5 Tag Preparation

Status: prepared, but no tag action is authorized by this file.

The current released version remains `v1.0` until an explicit release/tag action
is performed.

## Candidate Tag

```text
v1.5
```

## Required Preconditions

- Worktree clean.
- Release gate passes with all required gates complete.
- Release docs and public wording package present.
- Current source usage remains `PYTHONPATH=src:. python ...`.
- No package-install claim is added.
- No whole-app speedup, broad NVIDIA RTX, broad GPU, or broad backend speedup
  wording is added.
- `COLLECT_K_BOUNDED` remains experimental and deferred to v1.5.1.
- Vulkan, HIPRT, and Apple RT remain frozen before v2.1.
- User gives explicit release/tag approval.

## Suggested Verification Before Tag

```sh
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1398_v1_5_standalone_release_gate_test \
  tests.goal1406_v1_5_benchmark_evidence_matrix_test \
  tests.goal1405_v1_5_support_maturity_matrix_test \
  tests.goal1402_v1_5_pending_app_correctness_closure_test \
  tests.goal1399_collect_k_bounded_resolution_test
```

## Non-Action

This document does not create `v1.5`, move `v1.0`, or authorize release/tag
action by itself. It records the final checklist for the explicit release/tag
action.
