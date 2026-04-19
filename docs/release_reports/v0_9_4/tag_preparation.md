# RTDL v0.9.4 Tag Preparation

Date: 2026-04-19

Status: release gates passed; pending explicit release authorization.

## Proposed Tag Boundary

Tag `v0.9.4` should represent:

- Apple full-surface `run_apple_rt` dispatch for all 18 current predicates
- Apple MPS RT coverage for supported geometry and nearest-neighbor slices
- Apple Metal compute/native-assisted coverage for bounded DB and graph slices
- prepared Apple closest-hit reuse and masked traversal improvements from the
  internal evidence lines
- clear support-matrix disclosure of CPU exact refinement, aggregation,
  uniqueness, and ordering where used
- HIPRT and Apple native backend source reorganization into backend directories
- no broad Apple speedup or mature-backend claim

## Required Before Tagging

Before creating the tag:

- local full test discovery must pass: done in
  `/Users/rl2025/rtdl_python_only/docs/reports/goal625_v0_9_4_local_full_unittest_goal_pattern_2026-04-19.txt`
- Apple focused backend suite must pass on macOS: covered by the local full
  release-gate suite and prior Goal 624 evidence
- HIPRT focused backend suite must pass on Linux after rebuilding from the
  current tree: done in
  `/Users/rl2025/rtdl_python_only/docs/reports/goal625_v0_9_4_linux_backend_gate_2026-04-19.txt`
- public docs and examples must pass smoke/link/command audits: done in Goal
  625 and Goal 515 evidence
- final release gate report must be reviewed by at least one external AI: done
  by Claude and Gemini Flash in Goal 625
- worktree must be clean: pending final commit
- user must explicitly authorize release/tag creation

## Tag Command

Do not run this until the user explicitly authorizes the release tag:

```bash
git tag -a v0.9.4 -m "Release RTDL v0.9.4"
git push origin main
git push origin v0.9.4
```
