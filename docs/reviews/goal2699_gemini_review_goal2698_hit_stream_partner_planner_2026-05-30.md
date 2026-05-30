## Independent Gemini Review of Goal2698 Hit-Stream Partner Planner

Reviewer: Gemini
Date: 2026-05-30
Responds to: `docs/reports/goal2698_hit_stream_partner_continuation_planner_2026-05-30.md`

## Verdict

**accept-with-boundary.**

## Review Answers

### 1. Does the planner correctly combine neutral buffer handoff metadata with the support matrix without executing anything or overclaiming?

Yes, the planner correctly combines neutral buffer handoff metadata with the support matrix. The `plan_v2_5_hit_stream_partner_continuation` function in `src/rtdsl/hit_stream_handoff.py` explicitly calls `plan_v2_5_partner_support` from the support matrix and `_neutral_buffer_handoff_summary` to gather the necessary metadata. The resulting plan object includes fields like `support_cell` and `neutral_buffer_handoff_summary`, effectively merging these two critical pieces of information. Crucially, the function's docstring clearly states, "This is a planning surface only... It does not execute the partner continuation, prove zero-copy, or authorize speedup claims," and this boundary is reiterated in the returned plan object's `claim_boundary` field and in the Goal2698 report.

### 2. Are host-stage/copy needs, unsupported cells, pod-gated Triton paths, and zero-copy/speedup non-claims represented clearly enough?

Yes, these critical aspects are represented clearly and explicitly in the planner's output. The `plan_v2_5_hit_stream_partner_continuation` function returns fields such as:
- `copy_or_host_stage_required`: Indicates if an explicit copy or host-stage action is needed.
- `fail_closed`: Set to `True` for unsupported operations/partners, guiding failure.
- `pod_validation_required`: Highlights when `sm_70+` pod validation is necessary (e.g., for Triton).
- `true_zero_copy_authorized`: Explicitly `False`.
- `public_speedup_claim_authorized`: Explicitly `False`.
- `runtime_action`: Provides a concise summary of the next step (e.g., `plan_available`, `host_stage_or_copy_must_be_explicit`, `requires_sm70_pod_validation_before_performance_claim`, `fail_closed_unsupported_partner_operation`).

The example behaviors in `docs/reports/goal2698_hit_stream_partner_continuation_planner_2026-05-30.md` and the test cases in `tests/goal2698_hit_stream_partner_continuation_plan_test.py` confirm these representations work as intended.

### 3. Does this materially reduce risk before native OptiX CUDA hit-column work?

Yes, this planner materially reduces risk before native OptiX CUDA hit-column work can commence. By providing an explicit planning surface, it enables applications to:
- **Fail early:** Identify unsupported partner operations before any execution attempt.
- **Avoid hidden costs:** Clearly see when host-staging or copies are required, preventing silent performance penalties.
- **Understand claims:** Distinguish between operations that are merely planned, those needing pod validation, and those not authorized for zero-copy or speedup claims.
This "fail-closed" and "explain-first" approach ensures that subsequent native OptiX CUDA development can proceed with a much clearer understanding of the constraints and requirements, preventing wasted effort on unsupported paths or misinterpretations of data residency.

### 4. Are the tests and Windows/Linux validations sufficient for a no-pod planning milestone?

Yes, the tests and Windows/Linux validations are sufficient for a no-pod planning milestone. The `tests/goal2698_hit_stream_partner_continuation_plan_test.py` covers key scenarios:
- Reference continuation over host reference columns.
- Host-bridge to Triton, demonstrating explicit copy/host-stage requirements.
- Device columns to Triton, showing pod-gated validation.
- Unsupported partner operations leading to fail-closed behavior.

The successful `unittest` runs on both Windows and Linux, as detailed in the Goal2698 report, further confirm the planner's correctness across different environments for its intended "planning-only" scope. The tests ensure the metadata combination and decision logic are sound without requiring actual kernel execution.

### 5. What specific blockers remain before a real native CUDA-resident hit-stream output implementation should begin?

While Goal2698 provides a crucial planning surface, several significant blockers remain before a real native CUDA-resident hit-stream output implementation should begin. These largely align with the "Next Work" items in the Goal2698 report and the broader v2.5 development blockers identified in previous reviews (e.g., Goal2697):

1.  **Expanded Test Coverage and Benchmark Integration:** The planner needs to be integrated and run with expanded v2.5 test suites on both Windows and Linux. More importantly, it needs to be used within benchmark application code before partner execution paths are fully enabled, verifying its utility in real-world planning.
2.  **Pod-Gated Evidence Collection:** For scenarios requiring `sm_70+` pod validation (as highlighted by the planner's output), actual device-ready and pod-gated evidence must be collected. This is a prerequisite for any performance-related claims for native OptiX CUDA hit-column implementations.
3.  **Refactoring Torch-centric `hit_stream_handoff.py`:** As noted in Goal2697, the existing `hit_stream_handoff.py` still contains Torch-specific coercion logic. This needs to be refactored to be genuinely neutral (using DLPack / `__cuda_array_interface__`) to ensure "X's choice" and multi-partner composition without hidden copies.
4.  **Full Native Ownership/Lifetime Model Implementation:** The `neutral_buffer_seam` utilizes `"native_owned_pending_state_machine"`. The actual state machine for CUDA allocation, retention, release, and failure cleanup for resources managed by native OptiX needs to be fully designed and implemented.
5.  **Implementation of Native OptiX CUDA Output:** The core engineering task of modifying OptiX to produce bounded `ray_ids:int64`/`primitive_ids:int64` directly into CUDA-resident buffers remains. This is the ultimate goal, and the planner helps pave the way by formalizing the prerequisites.
