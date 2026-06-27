# Antigravity Review: V4 Goal4659 Hausdorff Official V4 Route

Date: 2026-06-25
Reviewer: Antigravity (Gemini 3.5 Flash)
Verdict: `accept_goal4659_app_route_progress_not_release`

---

## Scope

This review covers the following target files and resources:
- Call For Review: [call_for_review_v4_goal4659_hausdorff_official_route_2026-06-25.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/future/v4/reviews/call_for_review_v4_goal4659_hausdorff_official_route_2026-06-25.md)
- Evidence Report: [v4_goal4659_hausdorff_official_v4_route_evidence_2026-06-25.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/future/v4/v4_goal4659_hausdorff_official_v4_route_evidence_2026-06-25.md)
- Machine Summary: [summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/future/v4/evidence/v4_goal4659_hausdorff_v4_route_20260625/summary.json)
- Target Code:
  - [partner_adapters.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/partner_adapters.py)
  - [rtdl_hausdorff_distance_app.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py)
- Test File: [v4_goal4659_hausdorff_official_route_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4659_hausdorff_official_route_test.py)

---

## 1. Rationale

Goal4659 establishes valuable route progression for the `hausdorff_xhd` application. It successfully transitions the Hausdorff benchmark from a partial/adhoc operator coverage state into a legitimate, measured V4 app route:
1. **Generic Continuation**: The PyTorch continuation [global_argmax_u32_f64_partner_columns](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/partner_adapters.py#L3334) is written in a completely generic fashion. It relies on standard PyTorch CUDA mask-reduction and tensor operations without embedding any Hausdorff-specific logic or structures, complying with the requirement to avoid application-specific native kernels.
2. **Official Front Door**: The Hausdorff application route in [rtdl_hausdorff_distance_app.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py) successfully integrates the official V4 point-group nearest-witness interface (`prepare_point_group_nearest_witness_2d_device_arrays_v4` in [v4_point_group.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v4_point_group.py)) when targeting `partner="torch"`.
3. **Hot-Path Performance**: Telemetry shows that at correctness-passing scales (65,536 and 262,144 points per side), the PyTorch V4 hot path is faster than the V3.0.2 CuPy path (3.3x speedup at 65k points, 1.26x speedup at 262k points).
4. **Passable Tests**: The test suite in [v4_goal4659_hausdorff_official_route_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4659_hausdorff_official_route_test.py) successfully asserts the structural correctness of the route and checks the integrity of the collected telemetry.

However, key blockers remain that prevent this from being a final release:
1. **Correctness Block at Scale**: Both V3 (CuPy) and V4 (Torch) routes fail exact correctness verification at the 1,048,576 points per side scale. The tiled fixture produces large absolute coordinates which introduce floating-point precision issues because distance is computed using `float32` (though output as `float64`).
2. **Cold Prepare Overhead**: Prepare times for the V4 Torch official route (e.g. 5.45s at 262k points, 11.58s at 1M points) are slower than the V3 CuPy route (4.29s and 11.01s respectively), which highlights a cold-start overhead blocker.

---

## 2. Answers to Call for Review Questions

1. **Is the added Torch `global_argmax_u32_f64_partner_columns` a generic continuation rather than a Hausdorff-specific app kernel?**
   * **Yes**. The continuation is implemented in [partner_adapters.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/partner_adapters.py#L3334) using generic PyTorch operations. It does not mention or contain any Hausdorff-specific logic.
2. **Does the Hausdorff route actually use the official V4 `v4_point_group_nearest_witness_2d_device_arrays` surface for `partner="torch"`?**
   * **Yes**. In [rtdl_hausdorff_distance_app.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py#L906), the route constructs a session via `pg_v4.prepare_point_group_nearest_witness_2d_device_arrays_v4` and feeds the output into the PyTorch global argmax continuation.
3. **Is the evidence interpretation honest: real app-route progress, hot-path win at correctness-passing scales, but no broad V4 or unrestricted exact Hausdorff claim?**
   * **Yes**. The report and `summary.json` honestly distinguish the hot-path wins from cold-start overheads and clearly report the correctness failure at the 1M scale. They strictly state that release wording must contain the coordinate precision boundaries and avoid any broad speedup/release claims.
4. **Is the 1,048,576 points/side failure correctly treated as a blocker rather than hidden by the faster timings?**
   * **Yes**. It is explicitly declared as a blocker, and the next milestones require resolving it before any release.
5. **Are the next blockers correct: coordinate normalization or higher-precision native distance, prepare overhead, and app-level scorecard rerun?**
   * **Yes**. These three items target the exact deficiencies identified: float32 precision loss at scale, cold-start compile/prepare latency, and comprehensive app scorecard validation.

---

## 3. Non-Authorization Boundaries

To preserve strict V4 safety guardrails, this review **explicitly rejects and does NOT authorize**:
- **No V4 Release**: Does not authorize a formal V4 release, tag, or release-candidate publication.
- **No Broad V4 Speedup Claims**: Avoids any general speedup claims or marketing language concerning overall V4 performance or all-benchmark metrics.
- **No Unrestricted Exact Hausdorff Claims**: Any future claims must specify the coordinate magnitude and scale boundaries where float32 precision loss occurs.
- **No True Zero-Copy Claims**: The route host-stages query columns and does not support true zero-copy/device-resident handoff.
- **No Tier-3 Callback Support**: Blocks any arbitrary user-defined callback support or dynamic compilation hooks.
- **No C ABI / Embedding / Non-Python Host Support**: Keeps the execution model strictly within the Python/PyTorch/CuPy ecosystem.
- **No App-Specific Native Kernels**: Only allows generic operator composition continuations.
