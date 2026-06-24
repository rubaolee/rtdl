# Call For Review: Phoenix V3 Spatial Overlay Active-Count Full-Scale No-Go

Reviewer: Claude or Gemini external AI.

Please critically review this no-go packet and the queue integration:

- No-go packet: `docs/rebuild/v3/phoenix_v3_spatial_overlay_active_count_full_scale_no_go_2026-06-21.json`
- No-go markdown: `docs/rebuild/v3/phoenix_v3_spatial_overlay_active_count_full_scale_no_go_2026-06-21.md`
- Source evidence: `docs/rebuild/v3/evidence/phoenix_v3_spatial_overlay_full_active_count_20260621/full_overlay_repeat1_m3_failclosed.json`
- Queue packet: `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.json`
- Queue markdown: `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`
- Candidate script: `scripts/v3_phoenix_spatial_overlay_active_count_full_scale_candidate.py`
- Candidate test: `tests/v3_phoenix_spatial_overlay_active_count_full_scale_candidate_test.py`

Context:

- Phoenix V3 promotes reusable, evidence-backed language/engine capabilities only.
- This packet is not asking to promote a row. It asks whether the full-scale active-count evidence is correctly classified as no-go and correctly blocks M7/public performance claims.
- The run used full-scale shape-pair active-count evidence: 15,700 left shapes x 7,774 right shapes = 122,051,800 shape pairs.
- It records complete OptiX M3 metadata and a very large Embree/OptiX timed-median ratio: 1262.205676x.
- But correctness fails: OptiX active count 19,277 versus Embree active count 21,228, delta -1,951.
- Repeat floor also fails: repeat=1 for both backends. The evidence is fail-closed, not promotable.
- Queue integration now records this under `spatial_rayjoin_topology_stream_author_gap` as future research, with M7 rows added = 0.

Questions:

1. Is the no-go classification correct despite the 1262.205676x timed-median ratio?
2. Does the count mismatch alone block M7 promotion and all public speedup claims for this active-count route?
3. Does the queue integration honestly prevent misleading claims such as RTDL beats RayJoin, full polygon overlay, RayJoin paper reproduction, true zero-copy, or broad V3-over-V2 speedup?
4. Is the required reopen bar clear enough: stable exact count, full M3 phase table, same-packet author timing/count evidence or external acceptance of a weaker scope?
5. Are any additional blockers or wording changes required before this no-go is used as part of Phoenix V3 release readiness?

Required verdict format:

- `approve-no-go`
- `approve-no-go-with-amendments`
- `block-no-go`

Please be strict. If this no-go packet is incomplete, state the missing evidence clearly.
