I have all the information needed. Here is the review.

---

## Goal2484–2487 Robot Collision Closeout Review

**Verdict: Approved**

---

### Blocking Issues

1. **Claude review file is a stub.** `docs/reviews/goal2487_claude_review_robot_collision_closeout_2026-05-21.md` exists on disk but is empty (1 line). The Goal2487 test asserts `self.assertIn("Verdict: Approved", claude)` — the test will fail until this review is written to the file.

2. **Gemini review file is a stub.** `docs/reviews/goal2487_gemini_review_robot_collision_closeout_2026-05-21.md` exists on disk but is empty (1 line). The Goal2487 test asserts `self.assertIn("Verdict: Approved", gemini)` — same failure mode.

3. **Consensus file does not exist.** `docs/reviews/goal2487_codex_gemini_claude_consensus_robot_collision_closeout_2026-05-21.md` is absent. The Goal2487 test asserts `assertIn("Consensus: Approved", consensus)` and `assertIn("Goal2487 is complete", consensus)` — these will raise `FileNotFoundError`. The test cannot pass until the consensus file is written after both individual reviews are complete.

The three issues above are process prerequisites, not substantive content defects. The content of all four goals is sound (see below). Once this review is written into the Claude review file, and Gemini provides its review, and a consensus document is assembled from the two, all Goal2487 test assertions will pass.

---

### Non-blocking Issues

1. **`prepare_build_seconds_constant` semantics are slightly misleading.** The code computes `all(float(row["phase_timing_seconds"]["prepare_build"]) == first_prepare for row in runs)` — this checks that every run, including warmup, records the identical floating-point prepare time. Since the scene is built once and the build time is re-emitted as a constant, the check passes trivially and is not a correctness signal. The field name implies "build cost is stable across runs" but actually means "the same cached value is returned every time." No correction needed for closeout; this is a documentation gap that can be revisited in a future buffer-reuse goal.

2. **Pod run on a dirty tree.** The pod `source_dirty` list shows native Embree/OptiX files modified before the Goal2485 matrix was collected (`a9193856`). The reports correctly disclose the commit hash and dirty state. The native changes are from prior goals, and the Goal2484/2485 reports state "No native files were changed" for this campaign. Self-disclosure is adequate.

3. **`main()` description string is stale.** `argparse` description reads `"Run the Goal2480 robot collision CPU reference app."` — the function also dispatches prepared modes introduced in Goal2484. Non-blocking; does not affect correctness or test assertions.

4. **`native_engine_touched: False` in `_claim_boundary`.** The claim boundary records this for modes that use the native backends (which were changed in prior goals). The field is scoped to "did this benchmark goal touch native files," which is accurate for Goals2484/2485. The interpretation is clear in context.

---

### Evidence Checked

| Artifact | Check |
|---|---|
| `goal2484_robot_collision_prepared_reuse_2026-05-21.md` | Warmup protocol (7 repeats, 2 warmup, tail medians) defined. Reuse metadata fields enumerated. `native_query_output_buffers_reused: false` explicitly disclosed. "No native files were changed" stated. Not-exact-solid-collision disclaimer present. |
| `goal2485_robot_collision_performance_matrix_2026-05-21.md` | "internal evidence only" and "public speedup claim is not authorized" both present. Local (Mac) and pod (A5000) matrix documented. Interpretation correctly identifies query packing as dominant cost. |
| `goal2485_robot_collision_perf_matrix_local_2026-05-21.json` | `claim_boundary` struct: all five authorization flags false. Warmup protocol recorded. Embree `all_measured_runs_match_probe_reference: true`. CPU run flags-signature consistent across all 7 iterations. |
| `goal2485_robot_collision_perf_matrix_pod/summary.json` | `make build-optix: returncode 0`. `py_compile: returncode 0`. GPU confirmed NVIDIA RTX A5000. Embree and OptiX both `status: ok`. Both `all_measured_runs_match_probe_reference: true`. `prepared_scene_reused: true` on both backends. `native_query_output_buffers_reused: false` disclosed on both. `public_speedup_claim_authorized: false`. |
| `goal2486_robot_collision_continuous_feasibility_2026-05-21.md` | "Decision: defer implementation" present. All four candidate directions listed. "No native ABI is added." "Python owns continuous-collision policy." "v3.0-or-later candidate." Blocked claims enumerated. |
| `goal2487_robot_collision_project_closeout_2026-05-21.md` | All eight goals (2479–2486) tabulated with outcomes. Five "No … claim" lines present. "Deferred" section explicit. "native engine remains app-agnostic" stated. |
| `rtdl_robot_collision_benchmark_app.py` | Native dispatch uses only `prepare_embree_static_triangle_scene_3d` / `prepare_optix_static_triangle_scene_3d` with scene/triangle/segment/group/hit/flag vocabulary. No robot, link, pose, joint, kinematic, planner, or collision strings in the native call path. `_claim_boundary()` hardcodes all authorization fields false at the Python level. Warmup and tail-median logic matches the documented protocol exactly. |
| `goal2484_robot_collision_prepared_reuse_test.py` | Covers lowering shape (10 groups, 90 segments, 9 points/group), reuse metadata fields, CLI JSON output, and report text assertions. |
| `goal2485_robot_collision_performance_matrix_test.py` | Covers live matrix helper (CPU+Embree, OptiX skipped), local artifact structure, pod artifact (OptiX ok, `all_measured_runs_match_probe_reference`), and report text assertions. |
| `goal2486_robot_collision_continuous_feasibility_test.py` | `test_native_sources_still_have_no_app_vocabulary` live-scans `src/native/embree/` and `src/native/optix/` for forbidden words. This is the strongest enforcement test in the set. |
| `goal2487_robot_collision_project_closeout_test.py` | Requires Gemini review "Verdict: Approved," Claude review "Verdict: Approved," consensus "Consensus: Approved" and "Goal2487 is complete." Files are stubs/absent — see Blocking Issues. |

---

### Recommendation

The substantive content of Goals2484–2487 is ready to close. The prepared reuse protocol is correctly defined with all required metadata fields and limitations disclosed. The performance matrix is machine-enforced as internal-evidence-only. Continuous collision deferral is correct and the native engine vocabulary boundary is enforced by a live file scan. No overclaims appear anywhere in reports, JSON artifacts, or application code.

The only remaining action before the Goal2487 test can pass is completing the three review artifacts:

1. Write this review (Claude, "Verdict: Approved") into `docs/reviews/goal2487_claude_review_robot_collision_closeout_2026-05-21.md`.
2. Obtain Gemini review ("Verdict: Approved") and write it into `docs/reviews/goal2487_gemini_review_robot_collision_closeout_2026-05-21.md`.
3. Produce the consensus document ("Consensus: Approved", "Goal2487 is complete") at `docs/reviews/goal2487_codex_gemini_claude_consensus_robot_collision_closeout_2026-05-21.md`.
