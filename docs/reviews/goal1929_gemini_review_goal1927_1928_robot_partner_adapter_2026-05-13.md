# Goal1929 - Gemini Flash Review of Robot Collision v2 Partner Slice

Status: accept-with-boundary

Date: 2026-05-13

This is an independent Gemini/Antigravity review, distinct from Codex authoring. The v2.0 release remains blocked.

## Review Questions

### 1. Does the Goal1927 adapter keep the native engine app-agnostic by using only generic ray/primitive any-hit flags?

**Answer:** Yes, the Goal1927 adapter explicitly keeps the native engine app-agnostic. It leverages the native engine to produce generic `ray_primitive_any_hit_flags`, and the application-specific reduction logic (from ray flags to pose collision flags) is handled in the partner layer (Torch/CuPy), as confirmed by both the code (`src/rtdsl/partner_adapters.py` metadata: `"native_engine_row_contract": "generic_ray_primitive_any_hit_flags"`) and documentation (`docs/reports/goal1927_robot_collision_partner_pose_flags_adapter_2026-05-13.md`: "The native engine contract remains generic: `generic_ray_primitive_any_hit_flags`").

### 2. Is the Torch/CuPy reduction from per-ray flags to per-pose collision flags a reasonable v2.0 partner-layer app summary?

**Answer:** Yes, the Torch/CuPy reduction from per-ray flags to per-pose collision flags appears to be a reasonable v2.0 partner-layer app summary. The implementation in `src/rtdsl/partner_adapters.py` uses idiomatic and efficient tensor operations (`torch.scatter_add_` for Torch, `cupy.maximum.at` for CuPy) for GPU-based reduction. The documentation (`docs/reports/goal1927_robot_collision_partner_pose_flags_adapter_2026-05-13.md`) explicitly states this pattern aligns with the v2.0 strategy for app summaries without host row materialization, and this approach has received partial acceptance in broader V2.0 discussions (`docs/reports/goal1899_v2_strict_birth_gate_current_board_2026-05-13.md`).

### 3. Does the Goal1928 runner make a same-contract comparison against the v1.8 prepared OptiX pose-flag path?

**Answer:** Yes, the Goal1928 runner is explicitly designed to make a same-contract comparison. It measures the performance of both the v1.8 prepared OptiX pose-flag path (via `scripts/goal760_optix_robot_pose_flags_phase_profiler.py` within `scripts/goal1928_robot_collision_v2_partner_perf.py`) and the new v2.0 partner path (`rt.robot_collision_pose_flags_optix_prepared_partner_device_columns`), comparing performance for `pose_flags` and verifying numerical parity of `colliding_pose_count`. This is confirmed by the code and `docs/reports/goal1928_robot_collision_v2_partner_perf_2026-05-13.md`.

### 4. Are claim boundaries clear enough: no release authorization, no broad RT-core speedup, and no whole-app speedup yet?

**Answer:** Yes, the claim boundaries are very clear. Both the adapter code's metadata (`src/rtdsl/partner_adapters.py`) and the performance runner's output (`scripts/goal1928_robot_collision_v2_partner_perf.py`) explicitly set `v2_0_release_authorized`, `whole_app_speedup_claim_authorized`, and `broad_rt_core_speedup_claim_authorized` to `False`. The accompanying documentation (`docs/reports/goal1927_robot_collision_partner_pose_flags_adapter_2026-05-13.md`, `docs/reports/goal1928_robot_collision_v2_partner_perf_2026-05-13.md`) and the broader `docs/reports/goal1899_v2_strict_birth_gate_current_board_2026-05-13.md` release board consistently state that these claims are not authorized and remain blockers for a v2.0 release.

### 5. Identify any likely correctness, dtype, shape, or performance-analysis risks before pod execution.

**Answer:**
*   **Correctness Risk:** The parity check in `scripts/goal1928_robot_collision_v2_partner_perf.py` currently only validates the *count* of colliding poses (`colliding_pose_count_match`). A more robust correctness check would involve comparing the exact `pose_collision_flags` arrays between the v1.8 and v2.0 paths for perfect bit-wise equality, as it is possible for counts to match while individual flags differ due to subtle bugs.
*   **Dtype/Shape Risks:** The code includes checks for `uint32` ID range (`_require_uint32_id`), handles intermediate `int64` casts to prevent overflow during sums, and validates input/output array lengths, mitigating common dtype/shape issues.
*   **Performance-Analysis Risks:**
    *   **Scale of Data:** The documentation acknowledges that small row counts can lead to dispatch/setup-dominated timing, and larger packed-array rows are needed for meaningful performance insights. While current defaults are reasonable, full-scale production-like data should be prioritized for pod execution.
    *   **Empirical Validation:** The actual performance on an RTX pod, including potential overheads from Python/partner communication and the specific `scatter_add_`/`maximum.at` implementations, remains to be empirically validated. The `goal1899` document reinforces the need for RTX pod execution and validation.

## Verdict: accept-with-boundary

The implementation and documentation align well with the stated goals of Goal1927 and Goal1928, particularly in maintaining app-agnosticism of the native engine and clearly defining claim boundaries. The use of Torch/CuPy for app-layer reduction is consistent with the v2.0 vision.

The primary boundary for acceptance relates to the correctness verification: while `colliding_pose_count` parity is a good start, future pod execution should ideally include a byte-for-byte comparison of the resulting `pose_collision_flags` arrays for stronger correctness guarantees. The performance analysis risks are well-identified in the documentation itself, and their mitigation depends on proper pod execution.