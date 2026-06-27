# RTDL v0.9.5 Tag Record

Date: 2026-04-19

Status: released as `v0.9.5`.

## Tag Boundary

Tag `v0.9.5` represents:

- bounded `ray_triangle_any_hit` row semantics;
- native early-exit any-hit for OptiX, Embree, and HIPRT;
- compatibility any-hit dispatch for Vulkan and Apple RT;
- bounded `visibility_rows` helpers;
- Python standard-library `reduce_rows`;
- no native-backend overclaim for `reduce_rows`;
- no native early-exit claim for Vulkan or Apple RT.

Post-release current `main` later adds native Vulkan any-hit and Apple RT
native/native-assisted any-hit after backend library rebuilds. Those later
changes are recorded in Goals650-653 and are not part of the released tag
boundary described here.

## Required Before Tagging

Before creating the tag, all requirements were satisfied:

- local full test discovery passed: `1211 tests`, `179 skips`, `OK`
- Linux focused backend validation must pass: done, `23 tests`, `2 skips`, `OK`
- public docs and examples must pass smoke/command audits: done
- final release gate must be reviewed by external AIs: done by Claude and
  Gemini Flash
- worktree reviewed and committed
- user explicitly authorized release

## Tag Commands

Release commands:

```bash
git tag -a v0.9.5 -m "Release RTDL v0.9.5"
git push origin main
git push origin v0.9.5
```
