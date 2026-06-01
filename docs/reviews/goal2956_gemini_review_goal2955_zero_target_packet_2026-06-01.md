# Independent Review: Goal2955 Zero-Target v2.5 Packet

**Date:** 2026-06-01
**Reviewer:** Gemini CLI
**Target:** Goal2955: current packet after RTNN graph replay, with zero performance targets in the triage output.
**Output Path:** docs/reviews/goal2956_gemini_review_goal2955_zero_target_packet_2026-06-01.md

## Scope

This review covers the following chain of work:
- Goal2948: payload grouped-sum front-door scale evidence.
- Goal2950: RayDB-style payload grouped-sum front-door probe and planner guard.
- Goal2952: Hausdorff target-8192 default tuning.
- Goal2954: RTNN CUDA graph replay route tuning.
- Goal2955: current packet after RTNN graph replay, with zero performance targets in the triage output.

Primary files reviewed:
- `docs/reports/goal2948_payload_grouped_sum_scale_probe_2026-06-01.md`
- `docs/reports/goal2950_raydb_payload_grouped_sum_front_door_probe_2026-06-01.md`
- `docs/reports/goal2952_hausdorff_target8192_default_tuning_2026-06-01.md`
- `docs/reports/goal2954_rtnn_graph_replay_route_tuning_2026-06-01.md`
- `docs/reports/goal2955_current_packet_after_rtnn_graph_replay_2026-06-01.md`
- `scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py`
- `scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py`
- `scripts/goal2902_v2_5_current_packet_perf_triage.py`
- `src/rtdsl/v2_5_internal_readiness.py`
- `tests/goal2955_current_packet_after_rtnn_graph_replay_test.py`
- `docs/reports/goal2955_current_packet_after_rtnn_graph_pod/goal2855_summary.json`
- `docs/reports/goal2955_current_packet_after_rtnn_graph_pod/goal2955_triage.json`

## Questions To Answer

1.  Does the evidence support the narrow internal conclusion that the current v2.5 packet has zero performance targets under the existing triage rules?
2.  Are the recent route choices technically sound and generic rather than app-specific native-engine customizations?
3.  Are the claim boundaries preserved? In particular, no v2.5 release, public speedup, broad RT-core, whole-app speedup, true zero-copy, package-install, Triton auto-selection, or paper-reproduction claim should be authorized.
4.  Does the RayDB planner guard correctly prefer primitive-first fused grouped reduction when that route is faster than payload hit-stream continuation?
5.  Does the Hausdorff target-8192 default evidence justify the default change without overclaiming against X-HD?
6.  Does the RTNN graph replay route evidence justify the canonical harness route change without overclaiming against the RTNN paper?
7.  What must remain blocked before any v2.5 release packet or 3-AI release consensus?

## Findings

**1. Does the evidence support the narrow internal conclusion that the current v2.5 packet has zero performance targets under the existing triage rules?**

Yes, the evidence strongly supports this conclusion.
- The `docs/reports/goal2955_current_packet_after_rtnn_graph_replay_2026-06-01.md` report explicitly states: "This is the first current v2.5 packet where the triage script reports zero performance targets across the 10-app foundation."
- The `docs/reports/goal2955_current_packet_after_rtnn_graph_pod/goal2955_triage.json` artifact confirms this with `"performance_targets": []` and `"status": "pass"`.
- The `tests/goal2955_current_packet_after_rtnn_graph_replay_test.py` also asserts `self.assertEqual("pass", triage["status"])` and `self.assertEqual([], triage["performance_targets"])`.

**2. Are the recent route choices technically sound and generic rather than app-specific native-engine customizations?**

Yes, the route choices are technically sound and generic.
- **Goal2950 (RayDB):** The report `docs/reports/goal2950_raydb_payload_grouped_sum_front_door_probe_2026-06-01.md` highlights that the "payload-grouped front door is for workloads where the user needs a generic post-RT partner continuation that is not already expressible as a fused RTDL primitive." It also notes that "primitive-first fused grouped reduction is still expected to win because it already matches the app-agnostic operation exactly," indicating a preference for generic fused primitives when applicable.
- **Goal2952 (Hausdorff):** The report `docs/reports/goal2952_hausdorff_target8192_default_tuning_2026-06-01.md` explicitly states, "This is an app-level parameter/default tuning change. It does not add Hausdorff-specific native ABI names, does not customize the native engine..."
- **Goal2954 (RTNN):** The report `docs/reports/goal2954_rtnn_graph_replay_route_tuning_2026-06-01.md` confirms, "This is a generic runtime route change over the fixed-radius ranked-summary aggregate primitive family. It does not add RTNN-specific native code."
- The "Interpretation" section of `docs/reports/goal2955_current_packet_after_rtnn_graph_replay_2026-06-01.md` reinforces this pattern: "choose an existing generic RTDL route before adding primitives."

**3. Are the claim boundaries preserved? In particular, no v2.5 release, public speedup, broad RT-core, whole-app speedup, true zero-copy, package-install, Triton auto-selection, or paper-reproduction claim should be authorized.**

