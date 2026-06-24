# RTDL v0.9.2 Audit Report

Date: 2026-04-19

Status: release candidate audit accepted locally and by external AI review

## Audit Scope

This audit covers the v0.9.2 Apple RT candidate release package:

- Apple RT native-slice correctness
- Apple RT performance evidence
- public documentation honesty
- stale test cleanup
- pre-release test/doc/flow gate
- external AI review consensus

## Findings

### Implementation Scope

The v0.9.2 candidate is a backend/runtime improvement release, not a new
language redesign.

The accepted Apple RT native slices are:

- 3D `ray_triangle_closest_hit`
- 3D `ray_triangle_hit_count`
- 2D `segment_intersection`

All other current `run_apple_rt` predicates are compatibility-dispatched through
the CPU reference. The `native_only=True` option is the guard against mistaking
compatibility dispatch for Apple hardware-backed execution.

### Performance Scope

Goal600 gives the current canonical local Apple M4 performance evidence.

The audit finds the performance wording honest:

- closest-hit may be described as faster than Embree on the current fixture
- hit-count is correct but unstable and much slower than Embree
- segment-intersection is correct and stable but slower than Embree
- v0.9.2 may claim Apple RT overhead reduction and improved ergonomics
- v0.9.2 may not claim broad Apple speedup

### Documentation Scope

Goal599 refreshed the front page, docs index, backend maturity guide,
capability boundaries, architecture guide, tutorials, release-facing examples,
feature guide, and examples index.

Goal600 then audited stale public-doc phrases and found no obsolete v0.8-current
or old Apple RT wording in the front-door docs.

The audit finds the documentation coherent:

- current released version remains `v0.9.1` until explicit tag/release action
- v0.9.2 is identified as a candidate line
- Apple RT native and compatibility modes are separated
- Embree remains the mature performance baseline

### Test Scope

Goal600 test evidence:

- full public-pattern suite: `1118` tests, `OK`, `171` skipped
- targeted stale-test cleanup suite: `20` tests, `OK`, `2` skipped
- Apple RT focused suite: `19` tests, `OK`
- public command truth audit: `244` commands, valid
- public example smoke: pass
- `py_compile`: pass
- `git diff --check`: pass

### Flow Scope

The audit finds the flow coherent:

- Goal594 planned the work with consensus.
- Goals595-598 implemented and measured the Apple RT improvements.
- Goal599 refreshed public docs.
- Goal600 performed full local pre-release validation.
- Goal600 external reviews by Gemini-style reviewer and Claude both ACCEPT.

## Remaining Honest Boundary

The release candidate remains bounded:

- no broad Apple RT speedup claim
- no Apple RT maturity claim over Embree
- no native Apple hardware-backed claim for compatibility predicates
- no non-macOS or Intel Mac support claim
- no change to HIPRT/OptiX/Vulkan/Embree release contracts

## Audit Verdict

The v0.9.2 Apple RT candidate package is coherent, bounded, tested, and
externally reviewed.

Status: **ACCEPT** as release-ready after explicit user release authorization.
