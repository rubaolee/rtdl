# Call For Review: Phoenix V3 M8 Remaining Blocker Queue

Date: 2026-06-22

Please critically review the M8 remaining-blocker queue and next-target
selection.

Review files:

- `docs/rebuild/v3/phoenix_v3_m8_remaining_blocker_queue_2026-06-22.json`
- `docs/reports/phoenix_v3_m8_remaining_blocker_queue_2026-06-22.md`
- `scripts/v3_phoenix_remaining_blocker_queue.py`
- `tests/v3_phoenix_remaining_blocker_queue_test.py`
- `docs/reviews/codex_erdos_phoenix_v3_barnes_hut_m7_blocker_reclassification_2ai_consensus_2026-06-22.md`
- `docs/reports/phoenix_v3_librts_aabb_count_cache_focused_evidence_2026-06-22.md`

Current recommendation:

```text
next target: spatial_rayjoin_lsi_optix_topology_stream
initial action: non-POD local intake of Spatial/RayJoin LSI OptiX route mechanics
POD authorized now: false
release/public/broad claims authorized: false
```

Key facts:

- Barnes-Hut is focused-fix-covered pending full-suite validation by 2-AI
  consensus.
- LibRTS Embree AABB is focused-fix-covered pending full-suite validation;
  repeat=9 focused result is `1.923x`.
- LibRTS OptiX AABB is a watch item: frozen row was near parity, but repeat=9
  focused rerun was `0.913x`.
- Planning projection after covered fixes remains far below release bar:
  Set-A geomean `1.039066x`, Set-A app wins `1/5`.
- Largest uncovered Set-A row loss is Spatial/RayJoin LSI OptiX at `0.888121x`.
- RTNN clustered Embree is next at `0.945682x`, but RTNN symbol-cache work has
  already shown no material release-performance gain.

Please return one verdict label:

- `accept_m8_spatial_next_not_pod`
- `accept_with_required_edits_not_pod`
- `reject_choose_rtnn_or_librts_first`
- `blocked_need_more_evidence`

Questions:

1. Is the blocker queue fair and evidence-backed?
2. Is the Spatial/RayJoin LSI OptiX next-target choice justified?
3. Are the non-authorization boundaries explicit enough?
4. Are any required edits needed before this becomes 2-AI consensus?