Yes, the claim boundaries are consistently preserved across all reviewed goals and the overall packet.
- Each report (`goal2948`, `goal2950`, `goal2952`, `goal2954`, `goal2955`) contains a "Boundary" section explicitly disclaiming public speedup, whole-app speedup, broad RT-core, paper reproduction, and v2.5 release claims.
- The `src/rtdsl/v2_5_internal_readiness.py` module defines `V2_5_INTERNAL_READINESS_BLOCKED_ACTIONS` and `V2_5_INTERNAL_READINESS_CLAIM_BOUNDARY` which explicitly list all the unauthorized claims mentioned in the question.
- The `tests/goal2955_current_packet_after_rtnn_graph_replay_test.py` includes assertions like `self.assertFalse(summary["claim_boundary"]["v2_5_release_authorized"])` and `self.assertFalse(summary["claim_boundary"]["public_speedup_claim_authorized"])`, confirming these boundaries are programmatically checked.

**4. Does the RayDB planner guard correctly prefer primitive-first fused grouped reduction when that route is faster than payload hit-stream continuation?**

Yes, the RayDB planner guard correctly prefers the primitive-first fused grouped reduction.
- The "Design Decision" section in `docs/reports/goal2950_raydb_payload_grouped_sum_front_door_probe_2026-06-01.md` explicitly states: "RayDB `count` and `sum` should not force the generic hit-stream continuation when an exact fused RTDL primitive already exists. The fused primitive is one to two orders of magnitude faster for this workload."
- The "Pod Results" table in the same report demonstrates this with "Primitive-first sec" being significantly lower (e.g., `0.000345s` vs `0.009484s` for 250000 `count`) than "Payload front door sec", showing performance gains of 27x to 310x.

**5. Does the Hausdorff target-8192 default evidence justify the default change without overclaiming against X-HD?**

Yes, the evidence justifies the Hausdorff target-8192 default change without overclaiming.
- The "Pod Evidence" in `docs/reports/goal2952_hausdorff_target8192_default_tuning_2026-06-01.md` shows that for the `8192 x 8192` fixture, using `8192` target points per group with the `reduced` method resulted in `0.007006` Median sec, which is `0.843x` the CuPy baseline (meaning faster).
- The "Clean default confirmation" section further solidifies this with RTDL (`0.007071s`) outperforming CuPy (`0.008258s`), yielding a `0.856x` ratio.
- The "Boundary" section explicitly restricts claims: "It does not add Hausdorff-specific native ABI names, does not customize the native engine, and does not authorize public speedup, whole-app speedup, broad RT-core, X-HD reproduction, or v2.5 release claims."

**6. Does the RTNN graph replay route evidence justify the canonical harness route change without overclaiming against the RTNN paper?**

Yes, the evidence justifies the RTNN graph replay route change without overclaiming.
- The "Pod Evidence" in `docs/reports/goal2954_rtnn_graph_replay_route_tuning_2026-06-01.md` clearly shows that the "prepared-query batch CUDA graph replay f32" route consistently outperforms other routes and the CuPy baseline across uniform, clustered, and shell distributions. For example, for the uniform distribution, RTDL graph replay is `1.187x` faster than CuPy.
- The "Boundary" section clarifies that the goal "does not authorize public speedup, whole-app speedup, broad RT-core, RTNN-paper reproduction, or v2.5 release claims." It specifically notes that it "only records that... the existing graph replay route removes the remaining uniform weak row and improves all three measured distributions."

**7. What must remain blocked before any v2.5 release packet or 3-AI release consensus?**

Based on `src/rtdsl/v2_5_internal_readiness.py`, the following actions must remain blocked:
- `v2_5_release`
- `release_tag_action`
- `public_speedup_wording`
- `broad_rt_core_speedup_wording`
- `whole_app_speedup_wording`
- `true_zero_copy_wording`
- `package_install_wording`
- `triton_preview_auto_selection`
- `native_app_specific_engine_logic`

These are also reflected in the `claim_authorization` section of `src/rtdsl/v2_5_internal_readiness.py`, where all corresponding flags are set to `False`.

## Verdict

`accept-with-boundary`

The implementation and evidence for Goal2955, encompassing the chain of work from Goal2948 through Goal2954, are found to be sound. The internal conclusion that the current v2.5 packet has zero performance targets under existing triage rules is well-supported by the provided data and confirmed by automated tests. The recent route choices are technically sound and generic, avoiding app-specific native-engine customizations. Claim boundaries are consistently preserved across all reports and internal readiness checks, explicitly blocking any v2.5 release, public speedup, or other unauthorized claims. The RayDB planner guard correctly prioritizes primitive-first fused reductions when faster, and the Hausdorff and RTNN route changes are justified by performance improvements without overclaiming.

However, as stipulated in the prompt and confirmed by the `v2_5_internal_readiness.py` module, significant release and public claims remain blocked. This includes, but is not limited to, `v2_5_release`, `public_speedup_wording`, `broad_rt_core_speedup_wording`, `whole_app_speedup_wording`, `true_zero_copy_wording`, `package_install_wording`, `triton_preview_auto_selection`, and `native_app_specific_engine_logic`. The current work represents internal engineering progress and readiness for further review, not a green light for external promotion or release.
