# Goal2203 RayJoin Same-Query Postprocessor 2-AI Consensus

Date: 2026-05-17

Status: accepted as post-run evidence tooling with boundary; no pod evidence
yet.

## Scope

This consensus covers the Goal2201 postprocessor:

- `scripts/goal2201_rayjoin_same_query_evidence_report.py`
- `docs/reports/goal2201_rayjoin_same_query_evidence_postprocessor_2026-05-17.md`
- `tests/goal2201_rayjoin_same_query_evidence_postprocessor_test.py`

It also covers the Goal2198 runner wiring that invokes Goal2201 after the raw
pod summary is written.

## Inputs

Codex prepared the postprocessor, tests, and runner wiring.

Gemini independently reviewed the work in:

- `docs/reviews/goal2202_gemini_review_goal2201_rayjoin_same_query_postprocessor_2026-05-17.md`

Gemini verdict:

- `accept-with-boundary`

## Consensus

Codex and Gemini agree that Goal2201 is suitable for the next RTX pod as an
offline postprocessor for Goal2198 artifacts.

The postprocessor is accepted because it:

- reads a Goal2198 artifact directory without needing live pod access;
- parses RayJoin PIP/LSI `grid`, `lbvh`, and `rt` logs;
- records RayJoin query timing, build-index timing, adaptive-grouping timing,
  OptiX launch count, LSI intersection count, and PIP built-in check status;
- reads RTDL same-stream replay artifacts for CPU, Embree, and OptiX;
- verifies the RTDL stream producer is `rayjoin_query_exec_export_patch`;
- verifies `same_contract_with_rayjoin_query_exec` is true;
- verifies RTDL backend parity against the declared reference backend;
- fails closed if stronger public claim flags are true;
- writes `evidence_summary.json` and `evidence_report.md`.

## Gemini Follow-Up Closed

Gemini identified one concrete robustness issue: missing RTDL artifacts should
produce a specific required-artifact error instead of relying on a generic file
read exception.

Codex addressed this before consensus by adding explicit required-file checks
for both RayJoin logs and RTDL same-stream artifacts:

- missing RayJoin logs now report `missing required RayJoin log`;
- missing RTDL artifacts now report `missing required RTDL same-stream artifact`.

The test suite includes a missing-artifact failure case.

## Boundary

Goal2201/Goal2203 is tooling only. It does not authorize:

- RayJoin paper reproduction;
- RTDL beating RayJoin;
- broad RT-core acceleration;
- v2.0 release readiness.

Those claims require actual Goal2198 RTX pod artifacts, a measurement report,
and the appropriate external review/consensus.

## Verdict

Goal2201/Goal2203 verdict:

- `accept-with-boundary`

Next required input:

- an RTX pod to execute Goal2198 and generate real artifacts for Goal2201 to
  summarize.
