# Goal2206 RayJoin Same-Query Artifact Importer 2-AI Consensus

Date: 2026-05-17

Status: accepted as post-pod artifact import tooling with boundary; no real
Goal2198 pod artifacts imported yet.

## Scope

This consensus covers the Goal2204 importer:

- `scripts/goal2204_rayjoin_same_query_artifact_import.py`
- `docs/reports/goal2204_rayjoin_same_query_artifact_importer_2026-05-17.md`
- `tests/goal2204_rayjoin_same_query_artifact_importer_test.py`

The importer is designed to run after Goal2198 completes on an RTX pod and
after the resulting artifact directory has been copied back to the development
machine.

## Inputs

Codex implemented the importer, tests, and documentation.

Gemini independently reviewed the importer in:

- `docs/reviews/goal2205_gemini_review_goal2204_rayjoin_artifact_importer_2026-05-17.md`

Gemini verdict:

- `accept-with-boundary`

## Consensus

Codex and Gemini agree that Goal2204 is suitable for importing completed
Goal2198 pod artifacts into `docs/reports/`.

The importer is accepted because it:

- reuses Goal2201 parsing/validation;
- fails closed on missing required RayJoin logs and RTDL same-stream artifacts;
- fails closed on mismatched RTDL stream provenance;
- fails closed on failed RTDL backend parity;
- fails closed on premature public claim flags;
- copies compact raw logs/results into a repo evidence directory;
- regenerates `evidence_summary.regenerated.json` and
  `evidence_report.regenerated.md` from imported raw artifacts;
- hashes full RayJoin query streams for provenance by default;
- does not copy full query streams unless `--include-streams` is explicitly
  supplied.

## Gemini Observation

Gemini noted that `_git_commit()` returns `unknown` if Git metadata is
unavailable. That is acceptable for this importer because the post-pod evidence
still contains runner environment/progress artifacts and stream hashes, and a
missing Git commit is visible rather than silently converted into a claim.

No pre-pod code fix was required by the review.

## Boundary

Goal2204/Goal2206 is tooling only. It does not authorize:

- RayJoin paper reproduction;
- RTDL beating RayJoin;
- broad RT-core acceleration;
- v2.0 release readiness.

Those stronger claims require imported real pod artifacts, a measurement
report, and the appropriate external review/consensus.

## Verdict

Goal2204/Goal2206 verdict:

- `accept-with-boundary`

Next required input:

- an RTX pod to execute Goal2198 and generate real same-query RayJoin/RTDL
  artifacts.
