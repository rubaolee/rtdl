# RTDL v1.5 Tag Preparation

Status: completed. The `v1.5` annotated tag has been published after explicit
release/tag authorization.

The previous public release remains `v1.0`; it was not moved or retagged.

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
- The native engine is not yet app-agnostic internally; this tag package must
  not be described as a zero-app-knowledge engine release.
- Goal1411 boundary/backend 3-AI consensus is present and accepted.
- Goal1413 app-independent engine roadmap is present and linked from the v1.5
  release package.
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

Latest recorded verification:
`docs/reports/goal1412_v1_5_final_pre_tag_verification_2026-05-06.md`

## Tag Result

The tag action was performed after explicit user approval. This document does
not authorize moving `v1.5`, moving `v1.0`, or broadening the public claims
listed above.
