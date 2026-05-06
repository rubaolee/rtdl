# Goal 1397 - 3-AI Consensus For v1.5 Standalone And Partner Roadmap

Date: 2026-05-06

## Status

3-AI consensus accepts the roadmap change proposed in:

- `docs/reports/goal1397_v1_5_standalone_language_and_partner_roadmap_proposal_2026-05-06.md`

The accepted change is:

- v1.5 becomes the standalone RTDL language/runtime completion milestone for
  Embree+OptiX, not merely a primitive-packet release.
- v1.6-v2.0 becomes the staged partner-mechanism track.
- The current primitive-only readiness evidence remains useful prerequisite
  evidence, but it is no longer sufficient to tag or release v1.5 under the new
  scope.

## Review Inputs

Codex position:

- Acceptable if the release gate is updated immediately.
- Main risk is scope expansion; v1.5 must not be tagged until collection,
  app migration, benchmark, and support-maturity gates are complete.

Claude review:

- File: `docs/reports/goal1397_claude_v1_5_partner_roadmap_review_2026-05-06.md`
- Verdict: `ACCEPTABLE`
- Required fixes: none.
- Noted that v2.0 external communication should be updated before v2.0 partner
  work begins if prior external messaging used the old meaning.

Gemini review:

- File: `docs/reports/goal1397_gemini_v1_5_partner_roadmap_review_2026-05-06.md`
- Verdict: `ACCEPTABLE`
- Required fixes: none.

## Accepted Project Boundary

v1.5 completion now requires:

- stable or explicitly excluded bounded collection semantics;
- app endpoint migration/classification against generic standalone RTDL
  primitives and wrappers;
- same-contract per-app Embree/OptiX correctness and benchmark evidence;
- support/maturity matrix backed by tests;
- no public speedup wording unless separately evidence-backed and reviewed;
- no package-install claim unless packaging metadata is added;
- no Vulkan/HIPRT/Apple RT implementation push before v2.1.

v1.6-v2.0 now targets partner mechanisms:

- v1.6: partner API design;
- v1.7: first partner prototype;
- v1.8: partner conformance suite;
- v1.9: partner ecosystem hardening;
- v2.0: public partner-ready RTDL.

## Immediate Consequence

Do not tag `v1.5` from current `main` solely on the primitive readiness packet.
In short: do not tag `v1.5` until the standalone-language gates pass.
The earlier Goal1395 release-readiness decision is superseded only in release
scope: it remains valid as primitive readiness evidence, but not as final v1.5
release authorization under the new standalone-language definition.
