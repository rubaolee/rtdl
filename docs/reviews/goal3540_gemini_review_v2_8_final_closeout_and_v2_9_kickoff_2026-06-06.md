# Goal3540 Gemini Review: v2.8 Final Closeout and v2.9 Kickoff

Date: 2026-06-06

## Reviewed Documents

- `docs/reports/goal3537_v2_8_final_internal_closeout_after_10s_evidence_2026-06-06.md`
- `docs/reports/goal3538_v2_9_performance_first_kickoff_plan_2026-06-06.md`
- `docs/reports/goal3536_v2_8_vs_v2_3_10s_steady_state_a5000_2026-06-06.md`
- `docs/reports/goal3522_v2_8_internal_closeout_3ai_consensus_2026-06-05.md`

## Review Questions

### 1. Does Goal3537 correctly close v2.8 internally after the stricter Goal3536 10s evidence?

Yes. Goal3537 acts as a supplementary internal closeout, directly incorporating the findings and stricter evidence from Goal3536. It explicitly states that "v2.8 is internally closed as an architecture, prepared-execution, measurement, documentation, and claim-discipline foundation" and clarifies that v2.8 is not a broad performance leap, starting v2.9 from the Goal3536 performance diagnosis.

### 2. Does it avoid overclaiming v2.8 as a broad performance leap?

Yes. Goal3537 clearly avoids overclaiming v2.8 performance. It explicitly states that v2.8 is "not positioned as a broad performance leap over v2.3" and "not a public speedup release." It also corrects the previous over-amplified RayDB grouped sum claim based on the more robust 10-second measurements from Goal3536, acknowledging that the stricter evidence provides a "more honest" performance story.

### 3. Is Goal3538 the right v2.9 performance-first plan?

Yes. Goal3538 is well-aligned as the v2.9 performance-first plan. Its stated goal of making benchmark apps faster in a measurable, repeatable, app-agnostic, and honest way directly addresses the conclusions from Goal3537 and Goal3536. It directly builds upon the identified weak rows and the need for comprehensive 10-second harness coverage.

### 4. Are the P0 priorities correct: Barnes-Hut, spatial RayJoin, and full 10s coverage?

Yes. The P0 priorities in Goal3538 (Barnes-Hut node coverage, spatial RayJoin promoted contracts, and achieving full 10s harness coverage) are correct. These directly correspond to the "Carry-Forward Weak Rows" and the need for enhanced measurement rigor identified in Goal3537 and Goal3536. Addressing these weak spots and ensuring robust measurement is a critical first step for a performance-first release.

### 5. Does the plan preserve the app-agnostic engine boundary and explicit partner-choice rule?

Yes. Both Goal3537 and Goal3538 explicitly preserve the app-agnostic engine boundary and the explicit partner-choice rule. Goal3537 emphasizes that the repository "must continue to preserve the same app-agnostic engine and claim-boundary discipline," and Goal3538's "Engineering Rules" forbid "App-specific native-engine code" and mandate that "Users choose partners explicitly; the runtime must not silently choose PyTorch, CuPy, Numba, or Triton."

### 6. What must change before v2.9 implementation starts?

Before broader v2.9 implementation, the immediate and critical change is to complete the 10s harness coverage for the five partial rows identified in Goal3536 (Hausdorff X-HD threshold, spatial RayJoin prepared full route, robot collision prepared device buffers, Barnes-Hut node coverage, and LibRTS AABB index). This involves adding app-level repeat hooks or resident loops as specified in Goal3538's Workstream 1. Following this, the A5000 10s steady-state table should be rerun with no silent partial rows, as per Goal3538's initial goal sequence (V2.9-G1 and V2.9-G2).

## Verdict

`accept`

The v2.8 internal closeout is thorough and appropriately cautious regarding performance claims, while the v2.9 kickoff plan is well-reasoned, directly addresses the identified weaknesses, and maintains critical architectural principles. The proposed next steps for v2.9 are logical and necessary.