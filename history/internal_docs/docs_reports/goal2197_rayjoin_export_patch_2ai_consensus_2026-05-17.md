# Goal2197 RayJoin Export Patch 2-AI Consensus

Date: 2026-05-17

Status: 2-AI consensus complete for the Goal2195 RayJoin export patch plan.

## Scope

This consensus covers:

- `docs/reports/goal2195_rayjoin_query_exec_export_patch_plan_2026-05-17.md`
- `docs/reports/goal2195_rayjoin_query_exec_export_patch_2026-05-17.diff`
- `tests/goal2195_rayjoin_query_exec_export_patch_plan_test.py`
- `docs/reviews/goal2196_gemini_review_goal2195_rayjoin_export_patch_2026-05-17.md`

## Reviews

| Reviewer | File | Verdict |
| --- | --- | --- |
| Codex | `docs/reports/goal2195_rayjoin_query_exec_export_patch_plan_2026-05-17.md` | `accept-with-boundary` |
| Gemini | `docs/reviews/goal2196_gemini_review_goal2195_rayjoin_export_patch_2026-05-17.md` | `accept` |

## Consensus Finding

Codex and Gemini agree that the patch targets the correct RayJoin phase:
optional export of generated PIP/LSI query streams from `query_exec`.

The patch is accepted as an observational external-checkout patch because it:

- adds a `-query_stream_output` flag,
- exports `rtdl.rayjoin.same_query_stream.v1`,
- uses `producer: rayjoin_query_exec_export_patch`,
- exports unscaled PIP/LSI query coordinates,
- preserves RayJoin-native zero-based query ids,
- does not change RayJoin traversal or refinement algorithms,
- does not change RTDL native engine code.

## Boundary

This consensus does not claim:

- the patch has compiled on the RTX pod,
- RayJoin has emitted a real stream on pod hardware,
- RTDL has consumed a RayJoin-exported stream on pod hardware,
- RTDL beats RayJoin,
- full RayJoin paper reproduction,
- v2.0 release readiness.

## Next Step

Apply `docs/reports/goal2195_rayjoin_query_exec_export_patch_2026-05-17.diff`
to the pinned RayJoin pod checkout, rebuild, export LSI/PIP streams, and feed
those streams to `scripts/goal2192_rayjoin_same_query_stream_runner.py`.

## Verdict

Goal2195 is accepted as ready for pod validation.
