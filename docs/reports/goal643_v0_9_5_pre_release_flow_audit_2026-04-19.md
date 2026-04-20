# Goal 643: v0.9.5 Pre-Release Flow Audit

Date: 2026-04-19

## Scope

Release-flow audit for the v0.9.5 bounded any-hit / visibility-row /
emitted-row reduction line after Goals 632-644.

This audit checks whether the version has:

- a coherent goal ladder;
- implementation, test, doc, and review evidence;
- public honesty boundaries for backend support;
- no known code/test/doc blocker before a release-candidate decision.

## Goal Chain

Relevant goal evidence:

- Goal631: v0.9.5 any-hit / visibility goal ladder.
- Goal632: `rt.ray_triangle_any_hit(exact=False)` language predicate,
  lowering metadata, CPU reference, and examples.
- Goal633: `rt.visibility_rows_cpu(...)` and backend-capable
  `rt.visibility_rows(...)`.
- Goal635: earlier pre-release test/doc/audit snapshot before native backend
  expansion.
- Goal636: backend compatibility dispatch and the user doubt log documenting
  the distinction between hit-count projection and native early-exit.
- Goal637: OptiX native any-hit using `optixTerminateRay()`.
- Goal638: Embree native any-hit using `rtcOccluded1`.
- Goal639: HIPRT native any-hit using a HIPRT traversal-loop `break`.
- Goal640: backend support-boundary audit for CPU, Embree, OptiX, Vulkan,
  HIPRT, and Apple RT.
- Goal641: pre-release test report.
- Goal642: pre-release documentation refresh.
- Goal643: this flow audit.
- Goal644: `rt.reduce_rows(...)` Python standard-library helper for
  deterministic reductions over emitted rows.
- Goal645: public release package, front-page/tutorial/example doc refresh,
  and release-package regression checks for v0.9.5.

## Consensus / Review State

Completed external-style reviews:

- Goal632/633: Claude + Gemini accepted.
- Goal635: Claude + Gemini accepted.
- Goal636: external review accepted.
- Goal637: Claude + Gemini accepted.
- Goal638: Claude + Gemini accepted.
- Goal639: Claude + Gemini accepted.
- Goal640: Claude accepted.
- Goal644: Codex + Claude accepted; Gemini Flash was attempted but unavailable
  due tool quota exhaustion.

Pending after this file:

- Refreshed combined external-style review for Goals 641-644 test/doc/flow
  closure after adding `reduce_rows`.

## Code / Test State

Mechanical check:

```text
git diff --check
```

Result:

```text
no whitespace errors
```

Full local test:

```text
Ran 1211 tests in 111.506s
OK (skipped=179)
```

Linux focused backend test:

```text
Ran 23 tests in 3.648s
OK (skipped=2)
```

Linux validated backends:

```text
embree OK (4, 3, 0)
optix OK (9, 0, 0)
vulkan OK (0, 1, 0)
hiprt OK {'version': (2, 2, 15109972), 'api_version': 2002,
          'device_type': 1, 'device_name': 'NVIDIA GeForce GTX 1070'}
```

Local validated macOS backends:

```text
embree OK (4, 4, 0)
apple_rt OK Apple M4
```

## Documentation State

Public docs now consistently state:

- current release-prepared public version is `v0.9.5`;
- `ray_triangle_any_hit` emits `{ray_id, any_hit}`;
- `visibility_rows_cpu` emits `{observer_id, target_id, visible}`;
- `visibility_rows(..., backend=...)` can dispatch through real backends;
- `reduce_rows` emits deterministic grouped summary rows after row emission;
- OptiX, Embree, and HIPRT are native any-hit paths;
- Vulkan and Apple RT are compatibility paths for any-hit;
- compatibility is real backend execution, not native early-exit performance.
- `reduce_rows` is a Python standard-library helper, not native backend
  acceleration.

Corrected stale doc:

- `/Users/rl2025/rtdl_python_only/docs/tutorials/feature_quickstart_cookbook.md`

## Honesty Boundaries

No release-flow overclaim detected:

