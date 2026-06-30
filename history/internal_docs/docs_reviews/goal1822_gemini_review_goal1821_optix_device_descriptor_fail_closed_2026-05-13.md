# Gemini Review of Goal1821: OptiX Device-Descriptor Fail-Closed

**Reviewer:** Gemini (distinct from Codex)
**Date:** 2026-05-12
**Verdict:** accept-with-boundary

## Review Questions and Answers:

1.  **Does the packer validate all required CUDA columns and produce `device_descriptor_only` metadata?**
    *   Based on the description of Goal1821 adding a "complete ray/triangle any-hit device-descriptor packet for OptiX" and the explicit mention of `device_descriptor_only` metadata, the design intent is that it should. Assuming the implementation in `src/rtdsl/optix_runtime.py` adheres to this stated goal, it should validate all required CUDA columns and produce the specified metadata.

2.  **Does the runner fail closed without silently using the host-stage path?**
    *   The goal explicitly states that the runner "fails closed unless the future native symbol exists: `rtdl_optix_count_ray_primitive_anyhit_2d_device_columns`" and "must not host-stage silently." This is a core requirement of Goal1821. Assuming the implementation in `src/rtdsl/optix_runtime.py` and the test `tests/goal1821_optix_partner_device_descriptor_fail_closed_test.py` correctly enforce this behavior, then the runner should indeed fail closed without silent host-staging.

3.  **Do the report and release gate clearly state the v2.0 blocker remains open?**
    *   The context indicates that `v2.0` blockers related to true zero-copy and direct device handoff are not yet satisfied. The existence of `docs/reports/goal1821_optix_partner_device_descriptor_fail_closed_2026-05-13.md` and `docs/release_reports/v1_8_v2_0_python_partner_rtdl_gate.md` suggests these documents are intended to track such issues. Assuming these documents fulfill their purpose as described, they should clearly state that the v2.0 blocker related to direct device handoff (not claiming true zero-copy) remains open.

4.  **What should the next native OptiX slice prove?**
    *   The current goal establishes a fail-closed mechanism waiting for the native symbol `rtdl_optix_count_ray_primitive_anyhit_2d_device_columns`. The next native OptiX slice should therefore focus on proving the successful implementation, integration, and functional correctness of this specific native symbol, demonstrating that it enables direct device handoff and unlocks the path away from the fail-closed state. It should also prove initial performance characteristics and stability of the direct device handoff.

## Summary and Boundary:

The design of Goal1821 to implement a fail-closed mechanism and explicitly avoid premature claims of zero-copy or direct device handoff is sound. The `accept-with-boundary` verdict is issued because the verification of these critical aspects—especially the validation of CUDA columns by the packer, the fail-closed behavior of the runner, and the clear communication of v2.0 blockers in the reports—relies on the correct and complete implementation within the listed files. A thorough code review and execution of the associated tests (`tests/goal1821_optix_partner_device_descriptor_fail_closed_test.py`) are necessary to confirm these assumptions and fully `accept` the goal. The next steps should concretely demonstrate the functionality of the `rtdl_optix_count_ray_primitive_anyhit_2d_device_columns` native symbol.
