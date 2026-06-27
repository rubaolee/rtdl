# Source-Tree Doctor

Status: Phoenix V3 capability-branch development sanity check, not a release certificate.

The source-tree doctor checks that this checkout matches the current Phoenix V3
capability/quality branch marker and that the basic learner path is wired. It
does not certify release readiness, public performance wording, or broad
V3-over-V2 speedup.

It is not a benchmark and must not be used as performance evidence.

The previous released-doc version has been moved to the audit quarantine:

`docs/history/quarantine_v3_v4_reset_2026-06-20/docs__learn__source_tree_doctor.md`

Development sanity command:

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py --json
```

Use the result only as one input to the Phoenix V3 capability-branch gate:

- [V3 Rebuild Control](../rebuild/v3/README.md)
- [Phoenix V3 Capability Branch Status](../rebuild/v3/phoenix_v3_phase_h_capability_branch_status_2026-06-24.md)
- [Phase A Performance-Source Consensus](../reviews/codex_claude_antigravity_phoenix_v3_phase_a_performance_source_consensus_2026-06-24.md)
- [Current Claim Boundaries](current_claim_boundaries.md)