- No claim that v0.9.5 is tagged/pushed by Codex; tag action remains
  user-controlled in the package.
- No claim that Vulkan or Apple RT have native early-exit any-hit.
- No claim that HIPRT has AMD GPU validation.
- No claim that HIPRT whole-call timing is faster after Goal639.
- No claim that `reduce_rows` is a native RT backend reduction.
- No claim that RTDL is a renderer or full DBMS.

## Dirty Worktree Note

The working tree is intentionally dirty because this is active development
before release packaging. The changed-file set includes v0.9.5 source, tests,
docs, examples, handoff files, and reports. This is not itself a blocker, but
release packaging should happen from a reviewed commit after this audit and the
combined external review are complete.

## Current Blockers

No code/test/doc/flow blocker is known at this point.

Remaining required action before release-candidate packaging:

- create the final release-candidate/hold or release package according to the
  user's decision.

## Codex Verdict

ACCEPT.

The v0.9.5 flow is coherent and release-candidate-ready. The combined external
review of the pre-Goal644 test/doc/flow evidence is recorded below and is now
superseded by the Goal644 refresh.

## External Review

Combined Goals 641-643 review:

- File: `/Users/rl2025/rtdl_python_only/docs/reports/goal641_643_external_review_2026-04-19.md`
- Verdict: ACCEPT.
- Original flow finding: the goal ladder is coherent, upstream reviews are accepted,
  `git diff --check` is clean, and no overclaim was found.

Updated Codex verdict after external review: ACCEPT for release-candidate
packaging at the user's discretion.

Post-Goal644 update:

- Goal644 adds the generic `rt.reduce_rows(...)` helper requested after the
  Goals 533/534/536 design discussion.
- The local full suite was rerun after Goal644 and passed with 1207 tests and
  179 skips.
- The local full suite was rerun after Goal645 and passed with 1211 tests and
  179 skips.
- Public docs now describe the new helper and preserve the non-native-backend
  reduction boundary.
- A refreshed external review should now cover Goals 641-644 together before
  final packaging.

## Refreshed Final Release-Gate Review

After the Goal644 update, Codex requested a combined external review of Goals
641-644:

- request file: `/Users/rl2025/rtdl_python_only/docs/handoff/GOAL641_644_V0_9_5_FINAL_RELEASE_GATE_REVIEW_REQUEST_2026-04-19.md`
- Claude review: `/Users/rl2025/rtdl_python_only/docs/reports/goal641_644_claude_final_release_gate_review_2026-04-19.md`
- Gemini Flash review: `/Users/rl2025/rtdl_python_only/docs/reports/goal641_644_gemini_flash_final_release_gate_review_2026-04-19.md`

Results:

- Claude verdict: ACCEPT.
- Gemini Flash verdict: ACCEPT.

Final consensus:

- Codex: ACCEPT.
- Claude: ACCEPT.
- Gemini Flash: ACCEPT.

Final release-gate status after Goal644: ACCEPT for release-candidate packaging
at the user's discretion.

## Goal645 Public Release Package / Docs Update

After packaging, Codex updated the public front page, docs index, feature
guide, architecture page, capability boundaries, tutorials index,
release-facing examples, backend maturity page, and examples index to present
the same v0.9.5 surface:

- `ray_triangle_any_hit`;
- `visibility_rows`;
- `reduce_rows`;
- native early-exit only for OptiX, Embree, and HIPRT;
- compatibility any-hit for Vulkan and Apple RT;
- no native backend reduction claim for `reduce_rows`.

New validation:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal511_feature_guide_v08_refresh_test tests.goal532_v0_8_release_authorization_test tests.goal645_v0_9_5_release_package_test tests.goal513_public_example_smoke_test tests.goal515_public_command_truth_audit_test -v

Ran 14 tests in 2.679s
OK
```

Public command truth audit:

```text
valid: true
command_count: 248
public_doc_count: 14
```

Tutorial/example harness:

```text
65 passed, 0 failed, 26 skipped, 91 total
```

Whitespace audit:

```text
git diff --check
no output
```
