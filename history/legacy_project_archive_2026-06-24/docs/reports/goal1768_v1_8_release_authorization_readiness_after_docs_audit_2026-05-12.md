# Goal1768 v1.8 Release Authorization Readiness After Docs And Audit

Date: 2026-05-12

## Verdict

`v1_8_release_authorization_packet_ready_pending_user_go`

The three additional release requirements are satisfied for the v1.8
source-tree Python+RTDL release candidate:

1. Public docs are updated across the front page, tutorial, examples, and docs.
2. Post-v1.5 release-used evidence follows the project review/consensus rules;
   unresolved historical goals are quarantined from release use.
3. The GitHub learner path has been double-checked so a new reader can learn
   the Python+RTDL design without reading historical goal reports first.

This report does not authorize a tag, version bump, push, package upload, or
release. It says the release authorization packet is ready for the user's
explicit go/no-go decision.

## Requirement 1: Public Docs Updated

Status: `pass`

Evidence:

- `README.md`
- `docs/README.md`
- `docs/quick_tutorial.md`
- `examples/README.md`
- `docs/app_example_quickstart.md`
- `docs/public_documentation_map.md`
- `docs/current_architecture.md`
- `docs/capability_boundaries.md`
- `docs/current_main_support_matrix.md`
- `docs/performance_model.md`
- `docs/rtdl/ir_and_lowering.md`
- `docs/reports/goal1763_v1_8_public_docs_and_learner_path_readiness_2026-05-12.md`

The docs now repeat the learner design rule:

```text
Python writes the application.
RTDL expresses the RT-shaped kernel.
Native backends execute generic engine contracts.
```

## Requirement 2: Post-v1.5 Rule Audit

Status: `pass-with-quarantine`

Evidence:

- `docs/reports/goal1764_post_v1_5_release_rule_audit_2026-05-12.md`

The audit accepts the broad post-v1.5 Gemini audit counts as real:

- 80 passing
- 98 missing or invalid
- 351 ambiguous

The release-safe rule is that v1.8 may use only the consensus-clean release
evidence chain. Missing, invalid, or ambiguous historical goals are quarantined from release claims, release gates, architecture changes, performance wording, and roadmap changes unless separately remediated with distinct-AI review.

## Requirement 3: GitHub Learner Double Check

Status: `pass`

Evidence:

- `docs/reports/goal1765_github_learner_readiness_double_check_2026-05-12.md`
- `tests/goal1765_github_learner_readiness_double_check_test.py`

The learner path runs portable source-tree commands and keeps history/evidence
pages outside the beginner path.

## External Review

Claude:

- `docs/reviews/goal1766_claude_review_goal1763_1765_release_docs_audit_2026-05-12.md`
- Verdict: `accept`

Gemini:

- `docs/reviews/goal1767_gemini_review_goal1763_1765_release_docs_audit_2026-05-12.md`
- Verdict: `accept-with-boundary`

Both reviews agree that the docs/audit/learner package is ready to be included
in the final v1.8 release authorization packet, with explicit user release
authorization still required.

## Validation

Focused docs/audit/learner gate:

```text
Ran 39 tests in 17.370s
OK
```

Broader v1.8 release gate including the new docs/audit/learner tests:

```text
Ran 155 tests in 6.658s
OK
```

## Still Blocked Until User Authorization

- `VERSION` bump
- tag
- push
- package upload
- public release
- package-install claim
- public speedup wording
- Python+partner+RTDL claim
- PyTorch/CuPy integration claim
- true zero-copy claim

## Pod Requirement

No pod is needed for this docs/audit/learner phase. Pod or hardware work is
only needed if the release decision asks for new NVIDIA/OptiX runtime evidence,
new same-contract timing evidence, or environment-diversity validation.

## Protected Files

Do not stage:

- `docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz`
- `id_ed25519_rtdl_codex`
- `rtdl_v0_4.tar.gz`
- `scratch/`
