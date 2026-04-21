# RTDL v0.9.6 Tag Record

Status: released as `v0.9.6`.

Date: 2026-04-21

## Release Boundary

Tag `v0.9.6` represents the prepared/prepacked repeated visibility/count
optimization release:

- Vulkan native early-exit any-hit;
- Apple RT 3D MPS RT any-hit;
- Apple RT 2D MPS-prism native-assisted any-hit;
- Apple RT prepared/prepacked scalar blocked-ray count;
- OptiX prepared/prepacked scalar 2D any-hit count;
- HIPRT prepared 2D any-hit reuse;
- Vulkan prepared 2D any-hit plus packed-ray support;
- public documentation and history catch-up through Goal684.

## Requirements Already Satisfied

- local full test discovery passed after release packaging: `1274` tests OK,
  `187` skips
- public command truth audit passed: valid, `250` commands across `14` docs
- public entry smoke passed
- focused public-doc tests passed: `8` tests OK
- focused history regression passed: `4` tests OK
- `git diff --check` passed
- fresh Linux OptiX/Vulkan/HIPRT backend gate passed
- Codex, Claude, and Gemini Flash accepted Goal681

## Release Authorization

- maintainer explicitly authorized release after public docs and release-level
  flow audit were updated
- release docs are committed before the tag
- tag is created only after that release commit
- `main` and tag push are authorized by the release instruction

## Tag Commands

```bash
git tag -a v0.9.6 -m "Release RTDL v0.9.6"
git push origin main
git push origin v0.9.6
```
