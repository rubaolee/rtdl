# Review Result: Goal4827 County x Zipcode Same-Source Status Review

**Date:** 2026-06-30
**Reviewer:** Antigravity (AI Coding Assistant)

---

## Verdict Label

`approve_goal4827_status_and_authorize_deterministic_author_baseline_goal`

---

## Review Question Answers

1. **Are the three RTDL changes valid general directed point-location / directed-overlay repairs rather than RayJoin-only hidden kernels?**
   Yes. All three modifications address general primitives in the `rtdsl` framework and the native OptiX library:
   - The SoS reported-distance contract correction in [rtdl_optix_core.cpp](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/native/optix/rtdl_optix_core.cpp#L1240) solves a generic issue where OptiX's hardware traversal depth pruning can bypass the software-level equal-depth tie-breaker by encoding the tie-breaker priority directly into `t_reported`.
   - The sorting correction in [rayjoin_overlay.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/rayjoin_overlay.py#L1385) removes an artificial `(eid0, eid1)` tie-breaker not present in the author's logic, aligning with the core mathematical specification.
   - The rational intersection preservation in [rayjoin_overlay.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/rayjoin_overlay.py#L1419) utilizes `Fraction` coordinates to compute midpoints before any truncation/rounding occurs. This follows the standard `ExactPoint` midpoint construction and prevents rounding drift.
   None of these changes introduce dataset-specific hardcodings; they are generic robustness improvements for directed point-location and overlay.

2. **Does the author determinism note justify the SoS direction used here: `query_map_id == 0` prefers larger slope and `query_map_id == 1` prefers smaller slope, encoded into `t_reported`?**
   Yes. The author's determinism note explicitly states that `query_map_id == 0` prefers a larger slope, and `query_map_id == 1` prefers a smaller slope.
   Encoding this preference into `t_reported` (making the preferred candidate report a slightly smaller distance) prevents OptiX hardware-pruning from bypassing the tie-break logic. While the committed author source comparator was reversed relative to their own documentation/comments due to a bug in their CUDA code, the author-reply determinism note defines the mathematically intended SoS tie-break direction. Resolving this contract discrepancy by using the intended SoS direction is fully justified, but it implies that we cannot expect byte-equality with the old nondeterministic/buggy author binary.

3. **Does preserving rational scaled intersection coordinates for midpoint PIP queries correctly follow the author `ExactPoint` midpoint construction?**
   Yes. The author's midpoint construction algorithm computes midpoints using the exact coordinates of the intersection points first, and then truncates them to internal coordinates (instead of averaging coordinates that have already been truncated to internal coordinate bounds). Preserving the rational `Fraction` coordinates (`scaled_x_rational` and `scaled_y_rational`) and using them to compute midpoints before truncation accurately follows the `ExactPoint` midpoint construction, keeping midpoint classification consistent with the author's exact geometric model.

4. **Is the public County x Soil byte-equality rerun sufficient to show the SoS correction did not break the official public sample?**
   Yes. Rerunning the public County x Soil sample produces a byte-equal output with identical byte length (`16631243`) and SHA256 (`464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`). This successfully confirms that the SoS/reported-t adjustment and rational coordinate preservation do not regress the official public validation sample.

5. **Does the County x Zipcode prefix evidence justify treating the old same-source author-output file as a debug clue rather than deterministic byte-equality truth?**
   Yes. The prefix probe findings demonstrate that the old same-source author-output file is not a stable deterministic truth. Because the original author binary did not adjust `t_reported`, the OptiX traversal order (which is hardware-dependent and nondeterministic) determined which equal-height candidate got pruned before the shader-internal slope tie-break could run. The old author-output file is therefore just one arbitrary run of a nondeterministic program and should only be used as a debug clue, not as a ground-truth byte-equality comparison target.

6. **Should performance remain blocked until a deterministic author-reference baseline is generated with the author-reply `t_reported` patch?**
   Yes. Verification of correctness against a deterministic baseline is a strict prerequisite before any performance work can be authorized. Since the same-source regenerated County x Zipcode pair's correctness is still unverified against a deterministic reference, performance testing remains strictly blocked.

7. **Is the recommended next goal correct: generate a deterministic author baseline from the author source plus the author-reply patch, then compare RTDL against that baseline on the same-source County x Zipcode pair?**
   Yes. To confirm correctness under a deterministic contract, RTDL's output must be compared against a ground-truth author-reference baseline that is itself deterministic. Generating this baseline by patching the author's source code with the `t_reported` fix and the correct slope tie-breaker direction, and then running it to produce a baseline, is the correct next step.

---

## Blockers and Dependencies

* **Lack of Deterministic Reference Baseline:** The primary blocker is the absence of a deterministic baseline for the same-source County x Zipcode pair. This is a critical blocker for validating correctness and must be addressed in the next goal.

---

## Strict Boundaries & Constraints

* **No Performance Claims:** Performance claims remain strictly unauthorized while correctness validation is blocked.
* **No Tuning to Nondeterministic Output:** Do not attempt to tune RTDL to match the old nondeterministic/buggy author-output file.
* **General Product Invariant:** The changes must remain general product repairs rather than RayJoin-only hidden kernels.
