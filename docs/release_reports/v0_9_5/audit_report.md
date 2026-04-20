# RTDL v0.9.5 Audit Report

Date: 2026-04-19

Status: release audit accepted by Codex, Claude, and Gemini Flash.

## Audit Scope

This audit checks the `v0.9.5` release for:

- correctness of the new any-hit predicate;
- correctness of visibility-row helpers;
- correctness of `reduce_rows`;
- backend-support honesty;
- public documentation consistency;
- release-flow integrity after Goals644-645 expanded and packaged the release
  scope.

## Test Audit

Recorded test evidence:

- local full suite: `1211 tests`, `179 skips`, `OK`
- Linux focused backend suite: `23 tests`, `2 skips`, `OK`
- Goal644 focused public-doc/helper suite: `10 tests`, `OK`
- Goal645 focused public release-doc/package suite: `14 tests`, `OK`
- public command truth audit: `valid: true`, `248` commands
- tutorial/example harness: `65 passed`, `0 failed`, `26 skipped`
- `git diff --check`: clean

## Documentation Audit

Public docs for the released tag state:

- current `v0.9.5` surface includes any-hit, visibility rows, and emitted-row
  reductions;
- OptiX, Embree, and HIPRT are native early-exit any-hit paths;
- Vulkan and Apple RT are compatibility any-hit paths at the tag boundary;
- `reduce_rows` is a Python helper, not native backend acceleration;
- `v0.9.4` Apple DB/graph hardware boundaries still apply.

Post-release current `main` adds native Vulkan any-hit and Apple RT
native/native-assisted any-hit after backend library rebuilds. That newer
current-main evidence is recorded in Goals650-653 and is not a retroactive
claim about the released `v0.9.5` tag.

## Known Non-Claims

This audit rejects these claims:

- Vulkan or Apple RT have native early-exit any-hit in `v0.9.5`.
- `reduce_rows` is a native RT backend operation.
- HIPRT is AMD-GPU validated.
- HIPRT has a CPU fallback.
- Apple DB or graph workloads use Apple ray-tracing hardware.
- v0.9.5 proves broad backend speedup.

## Review Consensus

- Codex: ACCEPT.
- Claude: ACCEPT.
- Gemini Flash: ACCEPT.

Review files:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal641_644_claude_final_release_gate_review_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal641_644_gemini_flash_final_release_gate_review_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal645_claude_review_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal645_gemini_flash_review_2026-04-19.md`

## Audit Verdict

No release-blocking code, test, documentation, or flow issue is known for the
`v0.9.5` release.
