# RTDL v0.9.8 Tag Preparation

Status: released as `v0.9.8`.

Date: 2026-05-01

## Release Boundary

Tag `v0.9.8` represents the bounded RTX app evidence and public-claim cleanup
release:

- reviewed public RTX wording matrix at `11` rows;
- one newly reviewed public row:
  `road_hazard_screening / prepared_native_compact_summary_40k`;
- continued public speedup blocks for `database_analytics` and
  `polygon_set_jaccard`;
- local full-discovery and release-surface documentation evidence through
  Goals1214-1215;
- release-candidate and authorization-gate evidence through Goals1216-1218.

## Requirements Already Satisfied

- Goal1214 full local discovery: `2366` tests OK.
- Goal1215 release-surface docs: `64` tests OK.
- Goal1216 release-candidate audit: accepted by Codex and Gemini.
- Goal1217 version-marker baseline repair: accepted by Codex and Gemini.
- Goal1218 release-authorization gate: accepted by Codex and Gemini.
- Goal1219 release package review: accepted by Codex and Gemini.
- Goal1220 final authorization: accepted by Codex and Gemini.
- `VERSION` bumped to `v0.9.8`.
- No immediate pod is required before package/authorization paperwork.

## Release Authorization

- final authorization is recorded in Goal1220;
- release action is authorized by Goal1220 two-AI consensus;
- release docs are committed before the tag;
- tag is created only after the release commit;
- `main` and tag push are authorized by the release instruction.

## Tag Commands

```bash
git tag -a v0.9.8 -m "Release RTDL v0.9.8"
git push origin main
git push origin v0.9.8
```

## Boundary

This file records the authorized v0.9.8 tag boundary and commands.
