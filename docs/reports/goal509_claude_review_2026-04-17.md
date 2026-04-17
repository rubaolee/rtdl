# Goal 509 External Review

Date: 2026-04-17
Reviewer: Claude (claude-sonnet-4-6)
Artifacts reviewed:
- `docs/reports/goal509_robot_barnes_linux_perf_report_2026-04-17.md`
- `docs/reports/goal509_app_perf_linux_raw_2026-04-17.json`
- `scripts/goal509_app_perf_linux.py`
- `tests/goal509_app_perf_harness_test.py`

## Overall Verdict: PASS

The benchmarks are fair, correctness-gated, repeatable within their stated scope, and honestly documented. One minor observation is noted below.

---

## Fairness

**PASS.**

Robot collision screening: all backends execute the identical `robot_edge_ray_hitcount_kernel` on the same deterministically generated edge rays and obstacle triangles. The CPU oracle (`rt.ray_triangle_hit_count_cpu`) is independent of the backends under test. The comparison is apples-to-apples.

Barnes-Hut candidate generation: all backends run the identical `barnes_hut_node_candidate_kernel` on the same body and node inputs. This is the right unit of comparison for RTDL's contribution.

Barnes-Hut full-app timing: the harness correctly separates candidate-generation time from full-application time, and the report explicitly names Python opening-rule and force-reduction work as the dominant cost. Claiming full-app timing as RTDL speedup would be misleading; the harness avoids this and the fairness contract in the JSON embeds the rationale.

---

## Correctness Gating

**PASS.**

Robot: the harness computes `matches_oracle` as an exact equality check on all four summary fields (row_count, hit_rows, total_hits, colliding_pose_count). CPU, Embree, and OptiX match at all three sizes. Vulkan fails at all three sizes — hit_rows and total_hits are systematically lower (approximately 2/3 of oracle) while colliding_pose_count matches. Vulkan timing is correctly marked `matches_oracle: false` in the raw JSON and the narrative report rejects it explicitly. The test `test_robot_cli_exposes_only_correctness_validated_gpu_backend` enforces that `vulkan` is absent from the public CLI.

Barnes-Hut: all four backends pass the candidate oracle at both sizes. Full-app reductions match the reference reduction (the `max_relative_error` field is correctly excluded from the structural equality check). The O(N^2) exact comparison at 256 bodies yields a max relative error of 0.018, which is consistent with a standard Barnes-Hut approximation at typical theta values. Skipping the exact comparison at 1,024 bodies is justified and acknowledged.

---

## Repeatability

**PASS with minor observation.**

Inputs are deterministic (grid-based layout, no randomness). Host metadata is captured in the raw JSON. Median of 3 iterations is used, which is robust to a single outlier.

**Observation — GPU JIT warmup is visible in max_sec but correctly handled:** the raw JSON shows very large first-iteration times for GPU backends (e.g., OptiX Barnes-Hut candidate at 256 bodies: median 0.00132 s, max 0.321 s; OptiX robot at 1,000 poses: median 0.049 s, max 0.364 s). This is a one-time JIT/driver initialization artifact. Because median of 3 is used and the outlier is always the first iteration, the reported medians correctly represent steady-state performance. However, with 3 iterations, only 2 post-warmup samples contribute to the median for GPU backends. This is sufficient evidence for the bounded scope of this report; it is not sufficient for tight confidence intervals or publication-grade benchmarking. The report's framing as "correctness-gated performance evidence" rather than a definitive benchmark is proportionate to this sample size.

---

## Honest Documentation

**PASS.**

The report explicitly states:
- It is "not a release authorization."
- The GTX 1070 has no RT cores; OptiX and Vulkan timings are GPU-execution evidence, not RT-core evidence.
- Vulkan is not a supported robot collision backend and must not be claimed as such.
- Barnes-Hut full-app timing is almost flat across backends because Python force reduction dominates; the speedup claim is rightly limited to candidate generation.
- The goal does not prove RTDL is faster than specialized robotics or N-body libraries.

The "Goal509 does not support these claims" section is explicit and complete. No overreach is present in the narrative. The separation between candidate-generation speedup (up to 1.53x for OptiX at 1,024 bodies) and full-app timing (essentially flat) is clearly communicated, including the structural reason for the flatness.

---

## Summary

All four review dimensions pass. The only note is the GPU JIT warmup visible in max_sec values, which is handled correctly by the median and is proportionate to the report's bounded evidence scope. No changes are required before using this report as internal performance evidence.
