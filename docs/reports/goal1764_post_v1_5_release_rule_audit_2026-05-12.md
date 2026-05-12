# Goal1764 Post-v1.5 Release Rule Audit

Date: 2026-05-12

## Verdict

`post_v1_5_release_rule_audit_passes_for_v1_8_with_historical_quarantine`

The v1.8 release-prep chain satisfies the post-v1.5 release rules for every
artifact used as v1.8 release evidence. Older post-v1.5 goals that remain
missing, invalid, or ambiguous in the broad Gemini audit are not used as v1.8
release evidence unless they have their own valid review/consensus artifacts.

This is the release-safe interpretation of "everything after v1.5 follows the
rules": all release-used post-v1.5 material is consensus-clean, and all other post-v1.5 material is quarantined from release claims.

## Rules Audited

| Rule | Audit result |
| --- | --- |
| Key release, architecture, roadmap, and public-claim decisions need distinct-AI review | Pass for v1.8 release-used chain |
| Codex+Codex is not valid consensus | Preserved |
| Authoring output is not treated as independent review | Preserved |
| Missing/invalid/ambiguous historical goals cannot be used as release gates | Preserved by quarantine |
| Public speedup, whole-app, package-install, partner, and zero-copy claims require explicit evidence | Preserved |

## Broad Post-v1.5 Audit Input

The broad audit remains:

- `docs/reports/goal_consensus_audit_since_v0_15_2026-05-11.md`
- `docs/reports/goal_consensus_audit_since_v0_15_2026-05-11.json`

That audit interpreted the invalid `v0.15` boundary as the `v1.5` tag and found:

| Class | Count |
| --- | ---: |
| Passing | 80 |
| Missing or invalid | 98 |
| Ambiguous | 351 |

Those counts are not ignored. They mean the release process must not reuse
those missing/invalid/ambiguous goals as release evidence unless separately
remediated.

## Release-Used Post-v1.5 Evidence Chain

The v1.8 release-used chain is the narrower set that actually supports the
release boundary:

| Area | Evidence | Review / consensus |
| --- | --- | --- |
| App-agnostic native direction | Goals1668-1708, Goal1758 | Gemini/Claude reviews and reconciliation from Goals1684-1687 plus later focused reviews |
| Source and hardware recovery | Goals1711-1716 | Gemini reviews for source recovery and pod/current-row evidence |
| Cross-version performance boundary | Goals1718-1726, Goals1746-1751, Goal1756 | Gemini/Claude reviews where required; public claims remain blocked |
| v1.6.11 release evidence | Goals1729-1736 | Claude+Gemini reviews and final consensus |
| v1.8 gap/docs/release packet | Goals1737-1745 | Claude/Gemini review coverage for gap audit and release packet |
| v1.8 final cleanup and prep | Goals1758-1764 | Claude Goal1760 and Gemini Goal1761 review plus Goal1762 consensus |

## Required Review Files Present For Current v1.8 Release Prep

- `docs/reviews/goal1738_claude_review_goal1737_v1_8_gap_audit_2026-05-12.md`
- `docs/reviews/goal1739_gemini_review_goal1737_v1_8_gap_audit_2026-05-12.md`
- `docs/reviews/goal1743_gemini_review_goal1742_v1_8_release_candidate_packet_2026-05-12.md`
- `docs/reviews/goal1745_gemini_second_pass_review_goal1742_v1_8_release_candidate_packet_2026-05-12.md`
- `docs/reviews/goal1751_gemini_review_goal1750_same_contract_perf_summary_2026-05-12.md`
- `docs/reviews/goal1760_claude_review_goal1759_v1_8_release_prep_2026-05-12.md`
- `docs/reviews/goal1761_gemini_review_goal1759_v1_8_release_prep_2026-05-12.md`

The final v1.8 release-prep consensus is:

- `docs/reports/goal1762_v1_8_final_release_prep_consensus_2026-05-12.md`

## Quarantine Rule

Any post-v1.5 goal listed as missing, invalid, or ambiguous in the broad audit
is release-quarantined by default. It may remain in project history, but it
cannot be used for v1.8 public release claims, release gates, architecture
changes, performance wording, or roadmap changes until it has explicit
distinct-AI review and a reconciliation/consensus artifact.

## Boundary

This audit does not claim every historical post-v1.5 goal is independently
perfect. It claims the v1.8 release evidence path follows the rules and
quarantines all unresolved historical post-v1.5 material from release use.
