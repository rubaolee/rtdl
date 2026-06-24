# Goal1263 Three-AI Consensus: v1.1 Polygon-Pair OptiX Candidate

Date: 2026-05-04

Consensus status: `accepted_with_boundaries`
Public wording authorized: `bounded_candidate_wording_only`
Release gate authorized: `False`

Inputs:

- Codex intake: `docs/reports/goal1262_v1_1_patched_full_matrix_intake_2026-05-04.md`
- Codex scale sweep: `docs/reports/goal1263_polygon_pair_scale_sweep_intake_2026-05-04.md`
- Gemini review: `docs/reports/goal1263_gemini_external_review_2026-05-04.md`
- Claude review: `docs/reports/goal1263_claude_external_review_2026-05-04.md`

Gemini and Claude both returned `ACCEPT WITH CHANGES`. The required changes were
applied to the Goal1263 intake report:

- explicitly state that summary parity is the definitive v1.1 correctness gate;
- disclose `candidate_count_matches_expected: false` as an unresolved diagnostic
  boundary;
- track candidate-count reconciliation as v1.2 work;
- prevent DB 100k one-shot timing from being cited without its slower warm-query
  companion.

The Gemini artifact includes CLI retry/error noise before the final verdict, but
the file contains an explicit final `ACCEPT WITH CHANGES` review and concrete
required changes. Claude independently returned `ACCEPT WITH CHANGES` with the
same core boundary.

## Consensus Decision

`polygon_pair_overlap_area_rows` is accepted as the strongest current v1.1
bounded positive OptiX/Embree performance candidate.

Accepted evidence:

- Goal1262: 40k candidate ratio `0.835`, observed pipeline ratio `0.791`,
  parity `true`.
- Goal1263: 80k candidate ratio `0.682`, observed pipeline ratio `0.827`,
  parity `true`.
- Goal1263: 160k candidate ratio `0.707`, observed pipeline ratio `0.815`,
  parity `true`.

Ratios are `OptiX / Embree`; values below `1.0` mean OptiX is faster.

This is not a general v1.1 release gate and does not change the status of the
other v1.1 rows:

- `database_analytics`: execution-unblocked but not public-speedup-ready.
- `graph_analytics`: correctness-ready but total OptiX path remains slower.
- `polygon_set_jaccard`: correctness-ready at chunk `1024` but OptiX remains
  slower.

## Allowed Wording

Allowed wording must stay inside this boundary:

- "RTDL v1.1 shows bounded OptiX acceleration for
  `polygon_pair_overlap_area_rows` on an RTX A5000 at 40k, 80k, and 160k copies."
- "The measured path is RT-assisted LSI/PIP positive candidate discovery plus
  native C++ exact area continuation."
- "At 160k copies, OptiX measured about `1.4x` faster candidate discovery and
  about `1.2x` faster observed pipeline than Embree under the reviewed
  same-contract benchmark."
- "Correctness is confirmed by summary parity under the current v1.1 profiler
  contract."
- "`candidate_count_matches_expected: false` remains an unresolved diagnostic
  boundary and a tracked v1.2 reconciliation item."

## Blocked Wording

Do not use:

- "monolithic GPU polygon overlay";
- "GPU polygon overlay acceleration";
- "whole-app polygon overlap speedup";
- "broad GIS acceleration";
- "OptiX is faster for RTDL";
- "OptiX speeds up database, graph, or Jaccard workloads in v1.1";
- "polygon-pair correctness is fully proven" without the summary-parity and
  candidate-diagnostic boundary;
- DB speedup wording that cites the 100k one-shot ratio without also citing the
  slower 100k warm-query ratio.

## Follow-Up

No additional pod rerun is required before using the bounded wording above.

Required follow-up before stronger wording:

- reconcile candidate-count diagnostics for polygon candidate discovery;
- reduce host-side prepare/pack overhead for graph/Jaccard/DB paths;
- keep v1.2 focused on NVIDIA OptiX performance;
- keep v1.5 focused on generic traversal-plus-reduction primitives, not
  app-specific engines.
