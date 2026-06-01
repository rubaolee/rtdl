## Gemini Review: Goal2941-2945 Row-Stream Front Door Packet

**Date:** 2026-06-01
**Reviewer:** Gemini Agent

### Verdict: Accept

The Goal2941-2945 chain successfully introduces a generic, event-ordered hit-stream front door while rigorously maintaining all specified claim boundaries and ensuring no regressions in the canonical packet. The partner integration is explicit, with clear fail-closed mechanisms for unsupported operations. The proposed next step is a logical and generic extension of the current work.

### Findings:

#### 1. Do Goal2941-2945 preserve the app-agnostic native-engine boundary?
**Yes, the app-agnostic native-engine boundary is preserved.**

All relevant documentation and code consistently prohibit or explicitly disallow app-specific native engine logic. For example:
*   `docs/reports/goal2941_rayjoin_row_view_partner_columns_scale_probe_2026-06-01.md` states: "Goal2941 does not authorize app-specific native engine logic."
*   `src/rtdsl/partner_continuation_protocol.py` defines `RtdlPartnerContinuationOperation` with `app_specific_semantics_allowed: bool = False` and enforces this through `RtdlPartnerContinuationSpec`'s `__post_init__`, which raises a `ValueError` if app-specific semantics are allowed. The `validate_v2_5_partner_continuation_contract` function further confirms that operations reject app-specific semantics.
*   `src/rtdsl/v2_5_internal_readiness.py` lists `"native_app_specific_engine_logic"` in `V2_5_INTERNAL_READINESS_BLOCKED_ACTIONS`.
*   Tests such as `tests/goal2943_generic_event_ordered_hit_stream_front_door_test.py` explicitly assert the absence of app-specific vocabulary.

#### 2. Is the new public front door genuinely generic, or does it hide app-specific RayJoin/spatial/database logic?
**The new public front door appears genuinely generic.**

The primary function, `run_generic_ray_triangle_event_ordered_grouped_ray_id_reduction_3d` in `src/rtdsl/generic_primitives.py`, operates on generic inputs (`Ray3D`, `Triangle3D`) and processes them using generic concepts like `ray_id` and `primitive_id` for grouped reductions. The underlying primitive `hit_stream_grouped_ray_id_primitive_i64` (defined in `src/rtdsl/partner_continuation_protocol.py`) performs basic, generic aggregations (count, sum, xor, min, max) without any hidden app-specific RayJoin, spatial, or database logic. The documentation in `docs/reports/goal2943_generic_event_ordered_hit_stream_front_door_2026-06-01.md` also emphasizes the genericity of the operation.

#### 3. Are the partner-choice boundaries honest: explicit CuPy preview where implemented, Triton/Numba fail closed where not implemented, no hidden forced partner path?
**Yes, the partner-choice boundaries are honest and well-defined.**

`src/rtdsl/partner_continuation_protocol.py` clearly defines `PRIMARY_PARTNER` (Triton), `FALLBACK_PARTNER` (Numba), `CONFORMANCE_PARTNER` (CuPy), and `REFERENCE_PARTNER` (Python). It explicitly lists which operations are supported in preview by each partner (e.g., `V2_5_CUPY_PREVIEW_OPERATIONS` for `hit_stream_grouped_ray_id_primitive_i64`).

`src/rtdsl/v2_5_partner_support_matrix.py` uses `V2_5_SUPPORT_STATUS_PREVIEW`, `V2_5_SUPPORT_STATUS_DESCRIPTOR`, and `V2_5_SUPPORT_STATUS_UNSUPPORTED` to detail the status for each operation/partner pair. Unimplemented operations for Triton/Numba are marked `UNSUPPORTED`, implying a fail-closed mechanism. This is confirmed by `tests/goal2943_generic_event_ordered_hit_stream_front_door_test.py` which demonstrates that passing an unsupported partner raises a `ValueError`.

#### 4. Does the Goal2945 packet fairly show no regression after the front door?
**Yes, the Goal2945 packet shows no regression.**

Both `docs/reports/goal2942_current_packet_after_row_columns_pod/goal2855_summary.json` (before the front door) and `docs/reports/goal2945_current_packet_after_hit_stream_front_door_pod/goal2855_summary.json` (after the front door) report a `"status": "pass"` and `"all_pass": true` for all 7 canonical applications. There are no `"dirty_artifacts"` or `"claim_boundary_violations"`. The `docs/reports/goal2945_current_packet_after_hit_stream_front_door_pod/goal2945_triage.json` also reports `"status": "pass"` with no `"performance_targets"` or `"top_priority"`, indicating no identified performance regressions.

#### 5. Are all claim boundaries intact: no release, public speedup, broad RT-core, whole-app speedup, true-zero-copy, package-install, paper-reproduction, or app-specific engine-logic claims?
**Yes, all specified claim boundaries are intact and strictly enforced.**

All `.md` reports (`Goal2941`, `Goal2943`, `Goal2945`) consistently include explicit statements disallowing these claims. This is rigorously enforced in the codebase:
*   `src/rtdsl/partner_continuation_protocol.py` sets flags like `V2_5_PREVIEW_PUBLIC_SPEEDUP_CLAIM_AUTHORIZED = False` and raises `ValueError` if attempts are made to authorize these claims.
*   `src/rtdsl/v2_5_internal_readiness.py` explicitly lists all such claims in `V2_5_INTERNAL_READINESS_BLOCKED_ACTIONS` and sets their authorization to `False` in the readiness packet.
*   The `claim_boundary` fields within all reviewed JSON artifacts (e.g., `goal2941_rayjoin_row_view_partner_columns_large.json`, `goal2943_front_door_smoke.json`, `goal2855_summary.json`) consistently show `false` for flags like `public_speedup_claim_authorized` and `true_zero_copy_claim_authorized`.

#### 6. What should be the next generic runtime primitive after this chain? Please assess the proposed direction: prepared, event-ordered, payload-mapped primitive-column reductions over RT hit streams.
The `docs/reports/goal2945_current_packet_after_hit_stream_front_door_2026-06-01.md` report proposes: "The next generic runtime target is prepared, event-ordered, payload-mapped primitive-column reductions over RT hit streams."

**Assessment:** This direction is a sound and logical next step.
*   **"prepared"** builds on existing RTDL patterns and the `optix_row_view_to_partner_columns` adapter from Goal2941.
*   **"event-ordered"** leverages the successfully implemented generic event-ordered hit-stream front door from Goal2943.
*   **"payload-mapped primitive-column reductions"** generalizes the current `primitive_id` reduction to more flexible data handling, aligning with the "typed partner columns" concept.
*   **"over RT hit streams"** maintains focus on the core ray tracing output.
This proposed primitive maintains strong genericity by avoiding app-specific terms and building on established generic concepts, allowing for flexible processing of diverse per-primitive data.
