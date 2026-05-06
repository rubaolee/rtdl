# Three-AI Consensus: v1.0 to v1.5 Full Cross-Platform Audit

Date: 2026-05-06

## Scope

This consensus covers the audit report:

`docs/reports/v1_0_to_v1_5_full_cross_platform_audit_2026-05-06.md`

and the current local diff containing:

- the audit report;
- the local Embree LSI boundary-intersection fix in
  `src/native/embree/rtdl_embree_api.cpp`;
- Claude and Gemini review artifacts.

## Review Inputs

- Codex audit:
  `docs/reports/v1_0_to_v1_5_full_cross_platform_audit_2026-05-06.md`
- Claude initial review:
  `docs/reports/claude_v1_0_to_v1_5_full_cross_platform_audit_review_2026-05-06.md`
- Claude corrected re-review:
  `docs/reports/claude_v1_0_to_v1_5_full_cross_platform_audit_rereview_2026-05-06.md`
- Gemini review:
  `docs/reports/gemini_v1_0_to_v1_5_full_cross_platform_audit_review_2026-05-06.md`

## Consensus Result

Status: `accepted-with-forward-blocker`.

Codex, Claude, and Gemini agree that the corrected audit accurately describes
the v1.0-to-v1.5 release movement and preserves the required v1.5 boundaries:

- v1.5 is valid only for the documented supported Embree+OptiX surface;
- v1.5 does not authorize package-install claims;
- v1.5 does not authorize whole-app or broad GPU/RTX speedup claims;
- v1.5 does not stabilize `COLLECT_K_BOUNDED`;
- v1.5 does not claim app-free native-engine internals;
- `v1.0` and `v1.5` tags must not be moved or retagged.

The audit is also accepted as correctly distinguishing:

- the released `v1.5` tag;
- current `main`;
- the local dirty working-tree state containing the post-tag Embree LSI fix.

## Forward Blocker

The local Embree LSI boundary-intersection fix is required before any public
cross-platform readiness claim that depends on Linux Embree baseline/evaluation
passing.

Current state:

- The fix is present only in the local Windows and Linux dirty working trees.
- The fix is not in the released `v1.5` tag.
- The fix is not in GitHub `origin/main`.

Required next action before broader Windows/Linux readiness wording:

1. Commit and push the Embree LSI fix plus audit artifacts.
2. Reset to clean `origin/main` on Windows and Linux.
3. Rerun the Windows and Linux v1.5/public slices.
4. Rerun the Windows and Linux Embree baseline/evaluation slices.
5. Record the clean-tree results before making any public cross-platform
   confidence claim.

## Nonblocking Follow-Ups

Full discovery is still not green on Windows or Linux. The remaining blockers
are historical/pod/platform-sensitive and do not invalidate the documented
v1.5 supported-surface claim, but they should be tracked if the project wants
one-command full-suite green across common OSes:

- hardcoded maintainer absolute paths;
- historical pod artifact and log expectations;
- macOS-only Apple RT tests running on non-macOS;
- direct `.sh` execution on Windows;
- Unix executable-bit assertions on Windows;
- older subprocess/path assumptions.

The v1.5 release statement also contains non-portable absolute macOS evidence
pointers. Repo-relative equivalents exist under `docs/reports/`, but a future
docs traceability pass should clean those pointers.

## Consensus Sentence

RTDL v1.5 is accepted as valid within its documented supported Embree+OptiX
language/runtime boundary, while the newly found Linux Embree LSI
boundary-intersection fix must be committed, pushed, and clean-tree validated
before any stronger Windows/Linux readiness claim is made.
