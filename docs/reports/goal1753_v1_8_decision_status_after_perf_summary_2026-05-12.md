# Goal1753 v1.8 Decision Status After Performance Summary

## Verdict

`v1_8_decision_status_ready_pending_user_release_authorization`

The v1.8 Python+RTDL evidence chain is materially stronger after Goal1746-Goal1768, but this note does not authorize release, tagging, version bumping, package publication, or public speedup wording.

## What Changed Since Goal1742

- Goal1746 recovered all 14 v1.0 Embree app-level baseline artifacts.
- Goal1747 removed the `ann_candidate_search` skip by using the correct v1.0 Embree `rerank_summary` surface and documented the rejected `quality_summary` path as roughly 7.2 billion Python exact-distance checks.
- Goal1748 classified recovered Embree timing comparability as 4 diagnostic phase mappings, 7 timing-schema mismatches, and 3 missing same-name current artifacts.
- Goal1750 produced the strict same-contract performance summary:
  - OptiX: 15 artifact-pair rows, 12 same-contract primary ratios, 3 evidence-only rows.
  - Embree: 1 strict same-contract database row plus the bounded 14 recovered app-level rows.
- Goal1751 Gemini independently reviewed Goal1750 as `accept-with-boundary`.
- Goal1758 migrated the remaining older Apple RT / HIPRT / Oracle / Vulkan `lsi`, `overlay`, and `triangle_probe` native support symbols to generic native terminology and removed the final known multi-backend source/ABI app-shaped blocker.
- Goals1760 and 1761 supplied fresh independent Claude and Gemini review of the updated Goal1742/Goal1750/Goal1758/Goal1759 chain.
- Goal1762 recorded final v1.8 release-prep consensus, pending explicit user release authorization.
- Goals1763-1768 added the final public-doc, post-v1.5 rule-audit, and GitHub learner-readiness checks requested before release authorization.
- Goal1729 and Goal1742 were updated to include the new performance evidence while preserving conservative release/public-claim boundaries.

## Current v1.8 Release Interpretation

The current evidence supports this internal engineering statement:

```text
The tracked v1.8 source-tree Python+RTDL release surface is app-agnostic at the native engine source/ABI boundary, has current pod validation evidence for the bounded release surface, and has conservative cross-version performance evidence showing no broad same-contract regression in the comparable OptiX rows. Embree has one strict same-contract database comparison plus recovered v1.0 app-level evidence that remains diagnostic/schema-bounded.
```

Allowed public-facing release wording remains the narrower Goal1742 wording:

```text
RTDL v1.8 completes the source-tree Python+RTDL productization boundary for the tracked release surface. Python remains the application/control layer, and RTDL owns the app-agnostic RT-shaped kernel/runtime bridge for supported primitive paths.
```

## Still Blocked

The following remain blocked:

- Public speedup wording.
- Broad RTX/GPU acceleration wording.
- Whole-application performance claims.
- Claiming recovered v1.0 Embree app-level rows as public same-contract speedup evidence.
- Claiming package-install support.
- Claiming Python+partner+RTDL v2.0 completion.
- Release/tag/version-bump action without explicit user authorization.

## Claude Review Attempt

Codex attempted to launch Claude for:

```text
docs/reviews/goal1752_claude_review_updated_goal1742_1750_v1_8_packet_2026-05-12.md
```

The attempt did not produce the review file. Captured stdout reported:

```text
You're out of extra usage - resets 4:40am (America/New_York)
```

Therefore this note does not count Claude as having reviewed the updated Goal1742/Goal1750 packet.

## Next Required Actions

Before release action:

1. Re-run the focused v1.8 gate immediately before any authorized release operation.
2. Inspect `git status --short` and stage only intended files.
3. Ask the user for explicit release/tag/version-bump authorization.

## Boundary

This is a status note, not a release decision. It preserves the current evidence and names the remaining procedural/external-review blockers.
