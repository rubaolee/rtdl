# Goal1293 External Review Prompt: Goal1292 Pre-Pod Gate

Please review the current RTDL `main` branch before we spend NVIDIA RTX pod
time on Goal1292.

## Files To Inspect

- `docs/reports/goal1292_v1_5_generic_optix_evidence_packet_2026-05-05.md`
- `docs/reports/goal1292_v1_5_generic_optix_evidence_packet_2026-05-05.json`
- `scripts/goal1292_v1_5_generic_optix_evidence_packet.py`
- `scripts/goal1292_v1_5_generic_optix_evidence_runner.py`
- `tests/goal1292_v1_5_generic_optix_evidence_packet_test.py`
- `src/rtdsl/generic_primitives.py`
- `src/rtdsl/generic_prepared_status.py`
- `examples/rtdl_graph_analytics_app.py`
- `/Users/rl2025/refresh.md`

## Project Constraints

- v1.5 active engineering is Embree plus OptiX only.
- Before v2.1, Vulkan, HIPRT, and Apple RT must remain frozen for new
  implementation work.
- NVIDIA RT performance is the priority, but public speedup wording remains
  forbidden until separate reviewed evidence and consensus.
- Goal1292 is intended to be internal evidence plumbing only, not a public
  release gate or public claim.
- The next action, if accepted, is to run the packet commands on an RTX pod and
  copy back `docs/reports/goal1292_v1_5_generic_optix_pod_results/`.

## Review Questions

1. Is Goal1292 safe and useful to run on a pod before further local engineering?
2. Are the packet commands and required artifacts sufficient to diagnose
   correctness, OptiX prepared query timing, and graph wrapper repeat timing?
3. Are the boundaries correct: no public wording, no whole-app speedup claim,
   and no Vulkan/HIPRT/Apple RT work before v2.1?
4. Are there any blocking issues that should be fixed before pod execution?

## Required Output

Return a concise formal review with:

- Verdict: `ACCEPT`, `ACCEPT_WITH_NON_BLOCKING_NOTES`, or `REJECT`.
- Blocking issues, if any, with file/path references.
- Non-blocking notes, if any.
- Final statement on whether this can be included in a 3-AI consensus pre-pod
  gate.
