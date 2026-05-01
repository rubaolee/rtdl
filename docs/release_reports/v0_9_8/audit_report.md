# RTDL v0.9.8 Audit Report

Status: released as `v0.9.8`.

Date: 2026-05-01

## Audit Scope

This audit checks whether the post-`v0.9.6` RTX app evidence and public-claim
cleanup work is coherently packaged as the v0.9.8 release.

The release package includes:

- reviewed public RTX wording matrix synchronization to `11` rows;
- newly reviewed road-hazard prepared native compact-summary wording;
- explicit continued blocking of DB and Jaccard public speedup wording;
- stale current-state audit repairs after the road-hazard promotion;
- full local discovery evidence;
- release-surface documentation evidence;
- version-marker baseline repair before any v0.9.8 release action;
- authorization-gate evidence that no new pod is required before package review.

## Test Audit

Recorded release-gate evidence:

- Goal1214 full local discovery: `2366` tests OK, `196` skips, `0` failures,
  `0` errors.
- Goal1215 release-surface documentation audit: `64` tests OK.
- Goal1216 release-candidate audit focused suite: valid.
- Goal1217 version marker sync focused suite: `2` tests OK.
- Goal1218 release-authorization gate focused suite: `4` tests OK.

## Documentation Audit

The release package and current public docs distinguish:

- current released baseline `v0.9.6`;
- prepared v0.9.8 package status;
- reviewed RTX wording row count `11`;
- road-hazard prepared native compact-summary sub-path wording;
- DB/Jaccard public speedup blocks;
- hardware evidence versus release authorization;
- release-action docs versus final tag/publish action.

## Flow Audit

- Goal1216 release-candidate audit was accepted with Codex plus Gemini.
- Goal1217 version-marker repair was accepted with Codex plus Gemini.
- Goal1218 authorization gate was accepted with Codex plus Gemini.
- Goal1219 package review, Goal1220 final authorization, and Goal1221 release
  action review completed the required external-AI release-flow evidence before
  tag, push, or publish.

## Known Non-Claims

This release rejects these claims:

- RTDL is broadly faster for all apps;
- every current app has reviewed public RT-core speedup;
- DB/Jaccard have public speedup wording;
- road-hazard whole-app speedup is authorized;
- a cloud pod must be run before package review;
- `VERSION` has already been bumped to `v0.9.8`;
- release scope exceeds the audited package.

## Audit Verdict

No release blocker is known in code, docs, tests, or flow for the bounded
v0.9.8 release action.
