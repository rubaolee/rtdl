# Goal1762 v1.8 Final Release-Prep Consensus

Date: 2026-05-12

## Verdict

`v1_8_release_prep_consensus_ready_pending_user_release_authorization`

Codex, Claude, and Gemini agree that the v1.8 source-tree Python+RTDL release
candidate is ready for release authorization review after Goal1758 and
Goal1759. Goals1763-1768 extend this consensus with final public
documentation, post-v1.5 rule-audit, and GitHub learner-readiness checks.

This note does not authorize a tag, version bump, package upload, push, or
public release. Those actions still require explicit user authorization.

## Consensus Inputs

- Codex implementation/review:
  - Goal1758 migrated the remaining older Apple RT / HIPRT / Oracle / Vulkan
    `lsi`, `overlay`, and `triangle_probe` native source/ABI support to generic
    engine terminology.
  - Goal1759 prepared the v1.8 release chain for fresh external review after
    that cleanup.
  - The post-review focused v1.8 gate passed:
    `Ran 129 tests in 4.857s; OK`.
- Claude review:
  - `docs/reviews/goal1760_claude_review_goal1759_v1_8_release_prep_2026-05-12.md`
  - Verdict: `accept-with-boundary`.
- Gemini review:
  - `docs/reviews/goal1761_gemini_review_goal1759_v1_8_release_prep_2026-05-12.md`
  - Verdict: `accept`.
- Docs/audit/learner follow-up reviews:
  - `docs/reviews/goal1766_claude_review_goal1763_1765_release_docs_audit_2026-05-12.md`
  - Verdict: `accept`.
  - `docs/reviews/goal1767_gemini_review_goal1763_1765_release_docs_audit_2026-05-12.md`
  - Verdict: `accept-with-boundary`.
  - `docs/reports/goal1768_v1_8_release_authorization_readiness_after_docs_audit_2026-05-12.md`
  - Verdict: `v1_8_release_authorization_packet_ready_pending_user_go`.

## Agreed Release Boundary

The agreed v1.8 claim is:

```text
RTDL v1.8 completes the source-tree Python+RTDL productization boundary for the
tracked release surface. Python remains the application/control layer, and RTDL
owns the app-agnostic RT-shaped kernel/runtime bridge for supported primitive
paths.
```

The source/ABI blocker identified after the performance-table review is resolved
by Goal1758. The native engine boundary for the tracked release surface is
app-agnostic in source and exported ABI terminology.

## Still Blocked

The consensus does not authorize these claims:

- package-install support
- public speedup wording
- broad RTX/GPU acceleration wording
- whole-application acceleration
- universal backend support
- Python+partner+RTDL completion
- PyTorch/CuPy integration
- true zero-copy support
- using recovered v1.0 Embree app-level rows as public same-contract speedup
  evidence

## Release Action Requirements

Before any release action:

1. User must explicitly authorize the release operation.
2. Re-check `git status --short`.
3. Stage only intended source, docs, tests, reports, reviews, and evidence
   artifacts.
4. Do not stage protected local files:
   - `docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz`
   - `id_ed25519_rtdl_codex`
   - `rtdl_v0_4.tar.gz`
   - `scratch/`
5. Bump `VERSION`, tag, push, or publish only if the user's release
   authorization explicitly asks for those actions.

## Boundary

This is the final release-prep consensus note for v1.8. It is not itself a
release command and does not change the current `VERSION` value.
