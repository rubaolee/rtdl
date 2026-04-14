# Goal 352 Reopening Consensus: Graph Evaluation Harness Remediation

Date: 2026-04-13
Consensus Status: Approved

## Context

The `v0.5+v0.6` audit identified a high-severity methodology flaw in the Graph Evaluation Harness (Goal 352). Specifically, the PostgreSQL baseline timings were found to include one-off data ingestion and table preparation costs within every repeat of the timed query call.

## Consensus Items

1.  **Reopen Goal 352**: The harness must be formally remediated to ensure technical honesty in baseline comparisons.
2.  **Separate Setup from Query**: The `graph_eval.py` harness must be refactored to separate `postgresql_setup_seconds` from `postgresql_seconds` (query only). This has been technically implemented.
3.  **Harden Loaders**: The graph loaders in `graph_datasets.py` must be hardened to support explicit vertex counts, addressing the discovery gap for isolated vertices. This has been technically implemented.
4.  **Update Historical Reports**: Goal reports 352, 355, 357, and 359 must be updated to acknowledge the methodology correction and provide honest timing splits.

## Participants

- RTDL Core Collaborator (User)
- Gemini AI Assistant (Audit lead)
