# Goal 13 Spec

Date: 2026-03-31
Author: Codex

Goal 13 is to use RTDL and the current Embree backend to reproduce as much of the RayJoin paper evaluation surface as possible before the NVIDIA phase.

Primary focus:
- `lsi`
- `pip`
- `overlay`

Target outputs:
- Table 3 analogue
- Table 4 analogue
- Figure 13 analogue
- Figure 14 analogue
- Figure 15 analogue

Constraints:
- no NVIDIA/OptiX runtime work in this goal
- Embree only for native execution
- CPU remains the semantic reference
- all acceptance must remain under 2-agent consensus
