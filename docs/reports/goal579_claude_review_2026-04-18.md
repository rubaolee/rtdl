# Goal579 External Review: v0.9.1 Apple RT Public Doc And Example Integration

Reviewer: Claude Sonnet 4.6 (external AI review)

Date: 2026-04-18

Verdict: **ACCEPT**

---

## Scope

This review covers Goal579: the public-facing doc and example integration of the Goal578 Apple RT backend slice. The review checks all twelve listed changed files against the stated honesty boundaries.

Files reviewed:

- `README.md`
- `docs/README.md`
- `docs/capability_boundaries.md`
- `docs/current_architecture.md`
- `docs/quick_tutorial.md`
- `docs/release_facing_examples.md`
- `docs/rtdl_feature_guide.md`
- `docs/tutorials/README.md`
- `docs/release_reports/v0_9/README.md`
- `docs/release_reports/v0_9/support_matrix.md`
- `examples/README.md`
- `examples/rtdl_apple_rt_closest_hit.py`

---

## Per-File Findings

### README.md

Correctly presents v0.9.0 as the current released version. Apple RT is consistently described as a "v0.9.1 candidate slice" in all three relevant sections (top summary, version status table, and current release state). Build instructions are clearly labeled "Active v0.9.1 Apple RT candidate path." No speedup claim, no full parity claim. Backend names section correctly marks Apple RT as "active v0.9.1 candidate backend surface." **No issues.**

### docs/README.md

Apple RT example added at step 13 in the new user path, after the HIPRT example, before the release statements. Live documentation section links the Apple RT example. Live state summary correctly says: "active v0.9.1 candidate line adds Apple Metal/MPS run_apple_rt support for 3D ray_triangle_closest_hit; it does not claim full Apple backend parity or measured speedup yet."

Minor nit: After inserting step 13, the conditional "If you need the previous graph release line" block still uses numbers 16 and 17, which now collide with the v0.7 items immediately above. This is a numbering cosmetic issue; the content is correct and the links are accurate. **Non-blocking.**

### docs/capability_boundaries.md

Short-version table's "cannot do yet" cell is updated to include "general HIPRT or Apple RT backend coverage." A new dedicated "Apple RT Backend Coverage" subsection under "What RTDL Cannot Do Yet" is correctly scoped: `run_apple_rt` supports only 3D `ray_triangle_closest_hit` after `make build-apple-rt`; no broad parity, no Apple hardware speedup, no non-macOS, no prepared reuse, no broader workload matrix support. The capability section on "RTDL + Python Applications" also correctly places Apple RT as a narrower "v0.9.1" candidate under the broader HIPRT direction. **No issues.**

### docs/current_architecture.md

Header updated to reference v0.9.1 Apple RT candidate. Backend roles table gains an "Apple RT" row: "active macOS Apple Silicon Metal/MPS candidate for 3D closest-hit." Ownership paragraph correctly says "does not claim full Apple backend parity or performance speedup yet." Current boundaries section explicitly says not to read the system as "a claim that Apple RT has full workload parity or measured speedup beyond the current 3D closest-hit candidate slice." **No issues.**

### docs/quick_tutorial.md

Backend note bullet added: "active v0.9.1 Apple RT candidate support exists on Apple Silicon macOS; run_apple_rt currently covers 3D ray_triangle_closest_hit through Apple Metal/MPS only." Build step added: `make build-apple-rt`. Step 3 tutorial section adds the Apple RT example invocation after HIPRT, with clear "Apple Silicon Mac" qualifier. **No issues.**

### docs/release_facing_examples.md

"Choose By Job" table adds "Apple RT example" row. Introductory coverage list correctly says "active v0.9.1 Apple RT candidate example, clearly marked as a macOS/Apple-Silicon closest-hit slice." A dedicated "Apple RT Backend Candidate" section matches Goal578 scope exactly: bounded by Goal578, one 3D closest-hit ray/triangle workload, `MPSRayIntersector`. Unsupported claims list is explicit: no full backend parity, no hardware speedup, no non-macOS, no broader workload matrix support. **No issues.**

### docs/rtdl_feature_guide.md

v0.9.1 mentioned in the "What RTDL Is Today" summary. Backend list adds "v0.9.1 candidate Apple RT backend slice for 3D closest-hit ray/triangle traversal on macOS Apple Silicon." Release layers table gains "v0.9.1: in-progress Apple Metal/MPS RT backend slice for closest-hit." Non-claims list correctly says "full Apple RT backend parity or Apple hardware speedup evidence beyond the current bounded 3D closest-hit candidate slice." **No issues.**

