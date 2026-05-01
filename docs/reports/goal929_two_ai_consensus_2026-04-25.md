# Goal929 Two-AI Consensus

Date: 2026-04-25

## Scope

Review the RTX 3090 cloud evidence intake, the graph analytic-summary contract fix, the Jaccard `chunk-copies=20` manifest fix, and the Goal929 report.

Primary report:

`docs/reports/goal929_rtx_3090_cloud_group_results_2026-04-25.md`

Primary rerun artifacts:

- `docs/reports/cloud_2026_04_25/runpod_3090_2026_04_25/goal762_f_graph_artifact_report_rerun.json`
- `docs/reports/cloud_2026_04_25/runpod_3090_2026_04_25/goal762_h_polygon_artifact_report_rerun.json`

## Verdicts

| Reviewer | Verdict | Blockers | Speedup-claim boundary |
|---|---:|---|---|
| Claude | ACCEPT | None for evidence intake | Confirms the report avoids public speedup claims |
| Gemini | ACCEPT | None for evidence intake | Confirms the report avoids public speedup claims |
| Codex | ACCEPT | None for evidence intake; promotion still requires app-by-app baseline review | No speedup claim authorized |

## Consensus

Goal929 is accepted as cloud evidence intake. The session is internally consistent:

- RTX 3090 hardware metadata is present.
- Bootstrap and focused tests passed.
- Group F graph rerun passed with analyzer `status: ok`.
- Group H polygon rerun passed with analyzer `status: ok`.
- The manifest now uses `chunk-copies=20` for `polygon_set_jaccard`, matching the passing RTX artifact.
- The graph cloud contract now matches analytic-summary mode instead of requiring omitted CPU-reference labels.

This consensus does not promote public RTX speedup claims. It authorizes using these artifacts for the next app-by-app readiness and baseline-review work only.

## Non-Blocking Notes

- Claude noted `scripts/goal889_graph_visibility_optix_gate.py` still has `DATE = "2026-04-24"` while the rerun generated on 2026-04-25. Runtime `generated_at` preserves the actual run time, so this is not an intake blocker. Consider replacing fixed date constants in future report scripts with runtime dates.
- Group G manual artifacts remain evidence candidates until analyzer/intake coverage is added.
- Jaccard larger chunks (`50`, `100`) remain diagnostic failures and should not be used for promotion.
