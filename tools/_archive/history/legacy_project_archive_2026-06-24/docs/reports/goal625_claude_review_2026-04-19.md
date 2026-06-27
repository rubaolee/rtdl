# Goal 625 External AI Review — v0.9.4 Total Test/Doc/Audit Gate

Reviewer: Claude (claude-sonnet-4-6)
Date: 2026-04-19

## Verdict: ACCEPT

## Evidence Verified

### Test Gates

| Gate | Claimed | Transcript |
|------|---------|------------|
| Local macOS full suite (`*_test.py`) | 1178 tests, 171 skips, OK, 110.632s | Confirmed — `Ran 1178 tests in 110.632s` / `OK (skipped=171)` |
| Linux focused backend gate | 131 tests, OK, 64.706s | Confirmed — `Ran 131 tests in 64.706s` / `OK` |
| Public entry smoke | `valid: true`, all commands OK | Confirmed — JSON shows `"valid": true`, all 6 command entries `"ok": true` |
| Public command truth audit | `valid: true`, 244 commands across 14 docs | Confirmed by the referenced JSON report |
| Public doc smoke tests | 10 tests, OK | Stated in gate report; consistent with the referenced test modules |

### Linux Backend Build

All three native backends built from a fresh checkout on `lestat-lx1`:
- `librtdl_hiprt.so` — built successfully (one benign `fread` unused-result warning, not an error)
- `librtdl_optix.so` — built successfully
- `librtdl_vulkan.so` — built successfully

Probe versions confirmed: Embree (4,3,0), OptiX (9,0,0), Vulkan (0,1,0), HIPRT (2,2,15109972) on NVIDIA GeForce GTX 1070.

### Documentation

All six named release docs are present and internally consistent:

- `README.md`, `docs/README.md` — updated for v0.9.4 target
- `docs/release_reports/v0_9_4/README.md` — correct scope, links to support matrix, statement, audit, tag preparation
- `docs/release_reports/v0_9_4/release_statement.md` — clearly bounded; explicit "may claim / must not claim" sections
- `docs/release_reports/v0_9_4/audit_report.md` — lists known non-claims; no inconsistency found
- `docs/release_reports/v0_9_4/tag_preparation.md` — gates enumerated; tag command gated behind explicit user authorization

### Honesty Boundary

The following boundaries are correctly maintained across all reviewed docs:

- Apple DB/graph workloads are Metal compute or Metal-filter-plus-CPU native-assisted — **not** Apple ray-tracing-hardware traversal. Stated consistently.
- HIPRT is validated on the Linux NVIDIA CUDA path only. No AMD GPU or CPU fallback claim present.
- `v0.9.2` and `v0.9.3` are correctly described as internal/untagged evidence lines.
- Embree is the only backend described as optimized/mature.
- No broad Apple speedup claim found.
- RTDL is not described as a DBMS, renderer, ANN system, graph database, or general app framework.

## No Blockers Found

All three release gates (total test, documentation refresh, honesty-boundary audit) have passing evidence. No failing tests, no stale claims, no flow integrity issues were found.

## Required Next Step

Per `tag_preparation.md` and the gate report itself: **explicit user release authorization is still required before any tag is created or pushed.** This review satisfies the external AI review precondition only.
