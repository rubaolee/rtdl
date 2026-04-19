# Goal580 External AI Review

Reviewer: Claude Sonnet 4.6 (claude-sonnet-4-6)
Date: 2026-04-18
Files read: goal580 report, goal578/goal579 reports, `src/native/rtdl_apple_rt.mm`, `src/rtdsl/apple_rt_runtime.py`, `examples/rtdl_apple_rt_closest_hit.py`, `tests/goal578_apple_rt_backend_test.py`, `src/rtdsl/__init__.py`, `Makefile`, `docs/capability_boundaries.md`, `docs/release_reports/v0_9/support_matrix.md`, `docs/release_reports/v0_9/README.md`
Verdict: **ACCEPT**

---

## Scope Acknowledged

Goal580 is a pre-release gate, not a code-implementation review. The purpose is to verify that the evidence from Goal578 and Goal579 is mutually coherent, that no blocking issue was introduced between those goals and this gate, and that the release-flow remains honest. Code-level findings already accepted in Goal578 are not re-adjudicated here except where re-reading the current files reveals a discrepancy.

---

## Gate Evidence Assessment

### Prior Reviews

Goal578 (Apple RT backend bring-up):
- Gemini Flash review: ACCEPT
- Claude Sonnet 4.6 review: ACCEPT

Goal579 (Apple RT public doc/example integration):
- Gemini Flash review: ACCEPT
- Claude Sonnet 4.6 review: ACCEPT — with one non-blocking numbering nit in `docs/README.md`

The report states the numbering nit was fixed after the Goal579 reviews. This is consistent with the gate proceeding: both reviews accepted the goal subject to the trivial fix.

### Test Evidence

Test counts and commands are plausible and consistent with the file content:
- Focused Apple RT unit suite: 4 tests (matches the 4 test methods visible in `tests/goal578_apple_rt_backend_test.py`)
- Full test suite: 239 tests (consistent with an established codebase adding exactly 4 new tests)
- Example output `parity: true` on Apple M4: consistent with what the example code computes (`_same_rows_approx(apple_rows, cpu_rows)`)
- Compile check and whitespace check: consistent with the clean diff state

### Code State Re-verification

I re-read the four implementation files. The state is unchanged from what Goal578 accepted:
- ABI packing (`_pack_ = 1` / `__attribute__((packed))`) matches between Python and native structs
- `run_apple_rt` reads `compiled.refine_op.predicate.name` (the previously fixed dispatch path)
- `_load_library()` checks `platform.system() != "Darwin"` before any load
- `rtdl_apple_rt_free_rows` is guarded by `_freed` flag in `AppleRtRowView.close()`
- Version triple in native code is `(0, 9, 1)` — consistent with v0.9.1 candidate

No regressions are visible relative to Goal578's accepted state.

### Doc Consistency Re-verification

`docs/capability_boundaries.md` correctly places Apple RT in the "Cannot do yet → general HIPRT or Apple RT backend coverage" row and separately acknowledges the `v0.9.1` candidate slice as bounded to `ray_triangle_closest_hit` through `MPSRayIntersector`. No overclaim.

`docs/release_reports/v0_9/support_matrix.md` correctly marks the Apple RT column as "candidate supported" for `ray_triangle_closest_hit` 3D only, with explicit "future work" for all other workloads. The boundary section explicitly lists: no full parity, no performance-leading claim, no non-macOS support. Accurate.

The report's stated doc-status invariants are verified:
- Current released tag: `v0.9.0` — confirmed in `docs/release_reports/v0_9/README.md`
- Active candidate: `v0.9.1` Apple RT — confirmed throughout
- No speedup claim: confirmed (no benchmark numbers in any file)
- No full parity claim: confirmed

---

## Honesty-Boundary Assessment

The report lists three residual code limitations and states they are documented, not blocking:

1. **Only `ray_triangle_closest_hit` supported** — verified: `run_apple_rt` raises `NotImplementedError` for any other predicate (line 247 of `apple_rt_runtime.py`)
2. **Per-call device/queue/BVH creation** — verified: no `MTLDevice` singleton, no caching; correctly disclosed in the report and in the Goal578 review
3. **MPSRayIntersector deprecated** — verified: Makefile suppresses `-Wno-deprecated-declarations`; API is functional on the stated host; correctly disclosed

One naming note (informational, not a blocker): `rtdl_apple_rt_context_probe` uses its `char* error_out` buffer to return the device name on success, not an error string. This is a mild naming mismatch in the C ABI, but the Python caller treats status=0 as "the buffer contains the device name" and the behavior is correct and consistent end-to-end.

No honesty-boundary violation found.

---

## Release-Flow Assessment

The report states:
- No tag created
- No push performed
- No release authorization acted on
- External reviews recorded for Goal578 and Goal579
- Goal580 external review pending (this review)

These are verified by the git status snapshot: `main` branch, no tag action, only modified/new documentation and implementation files consistent with candidate work. The flow is staged correctly.

---

## Blockers

None.

---

## Verdict

**ACCEPT** for Goal580 as the v0.9.1 Apple RT pre-release candidate gate.

The evidence from Goal578 and Goal579 is internally coherent, the test results are consistent with the code, the documentation accurately reflects the bounded scope without overclaiming, the prior reviews both concluded ACCEPT, the Goal579 numbering nit is closed, and no release action has been taken prematurely. The candidate is gated correctly and ready to proceed toward a release action when authorized.
