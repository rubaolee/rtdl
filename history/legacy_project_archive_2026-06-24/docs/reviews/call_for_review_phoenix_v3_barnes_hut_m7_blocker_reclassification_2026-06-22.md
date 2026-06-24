# Call For Review: Phoenix V3 Barnes-Hut M7 Blocker Reclassification

Date: 2026-06-22

Please critically review whether the M7 Barnes-Hut blocker intake supports this
planning decision:

```text
Reclassify Barnes-Hut from active severe-regression target to focused-fix-covered
pending full-suite validation, and redirect next engineering/POD resources to
remaining LibRTS/Spatial/RTNN blockers.
```

Review files:

- `docs/rebuild/v3/phoenix_v3_barnes_hut_blocker_intake_m7_2026-06-22.json`
- `docs/reports/phoenix_v3_barnes_hut_blocker_intake_m7_2026-06-22.md`
- `scripts/v3_phoenix_barnes_hut_blocker_intake.py`
- `tests/v3_phoenix_barnes_hut_blocker_intake_test.py`
- `docs/handoff/PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md`

Known evidence:

- Frozen serious all-app Barnes-Hut app geomean: `0.8441965065233041x`.
- Focused same-RT-hardware generic fixed-radius OptiX symbol/cache evidence
  replaces six Barnes-Hut rows for planning only.
- Projected Barnes-Hut app geomean after that focused fix:
  `1.008971208978369x`.
- Productized runner versus existing fused Barnes-Hut control:
  `0.999328063165968x`; failed checks are empty and claim flags are false.
- This packet does not authorize V3 release, public speedup wording, broad
  V3-over-V2 wording, or another all-app POD run.

Please return one verdict label:

- `accept_m7_reclassification_not_release`
- `accept_with_required_edits_not_release`
- `reject_continue_barnes_hut_work`
- `blocked_need_more_evidence`

Questions:

1. Is the reclassification valid as a planning/resource decision?
2. Are the non-authorization boundaries explicit enough?
3. Is replacing Barnes-Hut frozen rows with focused rows for projection only
   acceptable, or is it misleading?
4. Is redirecting next work away from Barnes-Hut toward remaining LibRTS,
   Spatial/RayJoin, or RTNN blockers justified?
5. What exact edits, if any, are required before this can be recorded as
   2-AI consensus?
