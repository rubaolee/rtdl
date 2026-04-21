# Goal669: Cross-Engine Performance Lessons Consensus

Date: 2026-04-20

Status: accepted by Codex, Claude, and Gemini

## Reviewed Artifact

Primary report:

`/Users/rl2025/rtdl_python_only/docs/reports/goal669_cross_engine_performance_optimization_lessons_2026-04-20.md`

External review request:

`/Users/rl2025/rtdl_python_only/docs/handoff/GOAL669_CROSS_ENGINE_PERF_LESSONS_REVIEW_REQUEST_2026-04-20.md`

Reviewer verdicts:

- Codex: ACCEPT
- Claude: ACCEPT
- Gemini: ACCEPT

Reviewer report files:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal669_claude_cross_engine_perf_lessons_review_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal669_gemini_cross_engine_perf_lessons_review_2026-04-20.md`

## Consensus Findings

The three-AI consensus is that the report is technically suitable as an RTDL
optimization playbook for future workload-engine work.

Agreed points:

- The Apple RT visibility-count optimization is accurately summarized.
- The report correctly separates the scalar blocked-ray count contract from
  full emitted-row output.
- The report does not claim a broad Apple RT speedup, an Apple full-row-output
  speedup, or a universal cross-workload speedup.
- Prepared build-side data, prepacked probe-side data, reduced-output
  contracts, and phase-level profiling are valid reusable optimization
  principles.
- The workload guidance is appropriately calibrated: visibility/collision is
  the strongest fit, nearest-neighbor and DB-style workloads are good but need
  careful output contracts, graph workloads are mixed, and spatial overlay is
  partial because exact geometry output can dominate.
- The engine guidance is honest for OptiX, Embree, Vulkan, HIPRT, and Apple RT,
  including the HIPRT-on-NVIDIA/Orochi boundary and Apple MPS RT's lack of the
  same programmable any-hit model as OptiX/Vulkan.

## Review Notes Resolved

Claude suggested adding a worked break-even example for the Apple RT scalar
count case. The report was updated after review to include approximate
break-even repeated-query counts against the measured Embree row-count path:

- dense blocked: about 7 repeated queries
- mixed visibility: about 3 repeated queries
- sparse clear: about 3 repeated queries

The report explicitly bounds that break-even calculation to the tested scalar
count contract and Apple M4 harness.

## Accepted Use

Goal669 is accepted as the reusable RTDL performance-engineering policy for
future workloads:

1. Start from the app's real output contract.
2. Preserve canonical row-output semantics for correctness.
3. Add prepared build-side objects for stable data.
4. Add prepacked probe buffers for repeated probes.
5. Move reductions into native/backend paths when the app only needs a scalar
   or grouped result.
6. Report first-query cost, repeated-query cost, setup cost, output contract,
   correctness method, and actual hardware mechanism.

## Final Verdict

ACCEPT.

No blockers remain for using the Goal669 report as the cross-engine
optimization playbook.
