## Review of Goal2845 v2.5 Internal Readiness Refresh

### 1. Does Goal2845 correctly index the post-2808 hardening chain from Goal2835 through Goal2844 in the internal readiness packet?

**Yes.** The file `src/rtdsl/v2_5_internal_readiness.py` explicitly lists the following reports and their corresponding reviews as `V2_5_INTERNAL_READINESS_REQUIRED_REPORTS` and `V2_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PATHS`:

*   `docs/reports/goal2835_primitive_payload_entrypoint_metadata_2026-05-31.md`
*   `docs/reports/goal2837_fixed_radius_graph_entrypoint_metadata_2026-05-31.md`
*   `docs/reports/goal2839_rtnn_same_stream_runner_mode_2026-05-31.md`
*   `docs/reports/goal2841_rtnn_same_stream_scale_probe_2026-05-31.md`
*   `docs/reports/goal2843_v2_5_execution_path_policy_2026-05-31.md`
*   `docs/reviews/goal2836_gemini_review_goal2835_primitive_payload_entrypoint_metadata_2026-05-31.md`
*   `docs/reviews/goal2838_gemini_review_goal2837_fixed_radius_graph_entrypoint_metadata_2026-05-31.md`
*   `docs/reviews/goal2840_gemini_review_goal2839_rtnn_same_stream_runner_mode_2026-05-31.md`
*   `docs/reviews/goal2842_gemini_review_goal2841_rtnn_same_stream_scale_probe_2026-05-31.md`
*   `docs/reviews/goal2844_gemini_review_goal2843_execution_path_policy_2026-05-31.md`

The test `tests/goal2845_v2_5_internal_readiness_refresh_test.py` (`test_internal_readiness_packet_indexes_post_2808_hardening_chain`) explicitly asserts the presence of these reports and reviews within the readiness packet, ensuring they are correctly indexed.

### 2. Is adding `execution_path_policy` to the core validations appropriate and bounded?

**Yes.** `execution_path_policy` is added to the `core_validations` in `src/rtdsl/v2_5_internal_readiness.py`. The `validate_v2_5_internal_readiness_packet` function checks that `packet["core_validations"]["execution_path_policy"]["status"]` is "accept".

The boundedness of `execution_path_policy` itself is confirmed by:
*   `src/rtdsl/v2_5_execution_path_policy.py`: Defines `V2_5_EXECUTION_PATH_POLICY_CLAIM_BOUNDARY` which explicitly states that it "does not hide dispatch, force a partner, authorize public speedup wording, authorize RT-core speedup wording, authorize whole-app speedup wording, authorize true zero-copy wording, or authorize release readiness."
*   `docs/reviews/goal2844_gemini_review_goal2843_execution_path_policy_2026-05-31.md`: This review confirms that Goal2843 (the `execution_path_policy`) "successfully implements a policy that clarifies execution path choices based on Goal2841's findings, without introducing hidden dispatches or making unauthorized performance claims."

This confirms that the addition is both appropriate as a core validation and that its claims remain strictly bounded.

### 3. Is the Goal2811 test edit a stale source-shape assertion repair rather than a runtime semantics change?

**Yes.** The `docs/reports/goal2845_v2_5_internal_readiness_refresh_2026-05-31.md` report explicitly states under "Implementation" that:
"The exact v2.4/v2.5 module-band pod run also exposed one stale test in Goal2811. The native code had moved from the old `&d_aggregate.ptr` source spelling to a cleaner `CUdeviceptr d_aggregate = prepared->d_ranked_aggregate->ptr` plus `&d_aggregate` kernel argument. Goal2845 updates only that source-shape assertion; it does not change native runtime behavior."

This is further validated by `tests/goal2845_v2_5_internal_readiness_refresh_test.py`'s `test_goal2811_guard_tracks_current_device_pointer_contract` which asserts the presence of the new source shape and the absence of the old one, verifying only the assertion was repaired.

### 4. Does the report honestly record the pod exact-band failure before repair and avoid pretending it was a runtime problem?

**Yes.** The `docs/reports/goal2845_v2_5_internal_readiness_refresh_2026-05-31.md` report under the "Pod broad signal before the Goal2811 assertion repair" section clearly shows:
*   `exact Goal2621-Goal2843 module band: Ran 694 tests in 16.854s, FAILED`
*   `only failure: Goal2811 stale source-shape assertion`

This honestly records the failure and explicitly attributes it to a "stale source-shape assertion", avoiding any pretense of a runtime issue.

### 5. Does Goal2845 avoid release, public speedup, broad RT-core, whole-app speedup, true zero-copy, package-install, Triton auto-selection, or native app-specific engine claims?

**Yes.**
*   `src/rtdsl/v2_5_internal_readiness.py` defines `V2_5_INTERNAL_READINESS_CLAIM_BOUNDARY` which explicitly lists all these claims as not authorized. It also includes `V2_5_INTERNAL_READINESS_BLOCKED_ACTIONS` with a comprehensive list of actions that are not allowed. The `validate_v2_5_internal_readiness_packet` function checks that all `claim_authorization` flags are `False`.
*   The `docs/reports/goal2845_v2_5_internal_readiness_refresh_2026-05-31.md` report under the "Boundary" section reiterates this precisely: "Goal2845 does not authorize release, public speedup wording, broad RT-core wording, whole-app speedup wording, true zero-copy wording, package-install wording, Triton preview auto-selection, or native app-specific engine claims."

### Verdict:
`accept-with-boundary`

Goal2845 successfully refreshes the internal readiness index, correctly incorporating the post-2808 hardening chain from Goal2835 through Goal2844. It appropriately adds `execution_path_policy` to core validations with proper boundaries. The Goal2811 test edit is indeed a repair of a stale source-shape assertion, not a runtime semantics change, and the report transparently documents the prior pod failure. Crucially, Goal2845 consistently and explicitly avoids all unauthorized public claims. This is an internal readiness index refresh plus stale-test repair, not a release gate.