### docs/tutorials/README.md

Tutorial ladder gains step 11: "Apple RT Closest-Hit Example" — "See the active v0.9.1 Apple Metal/MPS closest-hit candidate." Track 3 application demos section links the Apple RT example. After-tutorials section also links it. All three occurrences are correctly labeled as the active candidate, not a released feature. **No issues.**

### docs/release_reports/v0_9/README.md

Post-release note added, correctly attributed to Goal578. Links to Goal578 implementation report, Gemini review, and Claude review. Note is bounded: "bounded candidate slice, not a full Apple backend parity claim or speedup claim." **No issues.**

### docs/release_reports/v0_9/support_matrix.md

Status line updated: "`v0.9.0` released; `v0.9.1` Apple RT candidate is active on main." Backend status table adds "Apple RT" row: "v0.9.1 candidate backend via Apple Metal/MPS on macOS Apple Silicon." New "Apple RT / v0.9.1 Candidate Matrix" section added with correct table: `ray_triangle_closest_hit` 3D shows "supported" for CPU Python reference, `run_cpu`, and Embree; "candidate supported" for Apple RT; "future work" for OptiX, Vulkan, HIPRT. Local M4 evidence references are accurate (Goal578). Boundary paragraph is correct and explicit. **No issues.**

### examples/README.md

"Start Here" table adds "Apple RT example" row with accurate description: "3D rays and 3D triangles become nearest-hit rows through the Apple Metal/MPS path." File list includes `rtdl_apple_rt_closest_hit.py`. "Current Apple RT boundary" section correctly scopes the candidate to `ray_triangle_closest_hit` over 3D rays/triangles, not full parity, not measured speedup. **No issues.**

### examples/rtdl_apple_rt_closest_hit.py

Example structure is correct. The kernel uses `ray_triangle_closest_hit(exact=False)`, which is consistent with the "candidate" and "approximate" language used in docs. CPU Python reference is computed first as a truth path. `run_apple_rt` attempt is wrapped in a try/except that catches `FileNotFoundError`, `OSError`, `RuntimeError`, `NotImplementedError`, and `ValueError` — sufficient to handle unavailable backend, missing dylib, and unsupported operation. Output JSON includes `apple_rt_available: false` and `apple_rt_error` on failure; `apple_rt_available: true`, parity check result, and both row sets on success. The scene is small and deterministic (3 rays, 2 triangles, fixed geometry). The `_same_rows_approx` comparison uses `tolerance=1e-5`, consistent with `float_approx` precision. No speedup claim in the output. **No issues.**

---

## Honesty Boundary Check

| Stated boundary | Observed in docs/example |
| --- | --- |
| v0.9.0 is current released version | Correct in all files |
| v0.9.1 is candidate, not released | Correct; "candidate", "active", "in-progress" used consistently |
| Apple RT = macOS Apple Silicon only | Correct; every mention qualifies the platform |
| run_apple_rt = 3D ray_triangle_closest_hit only | Correct; no broader workload claims |
| No full Apple backend parity claim | Correct; explicit non-claims in every relevant file |
| No Apple hardware speedup claim | Correct; no timing or speedup numbers anywhere |
| No prepared Apple RT reuse claim | Correct; explicitly listed as unsupported in capability_boundaries.md and examples/README.md |

All seven honesty boundaries are maintained consistently across all twelve changed files.

---

## Blockers

None.

---

## Non-Blocking Notes

1. **docs/README.md numbering collision**: The conditional "If you need the previous graph release line" block still numbers v0.6 entries as 16 and 17, which now collide with the main-path v0.7 entries after the Apple RT step was inserted at 13. Content is correct; only the list numbers are ambiguous. Suggested fix: renumber the conditional block as 18-19, or drop the numbering from the conditional block entirely.

---

## Reviewer Honesty Boundaries

This is a document and example review, not a hardware validation. I cannot independently:

- run the code on an Apple M4 or verify the reported parity result
- inspect the native Metal/MPS implementation in `src/native/rtdl_apple_rt.mm`
- verify that the build system produces a correctly-linked `librtdl_apple_rt.dylib`

The test evidence cited (239 tests pass, 4 focused Goal578 tests pass) is accepted as the author's claimed result. The review is limited to: are the public-facing claims consistent with the stated scope, and are the honesty boundaries correctly maintained?

On those questions: yes, and yes.

---

## Final Verdict

**ACCEPT**

Goal579 public doc and example integration is correct, consistently scoped, and satisfies all stated honesty boundaries. The one non-blocking numbering nit in `docs/README.md` does not affect content accuracy or the release honesty story.
