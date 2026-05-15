# Goal2091 — Copilot supplemental review for Goal2088 (post-streaming v2 release-prep)

Date: 2026-05-15

Note: supplemental review while Claude is unavailable. This does NOT replace the required fresh Claude-family review for 3-AI release consensus.

Summary: The packet is sound and well-scoped; ready for final consensus pending the missing Claude review and the documented prep steps. Final verdict (single word):

accept-with-boundary

---

1) Does Goal2088 correctly supersede the stale Goal2073 claim that `segment_polygon_anyhit_rows` is still mixed?

Yes. Goal2088, plus Goals 2081/2083/2086, replaces the old full-Python-row output contract with the streaming exact witness-column contract. Goal2083 pod timings (count=16384 -> v2 0.001421s vs v1.8 1.905528s) and Goal2086 scale runs show the mixed classification is resolved for the streaming contract; the old full-Python-row path remains documented as slower.

2) Does Goal2085 support that all 16 current OptiX/RT rows have v2/v1.8 < 1.0 under their documented contracts?

Yes. The Goal2085 OptiX/RT table (markdown + JSON) lists 16 rows and the recorded v2/v1.8 ratios are all below 1.0 (examples: segment_polygon_anyhit_rows 0.0007x, robot_collision_screening 0.367x). JSON artifacts corroborate the table.

3) Is the streaming exact witness-column contract a valid v2.0 replacement while preserving the boundary that old full-row materialization is not claimed fast?

Yes. Design docs (Goal2081) and pod evidence (Goal2083, Goal2086) demonstrate a valid app-layer replacement that preserves the native engine contract and moves exact filtering to partner device columns. All artifacts explicitly preserve the boundary that the old full-Python-row materialization is not claimed fast.

4) Are Embree CPU rows framed correctly as bounded same-contract evidence rather than headline GPU partner-speedup evidence?

Yes. The reports and table notes explicitly treat Embree as a CPU same-contract surface; GPU partner speedups are attributed to OptiX/CuPy rows. Embree near-parity rows are documented as bounded CPU evidence, not blockers.

5) Are claim boundaries preserved (no package-install claim, no arbitrary partner acceleration claim, no broad RT-core claim, no arbitrary polygon overlay claim, no v2.0-is-released claim)?

Yes. Claim-boundary sections across Goal2088, Goal2073, the JSON claim_boundary entries, and Gemini reviews list these items as "not allowed" and retain the explicit requirement that a user-requested release action is required before announcing v2.0.

6) Is the packet ready for final consensus once the missing Claude-family review is available, or does it need more evidence?

Ready for final consensus pending the missing Claude review and the remaining procedural steps (write new final consensus superseding Goal2073; run focused v2.0 release-prep test slice). No additional core performance evidence appears required. Minor reporting improvement recommended: explicitly separate warmup vs steady-state medians in future perf artifacts (not blocking).

---

Recommendation: proceed to obtain the missing Claude review, update the final consensus artifact (superseding Goal2073), run the focused test slice, then perform the explicit release action if the 3-AI consensus remains intact.

Supporting artifacts cited: docs/reports/goal2088_v2_0_release_prep_after_streaming_witness_2026-05-15.md; docs/reports/goal2085_v2_perf_table_after_streaming_witness_update_2026-05-15.md and .json; docs/reports/goal2081_streaming_witness_page_adapter_2026-05-15.md; docs/reports/goal2083_streaming_witness_page_pod_evidence_2026-05-15.md; docs/reports/goal2086_streaming_witness_page_extended_scale_pod_2026-05-15.md; docs/reviews/goal2082*, goal2084*, goal2087*, goal2090* (Gemini reviews).

End of supplemental Copilot review.
