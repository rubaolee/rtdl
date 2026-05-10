Here is the review of the RTDL v1.6.11 performance release-candidate matrix based on the provided documents.

### Verdict
**Approved.** The v1.6.11 performance matrix is exceptionally well-prepared, fail-closed, and honest. It achieves exactly what is required for a release-candidate preparation stage, setting up a rigorous and detailed measurement plan without prematurely authorizing a release tag or public claims before real hardware evidence is collected. The preflight checks are green, and the matrix is ready for pod execution.

### Strengths
- **Comprehensive Coverage**: The matrix covers all 18 public apps, correctly scoping execution and separating the two frozen/demo apps (`apple_rt_demo`, `hiprt_ray_triangle_hitcount`) from the 16 targets that require OptiX pod validation.
- **Strictly Fail-Closed**: It explicitly hardcodes `release_authorized: False` and `tag_authorized: False`. The manifest acts purely as an evidence-gathering plan.
- **Honest Constraints and Blocked Claims**: The configuration aggressively prevents overclaiming by explicitly blocking `whole_app_speedup`, `broad_rtx_or_gpu_acceleration`, and `stable_collect_k_bounded_promotion`. It correctly limits success criteria to measured sub-phases (e.g., "no DBMS-wide claim" or "no monolithic overlay claim").
- **Clear Pod Protocol**: It establishes a sound operational sequence by correctly asserting `pod_needed_now: False` (since local preflights are done) while enforcing `pod_required_for_final_perf_evidence: True` to prevent a blind release.
- **Enforced via Tests**: The design is backed by `goal1659_v1_6_11_perf_matrix_test.py`, which strictly asserts the fail-closed states, the blocked claims, and the exhaustive coverage of public apps.

### Risks
- **Experimental Primitive Leakage**: Apps utilizing `COLLECT_K_BOUNDED` (e.g., `segment_polygon_anyhit_rows` and `polygon_set_jaccard`) are correctly marked as `experimental_primitive_blocked`. The primary risk is that excellent pod timings for these rows could tempt reviewers into prematurely promoting `collect_k` to stable. The "no broad claim" acceptance boundary must be strictly enforced post-pod.
- **Legacy Engine Baseline Creep**: Apps such as `database_analytics`, `road_hazard_screening`, and `robot_collision_screening` run on legacy, customized engine surfaces. While accurately scoped here, there is a downstream risk that their benchmark numbers might be inadvertently presented as pure Python+RTDL proofs in future reporting.

### Required Changes
**None.** The matrix design is precise, safe, and fully aligned with the requirements of the final Python+RTDL-only release candidate before the partner release. You are cleared to proceed with scheduling the OptiX pod execution to gather the final performance evidence.
