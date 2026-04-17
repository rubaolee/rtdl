# Goal 14: Section 5.6 Five-Minute Local Profiles

Goal 14 isolates one question from the broader Goal 13 paper-reproduction effort:

- what Section 5.6 profile sizes let `lsi` and `pip` each finish in about **five minutes**
- on the current Mac
- with the current Embree-first architecture

This is a scaled local-execution and estimation goal, not a completion claim for the exact-scale run.

## Scope

- focus only on Figure 13 / Figure 14 style Section 5.6 experiments
- keep the paper's two-distribution, five-point experiment shape
- derive separate `lsi` and `pip` size profiles that fit a five-minute local budget
- retain exact-scale estimation as context, not as the operational run target
- explain how CPU-vs-GPU-RT comparison would need to be measured later

## Deliverables

- a reproducible estimation report
- explicit runtime estimates for exact-scale `lsi` and `pip` as context
- explicit recommended five-minute local profiles for `lsi` and `pip`
- explicit memory/feasibility analysis for the current RTDL implementation
- explicit statement that the accepted next step is the scaled local run, not the exact-scale run
- 2-agent consensus that the report is technically honest enough to guide the next step

## Acceptance Criteria

- the report uses the accepted current Section 5.6 analogue as its calibration basis
- the report clearly distinguishes query-only estimates from total end-to-end feasibility
- the report explicitly states whether the exact-scale run is currently practical
- the report defines a five-minute local profile for `lsi`
- the report defines a five-minute local profile for `pip`
- the report explicitly states what would be required to compare CPU and GPU RT performance
- Codex and Gemini agree on the report conclusion
