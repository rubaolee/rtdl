# Goal 14: Exact-Scale Section 5.6 Readiness

Goal 14 isolates one question from the broader Goal 13 paper-reproduction effort:

- can RTDL repeat RayJoin Section 5.6 at the **same nominal data sizes**
- on the current Mac
- with the current Embree-first architecture

This is a readiness and estimation goal, not a completion claim for the exact-scale run.

## Scope

- focus only on Figure 13 / Figure 14 style Section 5.6 experiments
- use the RayJoin paper sizes:
  - fixed `R = 5,000,000`
  - varying `S = 1,000,000 .. 5,000,000`
- estimate runtime and feasibility on the current Mac
- explain how CPU-vs-GPU-RT comparison would need to be measured later

## Deliverables

- a reproducible estimation report
- explicit runtime estimates for exact-scale `lsi` and `pip`
- explicit memory/feasibility analysis for the current RTDL implementation
- explicit statement of whether an overnight run is currently trustworthy
- 2-agent consensus that the report is technically honest enough to guide the next step

## Acceptance Criteria

- the report uses the accepted current Section 5.6 analogue as its calibration basis
- the report clearly distinguishes query-only estimates from total end-to-end feasibility
- the report explicitly states whether the exact-scale run is currently practical
- the report explicitly states what would be required to compare CPU and GPU RT performance
- Codex and Gemini agree on the report conclusion
