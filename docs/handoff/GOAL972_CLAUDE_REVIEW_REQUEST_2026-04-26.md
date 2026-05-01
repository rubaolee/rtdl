# Goal972 Claude Review Request

Please review the bounded event-hotspot baseline repair and write a verdict to:

```text
docs/reports/goal972_claude_review_2026-04-26.md
```

Scope:

- Read `docs/reports/goal972_event_hotspot_baseline_repair_2026-04-26.md`.
- Read the repaired artifact:
  - `docs/reports/goal835_baseline_event_hotspot_screening_prepared_count_summary_embree_summary_path_2026-04-23.json`
- Cross-check with:
  - `scripts/goal859_spatial_summary_baseline.py`
  - `scripts/goal836_rtx_baseline_readiness_gate.py`
  - `docs/reports/goal971_post_goal969_baseline_speedup_review_package_2026-04-26.json`

Review questions:

1. Is the event-hotspot Embree baseline now at the required Goal835 scale (`copies=20000`, `iterations=3`)?
2. Does the artifact preserve correctness parity, phase separation, and `authorizes_public_speedup_claim=false`?
3. Is it correct to leave optional SciPy baselines missing when SciPy is not installed locally?
4. Does Goal971 remain conservative after regeneration (`public_speedup_claim_authorized_count=0`)?

Return `ACCEPT` or `BLOCK`, with concrete blockers if any.
