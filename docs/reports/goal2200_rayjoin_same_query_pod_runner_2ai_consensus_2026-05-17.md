# Goal2200 RayJoin Same-Query Pod Runner 2-AI Consensus

Date: 2026-05-17

Status: accepted as a pod runbook with boundary; no pod evidence yet.

## Scope

This consensus covers the Goal2198 runner and runbook:

- `scripts/goal2198_rayjoin_same_query_pod_runner.sh`
- `docs/reports/goal2198_rayjoin_same_query_pod_runbook_2026-05-17.md`
- `tests/goal2198_rayjoin_same_query_pod_runner_test.py`

It also depends on the already accepted Goal2195 external RayJoin export patch
and the Goal2192 RTDL same-query stream consumer.

## Inputs

Codex prepared the runner and local validation.

Gemini independently reviewed the runner in:

- `docs/reviews/goal2199_gemini_review_goal2198_rayjoin_same_query_pod_runner_2026-05-17.md`

Gemini verdict:

- `accept-with-boundary`

## Consensus

Codex and Gemini agree that Goal2198 is ready to use on the next RTX pod as a
bounded same-query validation procedure.

The runner is accepted because it:

- clones RTDL from Git and RayJoin at commit
  `02bf6220d6d20b04af77ee20364eced75cc029c9`;
- applies RayJoin build-compatibility fixes only inside the external RayJoin
  checkout;
- applies the Goal2195 `-query_stream_output` patch only inside the external
  RayJoin checkout;
- builds RayJoin plus RTDL Embree/OptiX;
- runs RayJoin `grid`, `lbvh`, and `rt` generated PIP/LSI queries;
- feeds RayJoin-exported PIP/LSI streams into the Goal2192 RTDL same-query
  consumer;
- writes progress logs, per-step logs, stream artifacts, RTDL artifacts, and
  summary metadata;
- keeps public claim flags false.

## Gemini Follow-Up Closed

Gemini identified one concrete pre-pod risk: the runner installed
`cupy-cuda12x` without explicitly checking that the selected CUDA toolchain was
CUDA 12.x.

Codex addressed this before consensus by adding:

- `detect_cuda_major`
- `require_cuda12_for_cupy_package`
- `ALLOW_NON_CUDA12=0` fail-closed default

The runner now exits before installing/running if `nvcc --version` is not CUDA
12.x, unless `ALLOW_NON_CUDA12=1` is set for manual debugging.

## Boundary

This is not RayJoin performance evidence yet.

It does not authorize:

- a paper-scale RayJoin reproduction claim;
- an RTDL-beats-RayJoin claim;
- a broad RT-core acceleration claim;
- a v2.0 release claim.

Those claims require executing the runner on an RTX pod, importing the produced
artifacts, writing an evidence report, and obtaining the appropriate external
review/consensus for the resulting measurements.

## Verdict

Goal2198/Goal2200 verdict:

- `accept-with-boundary`

Next required input:

- an RTX pod for the scripted same-query run.
