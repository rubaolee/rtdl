# Goal1132 Two-AI Consensus

Date: 2026-04-29

## Goal

Add app-level phase timing to the Hausdorff OptiX threshold-decision path and
Embree directed-summary path while keeping public RTX speedup blocked because
the current large-scale dry-run uses an analytic tiled oracle.

## Codex Verdict

ACCEPT.

The OptiX `directed_threshold_prepared` app path now records input
construction, prepared threshold-query, Python postprocess, and validation
phases. The directed threshold helper still uses scalar
`count_threshold_reached` and does not materialize rows. The Embree
directed-summary path now records native directed-summary timing.

This is a measurement-readiness improvement only. The Hausdorff public speedup
claim remains blocked until there is a meaningful same-semantics baseline
contract and reviewed real RTX evidence.

## External AI Verdict

Claude: ACCEPT.

Saved at:

- `docs/reports/goal1132_claude_review_2026-04-29.md`

Claude confirmed:

- app-level phase timing is correct;
- scalar threshold avoids row materialization;
- public Hausdorff speedup remains correctly blocked.

Claude also noted a non-blocking before-cloud follow-up: the older Goal887
profiler schema still names required phases such as `point_pack_sec` and
`optix_close_sec`, while the app-level Goal1132 fields use
`input_construction_sec` and do not expose close timing. This should be
reconciled before treating Goal887 schema checks as a cloud compliance gate.

## Closure

2-AI consensus requirement is satisfied by Codex + Claude.

Goal1132 is closed as a bounded local phase-readiness goal, not as a public
speedup promotion.
